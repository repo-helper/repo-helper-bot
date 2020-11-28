#!/usr/bin/env python3
#
#  updater.py
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#
# stdlib
import sys
from datetime import datetime
from subprocess import Popen
from tempfile import TemporaryDirectory
from textwrap import indent, wrap
from typing import Dict, Iterator, Optional

# 3rd party
import dulwich.porcelain
import github3
import github3.repos.repo
from domdf_python_tools.paths import in_directory
from dulwich.errors import CommitError
from github3 import apps
from github3.apps import Installation
from github3.exceptions import NotFoundError
from repo_helper.cli.utils import commit_changed_files
from repo_helper.core import RepoHelper
from southwark.repo import Repo

# this package
from repo_helper_bot.constants import GITHUBAPP_ID, GITHUBAPP_KEY, client
# TODO: don't be triggered by merging own PR, or at the least clone, check commit message and skip
from repo_helper_bot.db import Repository, db

__all__ = ["iter_installed_repos", "run_update", "update_repository"]


def iter_installed_repos() -> Iterator[Dict]:
	"""
	Returns an iterator over all repositories repo-helper is installed for.
	"""

	installation: Installation
	for installation in client.app_installations(GITHUBAPP_ID):
		# print(installation)
		# print(installation.account)
		username = installation.account["login"]

		# Log in as installation for this user
		installation_id = client.app_installation_for_user(username).id
		client.login_as_app_installation(GITHUBAPP_KEY, GITHUBAPP_ID, installation_id)

		# Get repositories for this user.
		user_repositories = client.session.get(
				installation.repositories_url,
				headers={
						**installation.session.headers,
						"Accept": "application/vnd.github.machine-man-preview+json"
						}
				).json()["repositories"]

		yield from user_repositories


def update_repository(repository: Dict, recreate: bool = False):
	# TODO: rebase
	# TODO: if branch already exists and PR has been merged, abort

	db_repository: Optional[Repository] = Repository.query.get(repository["id"])
	if db_repository is None:
		db_repository = Repository(
				id=repository["id"],
				owner=repository["owner"]["login"],
				name=repository["name"],
				last_pr=datetime.fromtimestamp(100),
				pull_requests="[]",
				)
		db.session.add(db_repository)
	else:
		# Update name of existing repo
		db_repository.owner = repository["owner"]["login"]
		db_repository.name = repository["name"]

	db.session.commit()

	if db_repository.last_pr.day == datetime.now():
		print(f"A PR for {db_repository.fullname} has already been created today. Skipping.")
		return 1

	owner = repository["owner"]["login"]
	repository_name = repository["name"]
	branch_name = "repo-helper-update"

	# Log in as the app
	client.login_as_app(GITHUBAPP_KEY, GITHUBAPP_ID)

	# Log in as installation
	installation_id = client.app_installation_for_repository(
			owner=owner,
			repository=repository_name,
			).id
	client.login_as_app_installation(
			GITHUBAPP_KEY,
			GITHUBAPP_ID,
			installation_id,
			)

	github_repo: github3.repos.repo.Repository = client.repository(owner, repository_name)

	# Ensure 'repo_helper.yml' exists
	try:
		github_repo.file_contents("repo_helper.yml")
	except NotFoundError:
		print(f"repo_helper.yml not found in the repository {repository['owner']['login']}/{repository['name']}")
		return 1

	with TemporaryDirectory() as tmpdir:

		# Clone to tmpdir
		process = Popen(["git", "clone", repository["html_url"], tmpdir])
		process.communicate()
		process.wait()

		repo = Repo(tmpdir)

		if recreate:
			# Delete any existing branch and create again from master
			process = Popen(["git", "branch", "--delete", f"{branch_name}"])
			process.communicate()
			process.wait()

			# Switch to new branch
			dulwich.porcelain.update_head(repo, b"HEAD", new_branch=branch_name.encode("UTF-8"))
			repo.refs[f"refs/heads/{branch_name}".encode("UTF-8")] = repo.refs[b'refs/heads/master']

		elif f"refs/remotes/origin/{branch_name}".encode("UTF-8") in dict(repo.refs):
			with in_directory(tmpdir):
				process = Popen(["git", "checkout", "--track", f"origin/{branch_name}"])
				process.communicate()
				ret = process.wait()
				if ret:
					return ret

		else:
			# Switch to new branch
			dulwich.porcelain.update_head(repo, b"HEAD", new_branch=branch_name.encode("UTF-8"))
			repo.refs[f"refs/heads/{branch_name}".encode("UTF-8")] = repo.refs[b'refs/heads/master']

		# Update files
		try:
			rh = RepoHelper(tmpdir)
		except FileNotFoundError as e:
			error_block = indent(str(e), '\t')
			print(f"Unable to run 'repo_helper'.\nThe error was:\n{error_block}")

		managed_files = rh.run()

		try:
			if not commit_changed_files(
					repo_path=rh.target_repo,
					managed_files=managed_files,
					commit=True,
					message=b"Updated files with 'repo_helper'.",
					enable_pre_commit=False,
					):
				sys.stdout.flush()
				sys.stderr.flush()
				print("Failure!")
				return 1

			sys.stdout.flush()
			sys.stderr.flush()

		except CommitError as e:
			indented_error = '\n'.join(f"\t{line}" for line in wrap(str(e)))
			print(f"Unable to commit changes. The error was:\n\n{indented_error}")
			print("Failure!")
			# TODO: if "recreate", close the pull request.
			return 1

		headers = apps.create_jwt_headers(GITHUBAPP_KEY, GITHUBAPP_ID, expire_in=30)
		url = github_repo._build_url("app", "installations", str(installation_id), "access_tokens")
		with github_repo.session.no_auth():
			response = github_repo.session.post(url, headers=headers)
			json_response = github_repo._json(response, 201)

			installation_access_token = json_response["token"]

		# Push
		dulwich.porcelain.push(
				repo,
				repository["html_url"],
				branch_name.encode("UTF-8"),
				username="x-access-token",
				password=installation_access_token,
				force=recreate,
				)

		sys.stdout.flush()
		sys.stderr.flush()

		# Create PR
		base = github_repo.default_branch
		head = f"{owner}:{branch_name}"

		if not list(github_repo.pull_requests(base=base, head=head)):
			# TODO: body

			created_pr = github_repo.create_pull(
					title="[repo-helper] Configuration Update",
					base=base,
					head=head,
					)

			if created_pr is not None:
				db_repository.add_pr(int(created_pr.number))

		db_repository.last_pr = datetime.now()
		db.session.commit()

		print("Success!")
		return 0


def run_update():
	ret = 0

	for repository in iter_installed_repos():
		ret |= update_repository(repository)
		return

	return ret

#!/usr/bin/env python3
#
#  updater.py
"""
Auto update configuration files on push.
"""
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
from typing import Dict, Iterator, Optional, Tuple, Union

# 3rd party
import click
import dulwich.porcelain
import dulwich.repo
import sqlalchemy.exc
from domdf_python_tools.paths import in_directory
from domdf_python_tools.typing import PathLike
from dulwich.errors import CommitError
from github3 import apps
from github3.exceptions import NotFoundError
from github3.pulls import ShortPullRequest
from github3.repos import Repository as GitHubRepository
from github3_utils.apps import iter_installed_repos
from repo_helper.cli.utils import commit_changed_files  # nodep
from repo_helper.core import RepoHelper  # nodep
from repo_helper.utils import stage_changes  # nodep
from southwark import open_repo_closing
from southwark.repo import Repo

# this package
from repo_helper_bot.constants import BRANCH_NAME, GITHUBAPP_ID, GITHUBAPP_KEY, client, context_switcher
from repo_helper_bot.db import Repository, db
from repo_helper_bot.utils import make_pr_details

__all__ = ["run_update", "update_repository"]


def update_repository(repository: Dict, recreate: bool = False) -> int:
	"""
	Run the updater for the given repository.

	:param repository:
	:param recreate:
	"""

	# TODO: rebase
	# TODO: if branch already exists and PR has been merged, abort

	db_repository: Repository = get_db_repository(
			repo_id=repository["id"],
			owner=repository["owner"]["login"],
			name=repository["name"],
			)

	last_pr_date = datetime.fromtimestamp(db_repository.last_pr or 200)
	now = datetime.now()
	if not recreate and last_pr_date.day == now.day and last_pr_date.month == now.month:
		print(f"A PR for {db_repository.fullname} has already been created today. Skipping.")
		return 1

	owner = repository["owner"]["login"]
	repository_name = repository["name"]

	# Log in as the app
	context_switcher.login_as_app()

	# Log in as installation
	installation_id = context_switcher.login_as_repo_installation(owner=owner, repository=repository_name)

	github_repo: GitHubRepository = client.repository(owner, repository_name)

	# Ensure 'repo_helper.yml' exists
	try:
		github_repo.file_contents("repo_helper.yml")
	except NotFoundError:
		print(f"repo_helper.yml not found in the repository {repository['owner']['login']}/{repository['name']}")
		return 1

	with TemporaryDirectory() as tmpdir:

		# Clone to tmpdir
		repo = clone(repository["html_url"], tmpdir)

		if recreate:
			# Delete any existing branch and create again from master
			recreate_branch(repo)
		elif f"refs/remotes/origin/{BRANCH_NAME}".encode() in dict(repo.refs):
			checkout_branch(repo)
		else:
			# Switch to new branch
			create_branch(repo)

		# Update files
		try:
			rh = RepoHelper(tmpdir)
			rh.load_settings()
		except FileNotFoundError as e:
			error_block = indent(str(e), '\t')
			print(f"Unable to run 'repo_helper'.\nThe error was:\n{error_block}")

		managed_files = rh.run()
		staged_files = stage_changes(repo.path, managed_files)

		if not staged_files and recreate:
			# Everything is up to date, close PR.
			close_pr(owner, repository_name)
			return 0

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
			return 1

		# Push
		dulwich.porcelain.push(
				repo,
				repository["html_url"],
				BRANCH_NAME.encode("UTF-8"),
				username="x-access-token",
				password=get_installation_access_token(github_repo, installation_id),
				force=recreate,
				)

		sys.stdout.flush()
		sys.stderr.flush()

		# Create PR
		base = github_repo.default_branch
		head = f"{owner}:{BRANCH_NAME}"

		if not list(github_repo.pull_requests(state="open", base=base, head=head)):
			created_pr = github_repo.create_pull(
					title="[repo-helper] Configuration Update",
					base=base,
					head=head,
					body=make_pr_details(),
					)

			if created_pr is not None:
				db_repository.add_pr(int(created_pr.number))

		db_repository.last_pr = datetime.now().timestamp()
		db.session.commit()

		print("Success!")
		return 0


def run_update() -> Iterator[Tuple[str, int]]:
	"""
	Run the updater.
	"""

	for repository in iter_installed_repos(context_switcher=context_switcher):
		click.echo(repository["full_name"])
		yield repository["full_name"], update_repository(repository)


def close_pr(
		owner: str,
		repository: str,
		message="Looks like everything is already up to date.",
		):
	"""
	Close the bot's current pull requests, and delete the branch.

	:param owner: The owner of the repository.
	:param repository: The repository name.
	:param message: The message to close the pull request with.
	"""

	repo: GitHubRepository = client.repository(owner, repository)
	pull_request: ShortPullRequest

	for pull_request in repo.pull_requests(state="open", head=BRANCH_NAME):
		print(f"Closing PR#{pull_request}")
		pull_request.create_comment(message)
		pull_request.close()
		repo.ref(f"heads/{BRANCH_NAME}").delete()
		break


def recreate_branch(repo: Union[dulwich.repo.Repo, PathLike]):
	"""
	Delete any existing branch and create again from master.

	:param repo:
	"""

	with open_repo_closing(repo) as repo:  # pylint: disable=redefined-argument-from-local
		with in_directory(repo.path):
			process = Popen(["git", "branch", "--delete", f"{BRANCH_NAME}"])
			process.communicate()
			process.wait()
			create_branch(repo)


def checkout_branch(repo: Union[dulwich.repo.Repo, PathLike]) -> int:
	"""
	Checkout an existing branch.

	:param repo:
	"""

	if isinstance(repo, dulwich.repo.Repo):
		directory = repo.path
	else:
		directory = repo

	with in_directory(directory):
		process = Popen(["git", "checkout", "--track", f"origin/{BRANCH_NAME}"])
		process.communicate()
		return process.wait()


def create_branch(repo: Union[dulwich.repo.Repo, PathLike]):
	"""
	Create and checkout a new branch from master.

	:param repo:
	"""

	with open_repo_closing(repo) as repo:  # pylint: disable=redefined-argument-from-local
		dulwich.porcelain.update_head(repo, b"HEAD", new_branch=BRANCH_NAME.encode("UTF-8"))
		repo.refs[f"refs/heads/{BRANCH_NAME}".encode()] = repo.refs[b'refs/heads/master']


def clone(url: str, dest: PathLike) -> Repo:
	"""
	Clones the given URL and returns the :class:`southwark.repo.Repo` object representing it.

	:param url:
	:param dest:
	"""

	process = Popen(["git", "clone", url, dest])
	process.communicate()
	process.wait()

	return Repo(dest)


def get_installation_access_token(github_repo: GitHubRepository, installation_id: int):
	"""
	Returns the installation access token for the given installation.

	:param github_repo:
	:param installation_id:
	"""

	headers = apps.create_jwt_headers(GITHUBAPP_KEY, GITHUBAPP_ID, expire_in=30)
	url = github_repo._build_url("app", "installations", str(installation_id), "access_tokens")
	with github_repo.session.no_auth():
		response = github_repo.session.post(url, headers=headers)
		json_response = github_repo._json(response, 201)

		return json_response["token"]


def get_db_repository(repo_id: int, owner: str, name: str) -> Repository:
	"""
	Returns the entry for the given repository in the database, creating it if necessary.

	:param repo_id:
	:param owner: The owner of the repository.
	:param name: The name of the repository.
	"""

	retry = 0

	while True:
		retry += 1
		try:
			db_repository: Optional[Repository] = Repository.query.get(repo_id)
			if db_repository is None:
				db_repository = Repository(
						id=repo_id,
						owner=owner,
						name=name,
						last_pr=100,
						pull_requests="[]",
						)
				db.session.add(db_repository)
			else:
				# Update name of existing repo
				db_repository.owner = owner
				db_repository.name = name

			db.session.commit()

			return db_repository

		except sqlalchemy.exc.OperationalError:
			if retry >= 10:
				raise
			else:
				pass

#!/usr/bin/env python3
#
#  hooks.py
"""
Functions to handle GitHub webhooks.
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
from typing import Iterable, Set, Union

# 3rd party
from apeye.requests_url import RequestsURL
from github3.issues import Issue
from github3.pulls import PullRequest, ShortPullRequest
from github3.repos import Repository
from github3_utils.check_labels import Label, _python_dev_re, get_checks_for_pr

# this package
from repo_helper_bot.constants import BRANCH_NAME, github_app
from repo_helper_bot.updater import update_repository
from repo_helper_bot.utils import commit_as_bot, log

__all__ = ["assign_issue", "assign_pr", "on_issue_comment", "on_push"]


@github_app.on("push")
def on_push() -> str:
	"""
	Hook to run ``repo-helper`` when a push is made to the repository.
	"""

	owner = github_app.payload["repository"]["owner"]["login"]
	repo = github_app.payload["repository"]["name"]
	pusher = github_app.payload["pusher"]["name"]

	if github_app.payload["after"] == "0000000000000000000000000000000000000000":
		log("Skipping push where after == 0000000000000000000000000000000000000000")
		return ''

	log(f"New push to {owner}/{repo} by {pusher}!")
	log(f"The ref of the push is {github_app.payload['ref']}")

	if github_app.payload["commits"] and github_app.payload["commits"][0]["committer"]["username"] == "web-flow":
		# Merged PR
		log(f"Push is a merge of a PR. Skipping.")
		return ''

	if pusher not in {"repo-helper", "repo-helper[bot]"}:
		with commit_as_bot():
			update_repository(github_app.payload["repository"])

	return ''


empty_pr_close_message = """\
This pull request has been closed because there were no changes from the target branch.

If you're still working on this PR feel free to push another commit and reopen it.

---

I'm a bot. If you think I've done this in error please \
[contact my owner](https://github.com/repo-helper/repo-helper-bot/issues).
"""


@github_app.on("pull_request.synchronize")
def close_empty_pull_requests() -> None:
	owner = github_app.payload["repository"]["owner"]["login"]
	repo_name = github_app.payload["repository"]["name"]
	num = github_app.payload["pull_request"]["number"]
	pr: PullRequest = github_app.installation_client.pull_request(owner, repo_name, num)

	if not RequestsURL(pr.diff_url).get().text:
		issue = pr.issue()

		issue.close()
		issue.create_comment(empty_pr_close_message)


@github_app.on("issue.reopened")
@github_app.on("issue.opened")
def assign_issue() -> None:
	"""
	Hook to assign me to issues.

	.. TODO:: Assign the people set in ``.github/auto_assign.yml``.
	"""

	owner = github_app.payload["repository"]["owner"]["login"]
	repo = github_app.payload["repository"]["name"]
	num = github_app.payload["pull_request"]["number"]

	issue = github_app.installation_client.issue(owner, repo, num)

	log(f"Issue #{num} opened by {issue.user} in {owner}/{repo}!")

	# TODO: parse assignee from repo_helper.yml
	issue.add_assignees(["domdfcoding"])


@github_app.on("pull_request.reopened")
@github_app.on("pull_request.opened")
def assign_pr() -> None:
	"""
	Hook to assign me to pull requests and request my review.

	.. TODO:: Assign the people set in ``.github/auto_assign.yml``.
	"""

	owner = github_app.payload["repository"]["owner"]["login"]
	repo = github_app.payload["repository"]["name"]
	num = github_app.payload["pull_request"]["number"]

	pr: PullRequest = github_app.installation_client.pull_request(owner, repo, num)
	issue: Issue = github_app.installation_client.issue(owner, repo, num)

	log(f"PR #{num} opened by {pr.user} in {owner}/{repo}!")

	# TODO: parse assignee from repo_helper.yml
	issue.add_assignees(["domdfcoding"])

	if not pr.requested_reviewers and pr.user.login != "domdfcoding":
		pr.create_review_requests(["domdfcoding"])


@github_app.on("pull_request.closed")
def cleanup_pr() -> str:
	"""
	Delete the ``repo-helper-update`` branch when the bot's PR is merged.
	"""

	owner = github_app.payload["repository"]["owner"]["login"]
	repo = github_app.payload["repository"]["name"]

	if not github_app.payload["pull_request"].get("merged", False):
		return ''

	if github_app.payload["pull_request"]["user"]["login"].startswith("repo-helper"):
		if github_app.payload["pull_request"]["title"].startswith("[repo-helper]"):
			github_app.installation_client.repository(owner, repo).ref(f"heads/{BRANCH_NAME}").delete()

	elif github_app.payload["pull_request"]["user"]["login"].startswith("pre-commit"):
		if github_app.payload["pull_request"]["title"].startswith("[pre-commit.ci]"):
			repo_obj = github_app.installation_client.repository(owner, repo)
			repo_obj.ref("heads/ pre-commit-ci-update-config").delete()

	return ''


@github_app.on("issue_comment")
def on_issue_comment() -> str:
	"""
	Hook to respond to commands in pull request comments. comment.
	"""

	if github_app.payload["action"] != "created":
		return ''

	issue = github_app.payload["issue"]
	repository = github_app.payload["repository"]
	sender = github_app.payload["sender"]["login"]
	comment = github_app.payload["comment"]

	if sender not in {"repo-helper", "repo-helper[bot]"}:
		log(f"New comment on issue #{issue['number']} of {repository['full_name']} by {sender}")
		# TODO: check issue is a pull request, the PR is from us and its open

		print(comment["body"])

		#: TODO: org members show as "CONTRIBUTOR"
		if comment["author_association"] in {"OWNER", "COLLABORATOR", "CONTRIBUTOR", "MEMBER"}:
			if "@repo-helper recreate" in comment["body"]:

				with commit_as_bot():
					update_repository(github_app.payload["repository"], recreate=True)

	return ''


def label_pr_failures(pull: Union[PullRequest, ShortPullRequest]) -> Set[str]:
	"""
	Labels the given pull request to indicate which checks are failing.

	:param pull:

	:return: The new labels set for the pull request.
	"""

	pr_checks = get_checks_for_pr(pull)

	failure_labels: Set[str] = set()
	success_labels: Set[str] = set()

	def determine_labels(from_: Iterable[str], to: Set[str]) -> None:
		for check in from_:
			if _python_dev_re.match(check):
				continue

			if check in {"Flake8", "docs"}:
				to.add(f"failure: {check.lower()}")
			elif check.startswith("mypy"):
				to.add("failure: mypy")
			elif check.startswith("ubuntu"):
				to.add("failure: Linux")
			elif check.startswith("windows"):
				to.add("failure: Windows")

	determine_labels(pr_checks.failing, failure_labels)
	determine_labels(pr_checks.successful, success_labels)

	issue: Issue = pull.issue()

	current_labels = {label.name for label in issue.labels()}

	for label in success_labels:
		if label in current_labels and label not in failure_labels:
			issue.remove_label(label)

	new_labels = current_labels - success_labels
	new_labels.update(failure_labels)

	if new_labels != current_labels:
		issue.add_labels(*new_labels)

	return new_labels


@github_app.on("check_run.completed")
def on_check_run_completed() -> str:
	"""
	Hook to respond to the completion of check runs.
	"""

	repo_name = github_app.payload["repository"]["full_name"]
	repo: Repository = github_app.installation_client.repository(*repo_name.split('/'))
	head_branch = github_app.payload["check_run"]["check_suite"]["head_branch"]

	print(f"New check status for repository {repo_name}:")

	pr: PullRequest
	for pr in repo.pull_requests(state="open", head=head_branch):
		label_pr_failures(pr)

	return ''


automerge_label = Label(
		name="🤖 automerge",
		color="#87ceeb",
		description="Auto merge is enabled for this pull request.",
		)


@github_app.on("pull_request.auto_merge_enabled")
def pull_request_auto_merge_enabled() -> None:
	owner = github_app.payload["repository"]["owner"]["login"]
	repo_name = github_app.payload["repository"]["name"]
	num = github_app.payload["pull_request"]["number"]

	print(f"auto merge disabled for {owner}/{repo_name}#{num}")

	repo: Repository = github_app.installation_client.repository(owner, repo_name)

	current_repo_labels = {label.name for label in repo.labels()}

	if automerge_label.name not in current_repo_labels:
		print(f"creating {automerge_label.name} label")
		automerge_label.create(repo)

	pr: PullRequest = github_app.installation_client.pull_request(owner, repo_name, num)
	issue: Issue = pr.issue()

	current_pr_labels = {label.name for label in issue.labels()}
	current_pr_labels.add(automerge_label.name)
	issue.add_labels(*current_pr_labels)


@github_app.on("pull_request.auto_merge_disabled")
def pull_request_auto_merge_disabled() -> None:
	owner = github_app.payload["repository"]["owner"]["login"]
	repo_name = github_app.payload["repository"]["name"]
	num = github_app.payload["pull_request"]["number"]

	print(f"auto merge disabled for {owner}/{repo_name}#{num}")

	pr: PullRequest = github_app.installation_client.pull_request(owner, repo_name, num)
	issue: Issue = pr.issue()

	current_pr_labels = {label.name for label in issue.labels()}

	if automerge_label.name in current_pr_labels:
		issue.remove_label(automerge_label.name)

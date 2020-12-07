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

# this package
from repo_helper_bot.constants import BRANCH_NAME, github_app
from repo_helper_bot.updater import update_repository
from repo_helper_bot.utils import commit_as_bot, log

__all__ = ["assign_issue", "assign_pr", "on_issue_comment", "on_push"]


@github_app.on("push")
def on_push():
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

	# TODO: detect pushes that are merged PRs the bot opened
	if pusher not in {"repo-helper", "repo-helper[bot]"}:

		with commit_as_bot():
			update_repository(github_app.payload["repository"])


@github_app.on("issue.reopened")
@github_app.on("issue.opened")
def assign_issue():
	"""
	Hook to assign me to issues.

	.. TODO:: Assign the people set in ``.github/auto_assign.yml``.
	"""

	owner = github_app.payload["repository"]["owner"]["login"]
	repo = github_app.payload["repository"]["name"]
	num = github_app.payload["pull_request"]["number"]

	issue = github_app.installation_client.issue(owner, repo, num)

	log(f"Issue #{num} opened by {issue.user} in {owner}/{repo}!")

	issue.add_assignees(["domdfcoding"])


@github_app.on("pull_request.reopened")
@github_app.on("pull_request.opened")
def assign_pr():
	"""
	Hook to assign me to pull requests and request my review.

	.. TODO:: Assign the people set in ``.github/auto_assign.yml``.
	"""

	owner = github_app.payload["repository"]["owner"]["login"]
	repo = github_app.payload["repository"]["name"]
	num = github_app.payload["pull_request"]["number"]

	pr = github_app.installation_client.pull_request(owner, repo, num)
	issue = github_app.installation_client.issue(owner, repo, num)

	log(f"PR #{num} opened by {pr.user} in {owner}/{repo}!")

	issue.add_assignees(["domdfcoding"])

	if pr.user.login != "domdfcoding":
		pr.create_review_requests(["domdfcoding"])


@github_app.on("pull_request.closed")
def cleanup_pr():
	"""
	Delete the ``repo-helper-update`` branch when the bot's PR is merged.
	"""

	owner = github_app.payload["repository"]["owner"]["login"]
	repo = github_app.payload["repository"]["name"]

	if not github_app.payload["pull_request"].get("merged", False):
		return ''

	github_app.installation_client.repository(owner, repo).ref(f"heads/{BRANCH_NAME}").delete()


@github_app.on("issue_comment")
def on_issue_comment():
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

		if comment["author_association"] in {"OWNER", "COLLABORATOR", "MEMBER"}:
			if "@repo-helper recreate" in comment["body"]:

				with commit_as_bot():
					update_repository(github_app.payload["repository"], recreate=True)

	return ''

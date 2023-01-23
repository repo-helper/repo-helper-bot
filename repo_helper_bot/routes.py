#!/usr/bin/env python3
#
#  routes.py
"""
HTTP routes.
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

# 3rd party
from github3_utils.apps import iter_installed_repos

# this package
from repo_helper_bot.constants import app, context_switcher
from repo_helper_bot.updater import update_repository
from repo_helper_bot.utils import commit_as_bot

__all__ = ["home", "request_run"]


@app.route('/')
def home():
	"""
	Route for the homepage.
	"""

	return "This is repo-helper-bot, running on Heroku.\n"


@app.route("/request/<username>/<repository>/")
def request_run(username: str, repository: str):
	"""
	Route for the homepage.
	"""

	context_switcher.login_as_app()
	full_name = f"{username}/{repository}"

	with commit_as_bot():
		for repository_dict in iter_installed_repos(context_switcher=context_switcher):
			if repository_dict["full_name"] == full_name:
				result = update_repository(repository_dict)
				break
		else:
			return "Repository not found, or repo-helper-bot not installed on it.\n", 404

	if result:
		return f"An error occurred when running for {full_name}.\n", 500
	else:
		return f"Run successful for {full_name}.\n"

#!/usr/bin/env python3
#
#  constants.py
"""
Configuration constants.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import os
from http import HTTPStatus
from typing import TYPE_CHECKING, Optional

# 3rd party
from flask import Flask, redirect, request, url_for
from flask_githubapp import GitHubApp  # type: ignore
from github3 import GitHub
from github3_utils.apps import ContextSwitcher

if TYPE_CHECKING:
	# 3rd party
	from werkzeug.wrappers import Response

app = Flask(__name__)

GITHUBAPP_ID = app.config["GITHUBAPP_ID"] = int(os.environ["GITHUBAPP_ID"])
GITHUBAPP_SECRET = app.config["GITHUBAPP_SECRET"] = os.environ["GITHUBAPP_SECRET"]
GITHUBAPP_KEY: bytes

if "GITHUBAPP_KEY" in os.environ:
	GITHUBAPP_KEY = app.config["GITHUBAPP_KEY"] = os.environ["GITHUBAPP_KEY"].encode("UTF-8")
else:
	with open(os.environ["GITHUBAPP_KEY_PATH"], "rb") as key_file:
		GITHUBAPP_KEY = app.config["GITHUBAPP_KEY"] = key_file.read()

github_app = GitHubApp(app)

client: GitHub = GitHub()

context_switcher = ContextSwitcher(
		client=client,
		private_key_pem=GITHUBAPP_KEY,
		app_id=GITHUBAPP_ID,
		)

if not os.environ.get("RH_BOT_IMPORTCHECK", 0):
	context_switcher.login_as_app()


def https_redirect() -> Optional["Response"]:
	# Based on https://stackoverflow.com/a/59771351
	# By Maximilian Burszley <https://stackoverflow.com/users/8188846/maximilian-burszley>
	# CC BY-SA 4.0

	if not request.endpoint:
		return None

	if request.scheme != "http":
		return None

	return redirect(
			url_for(request.endpoint, _scheme="https", _external=True),
			HTTPStatus.PERMANENT_REDIRECT,
			)


if "ON_HEROKU" in os.environ:
	app.before_request(https_redirect)

BRANCH_NAME = "repo-helper-update"

__all__ = [
		"github_app",
		"app",
		"client",
		"GITHUBAPP_ID",
		"GITHUBAPP_SECRET",
		"GITHUBAPP_KEY",
		"BRANCH_NAME",
		"context_switcher",
		]

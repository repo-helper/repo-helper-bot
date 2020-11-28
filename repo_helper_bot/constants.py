#!/usr/bin/env python3
#
#  constants.py
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
import os

# 3rd party
from flask import Flask
from flask_githubapp import GitHubApp
from github3 import GitHub

app = Flask(__name__)

GITHUBAPP_ID = app.config["GITHUBAPP_ID"] = int(os.environ["GITHUBAPP_ID"])
GITHUBAPP_SECRET = app.config["GITHUBAPP_SECRET"] = os.environ["GITHUBAPP_SECRET"]

if "GITHUBAPP_KEY" in os.environ:
	GITHUBAPP_KEY = app.config["GITHUBAPP_KEY"] = os.environ["GITHUBAPP_KEY"]
else:
	with open(os.environ["GITHUBAPP_KEY_PATH"], "rb") as key_file:
		GITHUBAPP_KEY = app.config["GITHUBAPP_KEY"] = key_file.read()

github_app = GitHubApp(app)

client = GitHub()
client.login_as_app(GITHUBAPP_KEY, GITHUBAPP_ID)

__all__ = [
		"github_app",
		"app",
		"client",
		"GITHUBAPP_ID",
		"GITHUBAPP_SECRET",
		"GITHUBAPP_KEY",
		]

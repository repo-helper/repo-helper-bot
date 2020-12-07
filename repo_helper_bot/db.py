#!/usr/bin/env python3
#
#  db.py
"""
Database connection.
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
import json
import os
from typing import List

# 3rd party
from domdf_python_tools.paths import PathPlus
from flask_sqlalchemy import SQLAlchemy

# this package
from repo_helper_bot.constants import app

__all__ = ["Repository"]

if "DATABASE_URL" in os.environ:
	app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
else:
	app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{PathPlus.cwd()/'repo_helper.sqlite'}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Repository(db.Model):
	"""
	Stores information about a GitHub Repository.
	"""

	id = db.Column(db.INTEGER, primary_key=True)  # noqa: A003
	owner = db.Column(db.String(128))
	name = db.Column(db.String(128))
	last_pr = db.Column(db.FLOAT)
	# pull_requests = db.Column(PreviousPullRequests(256))
	pull_requests = db.Column(db.String(128))

	@property
	def fullname(self) -> str:
		"""
		The full name of the repository (``owner/name``).
		"""

		return f"{self.owner}/{self.name}"

	def __repr__(self):
		return f'<Repository {self.fullname!r}>'

	def add_pr(self, number: int):
		"""
		Add a pull request number to the list of previous PRs for this repository.

		:param number:
		"""

		current_prs = json.loads(self.pull_requests)
		current_prs.insert(0, number)
		self.pull_requests = json.dumps(current_prs[:10])

	def get_prs(self) -> List[int]:
		"""
		Returns a list of previous pull requests for this repository.
		"""

		return json.loads(self.pull_requests)

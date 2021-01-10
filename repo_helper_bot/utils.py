#!/usr/bin/env python3
#
#  utils.py
"""
Utility functions.
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
import os
from contextlib import contextmanager
from datetime import date, datetime
from functools import partial

# 3rd party
from domdf_python_tools.stringlist import StringList

__all__ = ["commit_as_bot", "log", "make_pr_details"]


@contextmanager
def commit_as_bot():
	"""
	Context manager to set the Git committer name and email to that of the bot.
	"""

	_environ = dict(os.environ)  # or os.environ.copy()
	try:
		name = "repo-helper[bot]"
		email = f"74742576+{name}@users.noreply.github.com"

		os.environ["GIT_COMMITTER_NAME"] = name
		os.environ["GIT_COMMITTER_EMAIL"] = email
		os.environ["GIT_AUTHOR_NAME"] = name
		os.environ["GIT_AUTHOR_EMAIL"] = email

		yield

	finally:
		os.environ.clear()
		os.environ.update(_environ)


def log(message: str, type: str = "INFO"):  # noqa: A002  # pylint: disable=redefined-builtin
	"""
	Log a message to the terminal.

	:param message:
	:param type:
	"""

	print(f"[{datetime.now():%Y-%m-%d %H:%M:%S%z}] [{type}] {message}")


#: Under normal circumstances returns :meth:`datetime.date.today`.
TODAY: date = date.today()


def make_pr_details():
	buf = StringList()
	buf.extend([
			"<details>",
			"  <summary>Commands</summary>",
			'',
			"  * `@repo-helper recreate` will recreate the pull request by checking"
			" out the current master branch and running `repo-helper` on that.",
			"</details>",
			])

	buf.blankline(ensure_single=True)

	buf.append("---")
	buf.blankline(ensure_single=True)

	if TODAY.month == 12:
		buf.append(
				" | ".join((
						"[☃️ repo](https://github.com/repo-helper/repo-helper-bot)",
						"[🎅 issues](https://github.com/repo-helper/repo-helper-bot/issues)",
						"[🎁 marketplace](https://github.com/apps/repo-helper)",
						))
				)
	else:
		buf.append(
				" | ".join((
						"[:octocat: repo](https://github.com/repo-helper/repo-helper-bot)",
						"[🙋 issues](https://github.com/repo-helper/repo-helper-bot/issues)",
						"[🏪 marketplace](https://github.com/apps/repo-helper)",
						))
				)

	return str(buf)


# See also https://gist.github.com/pierrejoubert73/902cc94d79424356a8d20be2b382e1ab

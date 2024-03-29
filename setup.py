#!/usr/bin/env python
# This file is managed by 'repo_helper'. Don't edit it directly.

# stdlib
import pathlib
import shutil
import sys

# 3rd party
from setuptools import setup

sys.path.append('.')

extras_require = {}

repo_root = pathlib.Path(__file__).parent

install_requires = []

for line in (repo_root / "requirements.txt").read_text(encoding="UTF-8").split('\n'):
	if line.startswith("git+https://github.com/repo-helper/repo_helper@"):
		install_requires.append("repo-helper")
	else:
		install_requires.append(line)


setup(
		description="I keep your repository configuration up-to-date using 'repo_helper'.",
		extras_require=extras_require,
		install_requires=install_requires,
		name="repo-helper-bot",
		py_modules=[],
		)

shutil.rmtree("repo_helper_bot.egg-info", ignore_errors=True)

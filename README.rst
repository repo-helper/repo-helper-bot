################
repo_helper_bot
################

🐍 🤖

.. start short_desc

**I keep your repository configuration up-to-date using 'repo_helper'.**

.. end short_desc


.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Tests
	  - |actions_linux| |actions_windows| |actions_macos| |codefactor| |pre_commit_ci|
	* - Activity
	  - |commits-latest| |commits-since| |maintained|
	* - Other
	  - |license| |language| |requires| |pre_commit|

.. |actions_linux| image:: https://github.com/domdfcoding/repo_helper_bot/workflows/Linux%20Tests/badge.svg
	:target: https://github.com/domdfcoding/repo_helper_bot/actions?query=workflow%3A%22Linux+Tests%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/domdfcoding/repo_helper_bot/workflows/Windows%20Tests/badge.svg
	:target: https://github.com/domdfcoding/repo_helper_bot/actions?query=workflow%3A%22Windows+Tests%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/domdfcoding/repo_helper_bot/workflows/macOS%20Tests/badge.svg
	:target: https://github.com/domdfcoding/repo_helper_bot/actions?query=workflow%3A%22macOS+Tests%22
	:alt: macOS Test Status

.. |requires| image:: https://requires.io/github/domdfcoding/repo_helper_bot/requirements.svg?branch=master
	:target: https://requires.io/github/domdfcoding/repo_helper_bot/requirements/?branch=master
	:alt: Requirements Status

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/domdfcoding/repo_helper_bot?logo=codefactor
	:target: https://www.codefactor.io/repository/github/domdfcoding/repo_helper_bot
	:alt: CodeFactor Grade

.. |license| image:: https://img.shields.io/github/license/domdfcoding/repo_helper_bot
	:target: https://github.com/domdfcoding/repo_helper_bot/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/domdfcoding/repo_helper_bot
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/domdfcoding/repo_helper_bot/v0.0.0
	:target: https://github.com/domdfcoding/repo_helper_bot/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/domdfcoding/repo_helper_bot
	:target: https://github.com/domdfcoding/repo_helper_bot/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2020
	:alt: Maintenance

.. |pre_commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
	:target: https://github.com/pre-commit/pre-commit
	:alt: pre-commit

.. |pre_commit_ci| image:: https://results.pre-commit.ci/badge/github/domdfcoding/repo_helper_bot/master.svg
	:target: https://results.pre-commit.ci/latest/github/domdfcoding/repo_helper_bot/master
	:alt: pre-commit.ci status

.. end shields

Installation
--------------

.. start installation

``repo_helper_bot`` can be installed from GitHub.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install git+https://github.com/domdfcoding/repo_helper_bot

.. end installation


Deploying to Heroku
---------------------

.. image:: https://www.herokucdn.com/deploy/button.svg
	:target: https://heroku.com/deploy?template=https://github.com/repo-helper/repo-helper-bot
	:alt: Deploy

1. `Create a GitHub App <https://developer.github.com/apps/building-github-apps/creating-a-github-app/>`_
2. Create Heroku project.
3. In the Heroku app's settings, set the following Config Vars:

   * ``GITHUBAPP_ID`` -- The ID of the GitHub App.
   * ``GITHUBAPP_KEY`` -- The private key of the GitHub App.
   * ``GITHUBAPP_SECRET`` -- The webhook secret of the GitHub App.

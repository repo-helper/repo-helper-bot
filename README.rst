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
	  - |actions_linux| |actions_windows| |actions_macos|
	* - Activity
	  - |commits-latest| |commits-since| |maintained|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy|
	* - Other
	  - |license| |language| |requires|

.. |actions_linux| image:: https://github.com/repo-helper/repo-helper-bot/workflows/Linux/badge.svg
	:target: https://github.com/repo-helper/repo-helper-bot/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/repo-helper/repo-helper-bot/workflows/Windows/badge.svg
	:target: https://github.com/repo-helper/repo-helper-bot/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/repo-helper/repo-helper-bot/workflows/macOS/badge.svg
	:target: https://github.com/repo-helper/repo-helper-bot/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status

.. |actions_flake8| image:: https://github.com/repo-helper/repo-helper-bot/workflows/Flake8/badge.svg
	:target: https://github.com/repo-helper/repo-helper-bot/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/repo-helper/repo-helper-bot/workflows/mypy/badge.svg
	:target: https://github.com/repo-helper/repo-helper-bot/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://dependency-dash.repo-helper.uk/github/repo-helper/repo-helper-bot/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/repo-helper/repo-helper-bot/
	:alt: Requirements Status

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/repo-helper/repo-helper-bot?logo=codefactor
	:target: https://www.codefactor.io/repository/github/repo-helper/repo-helper-bot
	:alt: CodeFactor Grade

.. |license| image:: https://img.shields.io/github/license/repo-helper/repo-helper-bot
	:target: https://github.com/repo-helper/repo-helper-bot/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/repo-helper/repo-helper-bot
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/repo-helper/repo-helper-bot/v0.0.0
	:target: https://github.com/repo-helper/repo-helper-bot/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/repo-helper/repo-helper-bot
	:target: https://github.com/repo-helper/repo-helper-bot/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2024
	:alt: Maintenance

.. end shields

Installation
--------------

.. start installation

``repo-helper-bot`` can be installed from GitHub.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install git+https://github.com/repo-helper/repo-helper-bot

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

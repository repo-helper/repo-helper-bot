# 3rd party
from domdf_python_tools.import_tools import discover

# this package
import repo_helper_bot.hooks

discover(repo_helper_bot)

# this package
from repo_helper_bot.constants import app, github_app

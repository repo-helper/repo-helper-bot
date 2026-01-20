# stdlib
import os

# 3rd party
from apeye.requests_url import RequestsURL
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from shippinglabel.requirements import read_requirements

os.system("git stash")

try:

	head_sha = RequestsURL("https://api.github.com/repos/repo-helper/repo_helper/commits/master",
							).get().json()["sha"]

	requirements, comments, invalid = read_requirements("requirements.txt", include_invalid=True)

	sorted_requirements = sorted(requirements)

	buf = StringList(comments)

	for line in invalid:
		if line.startswith("git+https://github.com/repo-helper/repo_helper@"):
			buf.append(f"git+https://github.com/repo-helper/repo_helper@{head_sha}")
		else:
			buf.append(line)

	buf.extend(str(req) for req in sorted_requirements)

	PathPlus("requirements.txt").write_lines(buf)

	os.system("pre-commit")
	os.system("git stage requirements.txt")
	os.system("git commit -m 'Bump repo-helper version'")

finally:
	os.system("git stash pop")

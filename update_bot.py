# stdlib
import os

# 3rd party
from apeye import RequestsURL
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from shippinglabel.requirements import read_requirements

head_sha = RequestsURL("https://api.github.com/repos/domdfcoding/repo_helper/commits/master").get().json()["sha"]

requirements, comments, invalid = read_requirements("requirements.txt", include_invalid=True)
print(requirements, comments, invalid)

sorted_requirements = sorted(requirements)

buf = StringList(comments)

for line in invalid:
	if line.startswith("git+https://github.com/domdfcoding/repo_helper@"):
		buf.append(f"git+https://github.com/domdfcoding/repo_helper@{head_sha}")
	else:
		buf.append(line)

buf.extend(str(req) for req in sorted_requirements)

PathPlus("requirements.txt").write_lines(buf)

os.system("pre-commit")
os.system("git stage requirements.txt")
os.system("git commit -m 'Bump repo-helper version'")

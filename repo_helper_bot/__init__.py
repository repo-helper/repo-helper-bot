#!/usr/bin/env python3
#
#  __init__.py
"""
I keep your repository configuration up-to-date using 'repo_helper'.
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

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.0.0"
__email__: str = "dominic@davis-foster.co.uk"

# TODO: Sign commit
# See https://stackoverflow.com/questions/22968856/what-is-the-file-format-of-a-git-commit-object-data-structure

# Temporary workaround for https://github.com/jelmer/dulwich/issues/1546

# stdlib
from typing import List, Tuple

# 3rd party
import dulwich.protocol


def _extract_capabilities(text: bytes) -> Tuple[bytes, List[bytes]]:
	if b"\0" not in text:
		return text, []
	text, capabilities, *_ = text.rstrip().split(b"\0")
	return (text, capabilities.strip().split(b" "))


dulwich.protocol.extract_capabilities = _extract_capabilities

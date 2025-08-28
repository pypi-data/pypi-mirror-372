"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2022.
All rights reserved.

Tools to access the documentation
"""

import pathlib
import webbrowser

INDEX_HTML_PATH = pathlib.Path(__file__).parent / "html" / "index.html"


def open_documentation(path: pathlib.Path = INDEX_HTML_PATH):
    url = f"file://{path.resolve()}"
    webbrowser.open(url)


if __name__ == "__main__":
    open_documentation()

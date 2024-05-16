from __future__ import annotations

from typing import Sequence
from argparse import ArgumentParser
from subprocess import run as run_in_subprocess

import sys


def main(argv: Sequence[str] | None = None) -> None:
    parser = ArgumentParser()
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)
    if not args.paths:
        sys.exit(0)
    run_in_subprocess(
        [
            "python",
            "-m",
            "libcst.tool",
            "codemod",
            "autotyping.AutotypeCommand",
            *args.paths,
            "--aggressive",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()

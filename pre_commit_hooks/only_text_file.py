from __future__ import annotations

import argparse
import subprocess
from typing import Sequence

from pre_commit_hooks.util import added_files
from pre_commit_hooks.util import filter_lfs_files


def is_text_file(
    filenames: Sequence[str],
    *,
    enforce_all: bool = False,
) -> int:
    # Find all added files that are also in the list of files pre-commit tells
    # us about
    retv = 0
    filenames_filtered = set(filenames)
    filter_lfs_files(filenames_filtered)

    if not enforce_all:
        filenames_filtered &= added_files()

    for filename in filenames_filtered:
        process = subprocess.run(
            [
                'git',
                'grep',
                '-I',
                '--name-only',
                '--untracked',
                '-e',
                '.',
                '--',
                filename,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if process.returncode != 0:
            print(f'{filename} is not a text file.')
            retv = 1
    return retv


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filenames',
        nargs='*',
        help='Filenames pre-commit believes are changed.',
    )
    parser.add_argument(
        '--enforce-all',
        action='store_true',
        help='Enforce all files are checked, not just staged files.',
    )
    args = parser.parse_args(argv)
    return is_text_file(args.filenames, enforce_all=args.enforce_all)


if __name__ == '__main__':
    raise SystemExit(main())

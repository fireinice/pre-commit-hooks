from __future__ import annotations

import subprocess
from typing import Any


class CalledProcessError(RuntimeError):
    pass


def added_files() -> set[str]:
    cmd = ('git', 'diff', '--staged', '--name-only', '--diff-filter=A')
    return set(cmd_output(*cmd).splitlines())


def cmd_output(*cmd: str, retcode: int | None = 0, **kwargs: Any) -> str:
    kwargs.setdefault('stdout', subprocess.PIPE)
    kwargs.setdefault('stderr', subprocess.PIPE)
    proc = subprocess.Popen(cmd, **kwargs)
    stdout, stderr = proc.communicate()
    stdout = stdout.decode()
    if retcode is not None and proc.returncode != retcode:
        raise CalledProcessError(cmd, retcode, proc.returncode, stdout, stderr)
    return stdout


def zsplit(s: str) -> list[str]:
    s = s.strip('\0')
    if s:
        return s.split('\0')
    else:
        return []


def filter_lfs_files(filenames: set[str]) -> None:  # pragma: no cover (lfs)
    """Remove files tracked by git-lfs from the set."""
    if not filenames:
        return

    check_attr = subprocess.run(
        ('git', 'check-attr', 'filter', '-z', '--stdin'),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        encoding='utf-8',
        check=True,
        input='\0'.join(filenames),
    )
    stdout = zsplit(check_attr.stdout)
    for i in range(0, len(stdout), 3):
        filename, filter_tag = stdout[i], stdout[i + 2]
        if filter_tag == 'lfs':
            filenames.remove(filename)

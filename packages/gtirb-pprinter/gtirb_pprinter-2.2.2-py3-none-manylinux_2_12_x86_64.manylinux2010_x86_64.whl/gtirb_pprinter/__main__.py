from gtirb_pprinter import pprinter_path
import subprocess
import sys


def _main():
    with pprinter_path() as tool_path:
        ret = subprocess.run(
            sys.argv, check=False, close_fds=False, executable=tool_path
        )
        sys.exit(ret.returncode)


if __name__ == "__main__":
    _main()

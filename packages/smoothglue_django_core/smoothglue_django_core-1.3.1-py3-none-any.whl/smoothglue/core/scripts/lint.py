import re
import sys

from pylint import run_pylint

from smoothglue.core.scripts.boot_django import boot_django


def _run_pylint():
    boot_django()
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(run_pylint())


if __name__ == "__main__":
    _run_pylint()

import os
import shutil
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from start_here.experiments.constants import (
    LABEL_STUDIO_DATABASE_NAME,
    LABEL_STUDIO_PORT,
    RESULTS_DATABASE_HOST,
    RESULTS_DATABASE_PASSWORD,
    RESULTS_DATABASE_PORT,
    RESULTS_DATABASE_USER,
)


def main() -> None:
    label_studio_bin = shutil.which("label-studio")
    if not label_studio_bin:
        print(
            "ERROR: 'label-studio' not found in PATH.\n"
            "Install it via: pipx install label-studio",
            file=sys.stderr,
        )
        sys.exit(1)

    os.environ["DJANGO_DB"] = "default"
    os.environ["POSTGRE_NAME"] = LABEL_STUDIO_DATABASE_NAME
    os.environ["POSTGRE_USER"] = RESULTS_DATABASE_USER
    os.environ["POSTGRE_PASSWORD"] = RESULTS_DATABASE_PASSWORD
    os.environ["POSTGRE_HOST"] = RESULTS_DATABASE_HOST
    os.environ["POSTGRE_PORT"] = str(RESULTS_DATABASE_PORT)

    print(
        f"Starting Label Studio on port {LABEL_STUDIO_PORT}\n"
        f"  Postgres: {RESULTS_DATABASE_USER}@{RESULTS_DATABASE_HOST}:{RESULTS_DATABASE_PORT}/{LABEL_STUDIO_DATABASE_NAME}\n",
        flush=True,
    )

    os.execvp(
        label_studio_bin,
        [label_studio_bin, "start", "--port", str(LABEL_STUDIO_PORT)],
    )


if __name__ == "__main__":
    main()

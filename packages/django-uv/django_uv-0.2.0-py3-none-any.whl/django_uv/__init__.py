from pathlib import Path
from tomllib import load
from subprocess import call
import os
import sys


def find_pyproject(path=Path.cwd() / "pyproject.toml") -> dict:
    if path.exists:
        with path.open("rb") as fp:
            data = load(fp)

    try:
        settings = data["tool"]["django"]
    except KeyError:
        # No tool section found
        return {}
    else:
        return settings


def main(argv=sys.argv) -> None:
    settings = find_pyproject()
    env = os.environ.copy()
    if "settings" in settings:
        env["DJANGO_SETTINGS_MODULE"] = settings["settings"]
        call(["uv", "run", "django-admin"] + argv[1:], env=env)
    else:
        from django.core.management import ManagementUtility

        utility = ManagementUtility(argv)
        utility.execute()

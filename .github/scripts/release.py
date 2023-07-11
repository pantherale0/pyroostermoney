#!/usr/bin/env python3
import json
import subprocess
import io, re

def get_last_version() -> str:
    """Return the version number of the last release."""
    json_string = (
        subprocess.run(
            ["gh", "release", "view", "--json", "tagName"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        .stdout.decode("utf8")
        .strip()
    )

    return json.loads(json_string)["tagName"]


def bump_patch_number(version_number: str) -> str:
    """Return a copy of `version_number` with the patch number incremented."""
    major, minor, patch = version_number.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def update_file_version(new_version):
    """Updates the VERSION variable in const.py"""
    with open("pyroostermoney/const.py", "r") as file:
        filedata = file.read()

    # replace str
    filedata = re.sub('VERSION=".*?"', f'VERSION="{new_version}"', filedata)

    with open("pyroostermoney/const.py", "w") as file:
        file.write(filedata)

def create_new_patch_release():
    """Create a new patch release on GitHub."""
    try:
        last_version_number = get_last_version()
        new_version_number = bump_patch_number(last_version_number)
    except subprocess.CalledProcessError as err:
        # The project doesn't have any releases yet.
        new_version_number = "0.0.1"
        
    update_file_version(new_version_number)

    subprocess.run(
        ["git", "config", "user.name", "github-actions"]
    )

    subprocess.run(
        ["git", "config", "user.email", "github-actions@github.com"]
    )

    subprocess.run(
        ["git", "add", "pyroostermoney/const.py"]
    )

    subprocess.run(
        ["git", "commit", "-m", "\"(auto) bump version for release\""],
        check=True
    )

    subprocess.run(
        ["git", "push", "-u", "origin", "HEAD"],
        check=True
    )

    subprocess.run(
        ["gh", "release", "create", "--generate-notes", new_version_number],
        check=True,
    )


if __name__ == "__main__":
    create_new_patch_release()
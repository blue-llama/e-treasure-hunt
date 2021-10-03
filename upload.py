#!/usr/bin/env python3

import fnmatch
import json
import os
import re

import requests

from hunt.constants import HINTS_PER_LEVEL

SERVER = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "adminpasswordhere"


CONTENT_TYPES = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
}


def upload_level(level: int, about: str, blurb: str) -> None:
    """
    Upload a level, without creating any of its hints.

    :param level: The level to upload.
    :param about: The file containing the JSON description of the level.
    :param blurb: The file containing the level blurb (shown on the _next_ level).
    """
    with open(about) as f:
        data = json.load(f)

    data["number"] = level

    # It's OK for there to be no blurb, but we report it in case that wasn't what was
    # intended.
    try:
        with open(blurb) as f:
            data["description"] = f.read()
    except FileNotFoundError:
        print(f"No blurb at level {level}")
        data["description"] = ""

    url = f"{SERVER}/api/levels/{level}"
    r = requests.put(url, auth=(USERNAME, PASSWORD), json=data)

    if not r.ok:
        print(f"Error uploading level {level}")
        print(r.text)

    r.raise_for_status()


def upload_hint(level: int, hint: int, image: str) -> None:
    """
    Upload a hint.

    :param level: The level that the hint belongs to.  The level must already exist.
    :param number: The hint number.  Zero-indexed.
    :param image: The file containing the hint.
    """
    root, ext = os.path.splitext(image)
    content_type = CONTENT_TYPES.get(ext.lower())
    if content_type is None:
        raise RuntimeError(f"unrecognized extension: {ext}")

    url = f"{SERVER}/api/levels/{level}/hints/{hint}"
    with open(image, "rb") as f:
        r = requests.put(
            url, auth=(USERNAME, PASSWORD), files={"hint": (image, f, content_type)}
        )

    if not r.ok:
        print(f"Error uploading level {level} hint {hint}")
        print(r.text)

    r.raise_for_status()


def upload_directory(level: int, dir: str) -> None:
    """
    Upload a level from a directory, creating all of its hints.

    :param level: The level to upload.
    :param dir: A directory, containing about.json, blurb.txt, and five images.
    """
    print(f"Uploading level {level}")

    # Create the level.
    upload_level(
        level,
        about=os.path.join(dir, "about.json"),
        blurb=os.path.join(dir, "blurb.txt"),
    )

    # Find the images.
    images = []
    for extension in CONTENT_TYPES:
        regex = re.compile(fnmatch.translate(f"*{extension}"), re.IGNORECASE)
        images.extend(
            [os.path.join(dir, name) for name in os.listdir(dir) if regex.match(name)]
        )

    # Should find exactly the right number - check the file extensions if not.
    if len(images) != HINTS_PER_LEVEL:
        raise RuntimeError(f"Found {len(images)} images in {dir}")

    # Upload them.
    images.sort(key=lambda x: x.lower())
    for hint, image in enumerate(images):
        upload_hint(level, hint, image)

    print(f"Uploaded level {level}")


def main() -> None:
    upload_directory(level=0, dir="/directory/containing/dummy/level")
    upload_directory(level=1, dir="/directory/containing/level/one")
    upload_directory(level=2, dir="/directory/containing/level/two")
    upload_directory(level=3, dir="/directory/containing/level/three")
    upload_directory(level=4, dir="/directory/containing/dummy/level")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import json
import os
from pathlib import Path

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


def upload_level_without_hints(level: int, dir: Path) -> None:
    """
    Upload a level, without creating any of its hints.

    :param level: The level to upload.
    :param dir: A directory containing about.json and (optionally) blurb.txt.
                The blurb, if present, is shown on the _next_ level.
    """
    about = dir / "about.json"
    with open(about, encoding="utf-8") as f:
        data = json.load(f)

    data["number"] = level

    # It's OK for there to be no blurb, but we report it in case that wasn't what was
    # intended.
    blurb = dir / "blurb.txt"
    try:
        with open(blurb, encoding="utf-8") as f:
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


def upload_hint(level: int, hint: int, image: Path) -> None:
    """
    Upload a hint.

    :param level: The level that the hint belongs to.  The level must already exist.
    :param number: The hint number.  Zero-indexed.
    :param image: The file containing the hint.
    """
    suffix = image.suffix
    content_type = CONTENT_TYPES.get(suffix.lower())
    if content_type is None:
        raise RuntimeError(f"unrecognized suffix: {suffix}")

    url = f"{SERVER}/api/levels/{level}/hints/{hint}"
    with open(image, "rb") as f:
        r = requests.put(
            url,
            auth=(USERNAME, PASSWORD),
            files={"hint": (image.name, f, content_type)},
        )

    if not r.ok:
        print(f"Error uploading level {level} hint {hint}")
        print(r.text)

    r.raise_for_status()


def upload_level(level: int, dir: Path) -> None:
    """
    Upload a level from a directory, creating all of its hints.

    :param level: The level to upload.
    :param dir: A directory containing five images, about.json and (optionally)
                blurb.txt.
                The blurb, if present, is shown on the _next_ level.
    """
    print(f"Uploading level {level}")

    # Find the images.
    images = [
        dir / file
        for file in os.listdir(dir)
        if Path(file).suffix.lower() in CONTENT_TYPES
    ]

    # Should find exactly the right number - check the file extensions if not.
    if len(images) != HINTS_PER_LEVEL:
        raise RuntimeError(f"Found {len(images)} images in {dir}")

    # Create the level.
    upload_level_without_hints(level, dir)

    # Upload the hints.
    images.sort(key=lambda x: x.name.lower())
    for hint, image in enumerate(images):
        upload_hint(level, hint, image)

    print(f"Uploaded level {level}")


def main() -> None:
    # Uploads three levels, including the dummy levels 0 and 4.
    upload_level(level=0, dir=Path("/directory/containing/dummy/level"))
    upload_level(level=1, dir=Path("/directory/containing/level/one"))
    upload_level(level=2, dir=Path("/directory/containing/level/two"))
    upload_level(level=3, dir=Path("/directory/containing/level/three"))
    upload_level(level=4, dir=Path("/directory/containing/dummy/level"))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import json
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


def upload_level_without_hints(level: int, path: Path) -> None:
    """
    Upload a level, without creating any of its hints.

    :param level: The level to upload.
    :param path: A directory containing about.json and (optionally) blurb.txt.
                 The blurb, if present, is shown on the _next_ level.
    """
    about = path / "about.json"
    with about.open(encoding="utf-8") as f:
        data = json.load(f)

    data["number"] = level

    # It's OK for there to be no blurb, but we report it in case that wasn't what was
    # intended.
    blurb = path / "blurb.txt"
    try:
        with blurb.open(encoding="utf-8") as f:
            data["description"] = f.read()
    except FileNotFoundError:
        print(f"No blurb at level {level}")
        data["description"] = ""

    url = f"{SERVER}/api/levels/{level}"
    r = requests.put(url, auth=(USERNAME, PASSWORD), json=data, timeout=5)

    if not r.ok:
        print(f"Error uploading level {level}")
        print(r.text)

    r.raise_for_status()


def upload_hint(level: int, hint: int, image: Path) -> None:
    """
    Upload a hint.

    :param level: The level that the hint belongs to.  The level must already exist.
    :param hint: The hint number.  Zero-indexed.
    :param image: The file containing the hint.
    """
    suffix = image.suffix
    content_type = CONTENT_TYPES.get(suffix.lower())
    if content_type is None:
        raise RuntimeError(f"unrecognized suffix: {suffix}")

    url = f"{SERVER}/api/levels/{level}/hint"
    payload = {"number": hint}
    with image.open("rb") as f:
        r = requests.post(
            url,
            auth=(USERNAME, PASSWORD),
            files={  # type: ignore[arg-type]
                "file": (image.name, f, content_type),
                "data": (None, json.dumps(payload), "application/json"),
            },
            timeout=5,
        )

    if not r.ok:
        print(f"Error uploading level {level} hint {hint}")
        print(r.text)

    r.raise_for_status()


def upload_level(level: int, path: Path) -> None:
    """
    Upload a level from a directory, creating all of its hints.

    :param level: The level to upload.
    :param path: A directory containing five images, about.json and (optionally)
                 blurb.txt.
                 The blurb, if present, is shown on the _next_ level.
    """
    print(f"Uploading level {level}")

    # Find the images.
    images = [file for file in path.iterdir() if file.suffix.lower() in CONTENT_TYPES]

    # Should find exactly the right number - check the file extensions if not.
    if len(images) != HINTS_PER_LEVEL:
        raise RuntimeError(f"Found {len(images)} images in {path}")

    # Create the level.
    upload_level_without_hints(level, path)

    # Upload the hints.
    images.sort(key=lambda x: x.name.lower())
    for hint, image in enumerate(images):
        upload_hint(level, hint, image)

    print(f"Uploaded level {level}")


def main() -> None:
    # Uploads three levels, including the dummy levels 0 and 4.
    upload_level(level=0, path=Path("/directory/containing/dummy/level"))
    upload_level(level=1, path=Path("/directory/containing/level/one"))
    upload_level(level=2, path=Path("/directory/containing/level/two"))
    upload_level(level=3, path=Path("/directory/containing/level/three"))
    upload_level(level=4, path=Path("/directory/containing/dummy/level"))


if __name__ == "__main__":
    main()

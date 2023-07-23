#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import requests
from pydantic import BaseModel, HttpUrl

SERVER = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "adminpasswordhere"


class Hint(BaseModel):
    number: int
    image: HttpUrl


class Level(BaseModel):
    number: int
    name: str
    description: str = ""
    latitude: str
    longitude: str
    tolerance: int
    hints: list[Hint] = []


class Page(BaseModel):
    count: int
    next: HttpUrl | None = None
    results: list[Level] = []


def download_level(path: Path, level: Level) -> None:
    print(f"Downloading level {level.number}")
    level_dir = path / str(level.number)
    level_dir.mkdir(parents=True, exist_ok=True)

    about = {
        "name": level.name,
        "latitude": level.latitude,
        "longitude": level.longitude,
        "tolerance": level.tolerance,
    }
    about_json = level_dir / "about.json"
    with about_json.open("w") as f:
        json.dump(about, f, indent=2)

    if level.description:
        blurb_txt = level_dir / "blurb.txt"
        blurb_txt.write_text(level.description)

    for hint in level.hints:
        r = requests.get(hint.image.unicode_string(), stream=True, timeout=5)

        if not r.ok:
            print(f"Error downloading level {level.number} image {hint.number}")
            print(r.text)

        r.raise_for_status()

        assert hint.image.path is not None
        suffix = Path(hint.image.path).suffix
        image_file = level_dir / f"image{hint.number}{suffix}"

        with image_file.open("wb") as f:
            for chunk in r.iter_content():
                f.write(chunk)


def main(path: Path) -> None:
    next_page: HttpUrl | None = HttpUrl(f"{SERVER}/api/levels")

    while next_page is not None:
        r = requests.get(
            next_page.unicode_string(), auth=(USERNAME, PASSWORD), timeout=5
        )

        if not r.ok:
            print("Error downloading levels")
            print(r.text)

        r.raise_for_status()

        page = Page.model_validate_json(r.text)
        for level in page.results:
            download_level(path, level)

        next_page = page.next


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target",
        type=Path,
        default=Path("download"),
        help="Path in which to save levels",
    )
    args = parser.parse_args()

    main(args.target)

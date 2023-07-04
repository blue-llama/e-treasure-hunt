"""Clientside validator for levels

Some of these checks just make sure that the hunt website won't reject the upload
(without having to actually attempt such an upload).

Other checks are for admin-y things like:
- Tolerances that are suspiciously tight
- README.md files (which are supposed to contain a detailed explanation of the
  structure of the level for the GM's use)
  being smaller than blurb.txt files (which are supposed to be a hunter-consumable
  précis of the level answer/concept once they've solved it)

The checking for the names of the images is stricter than the server requires.
The server will consider the images in alphabetical order, so (say) 1-image.jpg,
2-image.jpg, ... is just a valid a scheme as clue.png, hint1.png, etc.
However, this strict checking does serve to remind the admin to make sure that the
level setter has not come up with their own novel image-naming scheme that wouldn't
work once the server considers the images alphabetically.
"""
import argparse
import json
import os
import re
import zipfile
from pathlib import Path
from typing import TextIO

CONTENT_TYPES = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
}


def unzip_all() -> None:
    for filename in os.listdir(ALL_LEVELS_DIR):
        if filename.endswith(".zip"):
            folder_path: Path = ALL_LEVELS_DIR / filename[:-4]
            if not folder_path.exists():
                with zipfile.ZipFile(ALL_LEVELS_DIR / filename) as zip_ref:
                    zip_ref.extractall(folder_path)


def validate_format() -> None:
    count = 0
    for filename in os.listdir(ALL_LEVELS_DIR):
        dir_path = ALL_LEVELS_DIR / filename
        if dir_path.is_dir() and "DUMMY" not in filename:
            count += 1
            if not (dir_path / "about.json").exists():
                print("No json in", filename)
            else:
                # Check json for values
                with (dir_path / "about.json").open() as f:
                    check_json(f, filename)

            if not (dir_path / "readme.md").exists():
                print("No readme in", filename)

            if not (dir_path / "blurb.txt").exists():
                print("No blurb in", filename)

            # Check readme is bigger than blurb
            if (dir_path / "blurb.txt").exists() and (dir_path / "readme.md").exists():
                blurb_size = os.path.getsize(dir_path / "blurb.txt")
                readme_size = os.path.getsize(dir_path / "readme.md")
                if blurb_size > readme_size:
                    print("Blurb is bigger than readme for", filename)

            images = [
                dir_path / file
                for file in os.listdir(dir_path)
                if Path(file).suffix.lower() in CONTENT_TYPES
            ]

            # Should find exactly the right number - check the file extensions if not.
            if len(images) != 5:
                print(f"Found {len(images)} images in {dir_path}")
            else:
                images.sort(key=lambda x: x.name.lower())
                if not images[0].name.startswith("clue"):
                    print("No clue in", filename)

                # Check the images aren't too big or bad things will happen to the
                # upload. We don't want a repeat of the Wawrinka incident.
                for image in images:
                    image_size = os.path.getsize(image)
                    if image_size > 3 * 1000 * 1000:  # ~3 MB
                        print(
                            "Image",
                            image,
                            "is too big in",
                            filename,
                            "size = ",
                            f"{image_size:,}",
                        )

                for i in range(1, 5):
                    if not images[i].name.startswith("hint"):
                        print("No hint", i, "in", filename)

    print("Analyzed", count, "levels")


def check_coord(coord: str, coord_name: str, filename: str) -> None:
    lat = float(coord)
    if not lat:
        print("No", coord_name, "for level", filename)
    elif lat == 0.0:
        print("  warning: 0", coord_name, "for level", filename)

    numbers_and_dp_only = re.sub("[^0-9.]", "", coord)
    a, b = numbers_and_dp_only.split(".") if "." in coord else (coord, "")
    if len(b) > 5:
        print("More than 5 dp for", coord_name, "for level", filename, ":", coord)
    if len(a) + len(b) > 7:
        print("More than 7 digits for", coord_name, "for level", filename, ":", coord)


def check_json(f: TextIO, filename: str) -> None:
    json_data = json.load(f)
    if not len(json_data["name"]) > 0:
        print("No name for level", filename)

    check_coord(json_data["latitude"], "lat", filename)
    check_coord(json_data["longitude"], "long", filename)

    tol = int(json_data["tolerance"])
    if not tol:
        print("No tolerance for level", filename)
    elif tol < 1:
        print("0 tolerance for level", filename)
    elif tol < 20:
        print("Too-low-resolution tolerance of", tol, "for level", filename)
    elif tol <= 50:
        print("  warning: Small tolerance of", tol, "for level", filename)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "input_directory",
        help="Path to a directory containing the (possibly zipped) "
        "levels to be examined",
    )
    args = argparser.parse_args()
    ALL_LEVELS_DIR = Path(args.input_directory)
    assert ALL_LEVELS_DIR.exists()
    assert ALL_LEVELS_DIR.is_dir()

    unzip_all()
    validate_format()

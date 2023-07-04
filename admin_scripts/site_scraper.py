"""Web scraper for the hunt website to download unlocked levels

Useful for archiving levels if the previous admin forgot to, and
you don't currently have admin credentials.

If you do have admin credentials, better to download full levels using the
REST API, like this:

`curl -u admin:adminpasswordhere http://localhost:8000/api/levels/1`
"""
import argparse
import json
import sys
import typing
from pathlib import Path

import bs4
import requests


class PageLevelData:
    def __init__(
        self,
        level_num: int,
        previous_level_name: str,
        previous_level_coords: tuple[str, str],
        image_urls: list[str],
    ):
        self.level_num = level_num
        self.previous_level_name = previous_level_name
        self.previous_level_coords = previous_level_coords
        self.image_urls = image_urls
        self.level_name = None
        self.level_coords = None


def print_err(message: str) -> None:
    print(message, file=sys.stderr)


def scrape_level(level_num: int) -> str:
    url = f"https://www.e-treasure-hunt.com/level/{level_num}"
    r = requests.get(url, headers={"cookie": COOKIE})
    if r.ok:
        return r.text
    else:
        print_err("%d: %s" % (r.status_code, r.text))
        return ""


# Disable type-checking for this function as mypy struggles with bs4 usage
@typing.no_type_check
def parse_level_data_from_html(html_text: str, level_num: int) -> PageLevelData:
    soup = bs4.BeautifulSoup(html_text, features="html.parser")

    body = soup.body
    previous_level_name = body.find("div", "heading").h1.contents[0]
    previous_level_coords_h3 = body.find("h3")
    if previous_level_coords_h3:
        previous_level_coords_string = previous_level_coords_h3.contents[0]
        x, y = previous_level_coords_string.split(",")
        previous_level_coords = (x.strip(), y.strip())
    else:
        previous_level_coords = None

    hint_elements = body.find_all("img", "hint")
    img_srcs = [hint_element["src"] for hint_element in hint_elements]
    # print(repr(hint_elements))
    return PageLevelData(
        previous_level_name=previous_level_name,
        previous_level_coords=previous_level_coords,
        image_urls=img_srcs,
        level_num=level_num,
    )


def main(save_dir: str = ".") -> None:
    save_off_directory: Path = Path(save_dir)
    levels = []
    for level_num in range(MIN_LEVEL, MAX_LEVEL + 1):
        html_text = scrape_level(level_num)
        level_data = parse_level_data_from_html(html_text, level_num=level_num)
        levels.append(level_data)

    # Correct off-by-one on name, coords
    for i, level in enumerate(levels):
        if i + 1 < len(levels):
            level.level_name = levels[i + 1].previous_level_name
            level.level_coords = levels[i + 1].previous_level_coords

    # Save off data
    if not save_off_directory.exists():
        save_off_directory.mkdir()

    for level in levels:
        level_directory = save_off_directory / str(level.level_num)
        if not level_directory.exists():
            level_directory.mkdir()

        # N.B. missing tolerance
        x_coord = level.level_coords[0] if level.level_coords is not None else ""
        y_coord = level.level_coords[1] if level.level_coords is not None else ""
        json_data = json.dumps(
            {"name": level.level_name, "latitude": x_coord, "longitude": y_coord},
            indent=2,
        )
        with (level_directory / "about.json").open("w") as f:
            f.write(json_data)

        for i, img_url in enumerate(level.image_urls):
            img_response = requests.get(img_url)
            if img_response.ok:
                file_ext = "img"
                if "Content-Type" in img_response.headers:
                    content_type = img_response.headers["Content-Type"]
                    if content_type == "image/png":
                        file_ext = "png"
                    elif content_type == "image/jpeg":
                        file_ext = "jpeg"
                    else:
                        print_err("Unknown content type: %s" % content_type)
                else:
                    print_err("No content type for %s response!" % img_url)

                img_filename = f"img{i}.{file_ext}"
                with (level_directory / img_filename).open("wb") as f:
                    f.write(img_response.content)
                pass
            else:
                print_err("%d: %s" % (img_response.status_code, img_response.text))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "cookie", help="Site cookie, in format 'csrftoken=<foo>; sessionid=<bar>'"
    )
    argparser.add_argument(
        "save_dir",
        help="Path into a directory into which to save"
        " the levels. Script will create it "
        "if it doesn't exist.",
    )
    argparser.add_argument("minlevel", help="Minimum level number, usually 1")
    argparser.add_argument(
        "maxlevel",
        help="Maximum level number. Script will actually"
        " scrape maxlevel+1 because of the way the"
        " level title and coords are only revealed"
        " on the subsequent page",
    )
    args = argparser.parse_args()
    COOKIE = args.cookie
    MIN_LEVEL = args.minlevel
    MAX_LEVEL = args.maxlevel
    main(save_dir=args.save_dir)

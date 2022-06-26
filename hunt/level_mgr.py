from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, cast
from uuid import uuid4

from hunt.constants import HINTS_PER_LEVEL
from hunt.models import Hint, Level

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile
    from django.http.request import HttpRequest

    class NamedFile(UploadedFile):
        name: str


def upload_new_level(request: HttpRequest) -> str:
    if not request.user.has_perm("hunt.add_level"):
        return "/level-mgmt?success=False"

    if not request.POST:
        return "/level-mgmt?success=False"

    lvl_num = request.POST.get("lvl-num")
    if lvl_num is None:
        return "/level-mgmt?success=False"

    fail_str = "/level-mgmt?success=False&next=" + lvl_num

    # Get the existing level, or create a new one.
    try:
        level = Level.objects.get(number=lvl_num)
    except Level.DoesNotExist:
        level = Level(number=lvl_num)

    def extension(file: NamedFile) -> str:
        """Return normalized filename extension"""
        (_root, extension) = os.path.splitext(file.name)
        return extension.lower()

    # Gather up the needed information.
    uploaded_files: list[UploadedFile] = request.FILES.getlist("files", default=[])
    files = [cast("NamedFile", f) for f in uploaded_files if f.name is not None]
    about_file = next((f for f in files if extension(f) == ".json"), None)
    blurb = next((f for f in files if extension(f) == ".txt"), None)
    images = [f for f in files if extension(f) in (".jpg", ".png")]
    images.sort(key=lambda f: f.name.lower())

    # Level info and images are mandatory, we can manage without a description.
    if about_file is None or len(images) != HINTS_PER_LEVEL:
        return fail_str

    # Read level info, and read or default level description.
    about = json.load(about_file)
    lines = (
        [] if blurb is None else [line.decode("utf-8") for line in blurb.readlines()]
    )
    description = "".join(line for line in lines if line.strip())

    # Update the level.
    level.name = about.get("name")
    level.description = description
    level.latitude = about.get("latitude")
    level.longitude = about.get("longitude")
    level.tolerance = about.get("tolerance")
    level.full_clean()
    level.save()

    # Delete old hints.
    old_hints = level.hints.all()
    for old_hint in old_hints:
        old_hint.image.delete()
    old_hints.delete()

    # Create new hints.
    for number, file in enumerate(images):
        filename = str(uuid4()) + extension(file)
        hint = Hint()
        hint.level = level
        hint.number = number
        hint.image.save(filename, file)

    return f"/level-mgmt?success=True&next={int(lvl_num) + 1}"

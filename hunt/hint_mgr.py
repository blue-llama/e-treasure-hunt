import json
import os
from threading import Thread
from uuid import uuid4

from django.core.files.uploadedfile import UploadedFile
from django.http.request import HttpRequest
from storages.backends.dropbox import DropBoxStorage

from hunt.constants import HINTS_PER_LEVEL
from hunt.models import Hint, Level


def delete_file(fs: DropBoxStorage, name: str) -> None:
    fs.delete(name)


def save_file(fs: DropBoxStorage, file_: UploadedFile, name: str) -> None:
    fs.save(name, file_)


def upload_new_hint(request: HttpRequest) -> str:
    if not request.user.has_perm("hunt.add_level"):
        return "/hint-mgmt?success=False"

    if not request.POST:
        return "/hint-mgmt?success=False"

    lvl_num = request.POST.get("lvl-num")
    if lvl_num is None:
        return "/hint-mgmt?success=False"

    fail_str = "/hint-mgmt?success=False&next=" + lvl_num

    # Get the existing level, or create a new one.
    try:
        level = Level.objects.get(number=lvl_num)
    except Level.DoesNotExist:
        level = Level(number=lvl_num)

    def extension(filename: str) -> str:
        """Return normalized filename extension"""
        (_root, extension) = os.path.splitext(filename)
        return extension.lower()

    # Gather up the needed information.
    lvl_files = request.FILES.getlist("files")
    lvl_info_file = next((f for f in lvl_files if extension(f.name) == ".json"), None)
    lvl_desc_file = next((f for f in lvl_files if extension(f.name) == ".txt"), None)
    lvl_photos = [f for f in lvl_files if extension(f.name) in (".jpg", ".png")]
    lvl_photos.sort(key=lambda x: x.name)

    if (
        (lvl_desc_file is None)
        or (lvl_info_file is None)
        or (len(lvl_photos) != HINTS_PER_LEVEL)
    ):
        return fail_str

    # Update the level.
    lines = [line.decode("utf-8") for line in lvl_desc_file.readlines()]
    lvl_desc = "".join(line for line in lines if line.strip())

    lvl_info = json.load(lvl_info_file)
    level.name = lvl_info.get("name")
    level.description = lvl_desc
    level.latitude = lvl_info.get("latitude")
    level.longitude = lvl_info.get("longitude")
    level.tolerance = lvl_info.get("tolerance")
    level.save()

    fs = DropBoxStorage()
    threads = []

    # Delete old hints.
    old_hints = level.hint_set.all()
    for old_hint in old_hints:
        if fs.exists(old_hint.filename):
            process = Thread(target=delete_file, args=[fs, old_hint.filename])
            process.start()
            threads.append(process)
    old_hints.delete()

    # Create new hints.
    for number, file_ in enumerate(lvl_photos):
        filename = str(uuid4()) + "." + extension(file_.name)
        process = Thread(target=save_file, args=[fs, file_, filename])
        process.start()
        threads.append(process)

        hint = Hint()
        hint.level = level
        hint.number = number
        hint.filename = filename
        hint.save()

    # Wait for all of our Dropbox operations to complete before returning.
    for process in threads:
        process.join()

    return "/hint-mgmt?success=True&next=" + str(int(lvl_num) + 1)

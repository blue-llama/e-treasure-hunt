import ast
import json
from threading import Thread
from uuid import uuid4

from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    SimpleUploadedFile,
    TemporaryUploadedFile,
    UploadedFile,
)
from django.http.request import HttpRequest
from storages.backends.dropbox import DropBoxStorage

from hunt.models import Level


def delete_file(fs: DropBoxStorage, name: str) -> None:
    fs.delete(name)


def save_file(fs: DropBoxStorage, file_: UploadedFile, name: str) -> None:
    fs.save(name, file_)


# Hacky fix for django file upload bug
def clone_uploaded_file(data: UploadedFile) -> UploadedFile:
    if isinstance(data, InMemoryUploadedFile):
        return SimpleUploadedFile(data.name, data.read(), data.content_type)

    if isinstance(data, TemporaryUploadedFile):
        data.file.close_called = True

    return data


def upload_new_hint(request: HttpRequest) -> str:
    if not request.user.has_perm("hunt.add_level"):
        return "/hint-mgmt?success=False"

    if not request.POST:
        return "/hint-mgmt?success=False"

    lvl_num = request.POST.get("lvl-num")
    fail_str = "/hint-mgmt?success=False&next=" + str(int(lvl_num))

    try:
        level = Level.objects.get(number=lvl_num)
    except Level.DoesNotExist:
        level = Level(number=lvl_num)

    lvl_files = request.FILES.getlist("files")
    lvl_files.sort(key=lambda x: x.name)

    lvl_info_file = lvl_files[0]
    lvl_desc_file = lvl_files[1]
    lvl_photos = lvl_files[2:]

    if (
        (lvl_desc_file.name != "blurb.txt")
        or (lvl_info_file.name != "about.json")
        or (len(lvl_photos) != 5)
    ):
        return fail_str

    fs = DropBoxStorage()
    threads = []

    if level.clues:
        old_clues = ast.literal_eval(level.clues)
        for old_clue in old_clues:
            if fs.exists(old_clue):
                process = Thread(target=delete_file, args=[fs, old_clue])
                process.start()
                threads.append(process)

    clue_names = []
    for file_ in lvl_photos:
        extension = file_.name.split(".")[-1]
        print(file_.name)
        if (extension.lower() != "png") and (extension.lower() != "jpg"):
            return fail_str
        clue_name = str(uuid4()) + "." + extension
        clue_names.append(clue_name)

        # Hack - Django keeps closing files. Clone it to keep it open.
        file_clone = clone_uploaded_file(file_)

        process = Thread(target=save_file, args=[fs, file_clone, clue_name])
        process.start()
        threads.append(process)

    lvl_info = json.load(lvl_info_file)

    lvl_desc = ""
    lvl_desc_lines = lvl_desc_file.readlines()
    for line_enc in lvl_desc_lines:
        line = line_enc.decode("cp1251")
        if line.strip():
            lvl_desc = lvl_desc + line

    level.name = lvl_info.get("name")
    level.description = lvl_desc
    level.latitude = lvl_info.get("latitude")
    level.longitude = lvl_info.get("longitude")
    level.tolerance = lvl_info.get("tolerance")
    level.clues = clue_names

    # We now pause execution on the main thread by 'joining' all of our started threads.
    # This ensures that each Dropbox operation completes before we return.
    for process in threads:
        process.join()

    try:
        level.save()
    except Exception:
        return fail_str

    return "/hint-mgmt?success=True&next=" + str(int(lvl_num) + 1)

from hunt.models import (
    HuntInfo,
    Level,
    HintTime,
    AppSetting,
    HuntEvent,
    Answer,
    Location,
)
from storages.backends.dropbox import DropBoxStorage
import json
from uuid import uuid4
import ast
from django.conf import settings
from threading import Thread
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import TemporaryUploadedFile


def delete_file(fs, name):
    fs.delete(name)


def save_file(fs, file, name):
    fs.save(name, file)


# Hacky fix for django file upload bug
def clone_uploaded_file(data):
    if isinstance(data, InMemoryUploadedFile):
        return SimpleUploadedFile(data.name, data.read(), data.content_type)
    elif isinstance(data, TemporaryUploadedFile):
        data.file.close_called = True
    return data


def delete_old_clue_threads(fs, threads, level):
    if level.clues:
        old_clues = ast.literal_eval(level.clues)
        for old_clue in old_clues:
            if fs.exists(old_clue):
                process = Thread(target=delete_file, args=[fs, old_clue])
                process.start()
                threads.append(process)


def create_file_thread(fs, threads, file):

    extension = file.name.split(".")[-1]
    clue_name = str(uuid4()) + "." + extension

    # Hack - Django keeps closing files. Clone it to keep it open.
    file_clone = clone_uploaded_file(file)

    process = Thread(target=save_file, args=[fs, file_clone, clue_name])
    process.start()
    threads.append(process)
    return clue_name


def create_clues_and_hints(level_number, file_dict):
    fs = DropBoxStorage()
    threads = []
    clue_names = []

    clue_names.extend(create_file_thread(fs, threads, file_dict.get("clue")))
    for file in file_dict.get("hints"):
        clue_names.extend(create_file_thread(fs, threads, file))

    # We now pause execution on the main thread by 'joining' all of our started threads.
    # This ensures that each Dropbox operation completes before we return.
    for process in threads:
        process.join()

    return clue_names


def create_level(levelform, file_dict):
    try:
        level = Level.objects.get(number=levelform.number)
        delete_old_clue_threads(fs, threads, level)
    except Level.DoesNotExist:
        level = Level(number=levelform.number)

    clue_names = create_clues_and_hints(request.FILES)
    level.clues = clue_names

    level.save()
    return level


def create_answer(level, answerform_data):
    # Seek to the beginning of the file because the validator may have read the file
    answerform_data.get("info").file.seek(0)
    json_data = json.loads(answerform_data.get("info").file.read())
    description = answerform_data.get("description").file.read()
    location = Location.objects.create(
        latitude=json_data.get("latitude"),
        longitude=json_data.get("longitude"),
        tolerance=json_data.get("tolerance"),
    )
    Answer.objects.create(
        location=location,
        solves_level=level,
        name=answerform_data.get("name"),
        description=description,
    )


# GRT Ugh, this is so annoying because it expects a single description in a single file
def upload_new_hint(request):
    if not request.user.has_perm("hunt.add_level"):
        return "/hint-mgmt?success=False"

    if not request.POST:
        return "/hint-mgmt?success=False"

    lvl_num = request.POST.get("lvl-num")
    fail_str = "/hint-mgmt?success=False&next=" + str(int(lvl_num))

    try:
        create_answers(lvl_info.get("answers"), level)
    except:
        return fail_str

    return "/hint-mgmt?success=True&next=" + str(int(lvl_num) + 1)

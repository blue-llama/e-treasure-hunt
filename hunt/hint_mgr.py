from hunt.models import HuntInfo, Level, AppSetting, HuntEvent
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
     
def upload_new_hint(request):
    if (not request.user.has_perm('hunt.add_level')):
        return '/hint-mgmt?success=False'
    
    if(not request.POST):
        return '/hint-mgmt?success=False'
    
    lvl_num = request.POST.get('lvl-num') 
    fail_str = '/hint-mgmt?success=False&next=' + str(int(lvl_num))
    
    try:
        level = Level.objects.get(number=lvl_num)
    except Level.DoesNotExist:
        level = Level(number=lvl_num)
    
    lvl_files = request.FILES.getlist('files')
    lvl_files.sort(key=lambda x: x.name)
    
    lvl_info_file = lvl_files[0]
    lvl_desc_file = lvl_files[1]
    lvl_photos = lvl_files[2:]
    
    if((lvl_desc_file.name != 'blurb.txt') or (lvl_info_file.name != 'about.json') or (len(lvl_photos) != 5)):
        return fail_str
        
    fs = DropBoxStorage()
    threads = []
    
    if ((level.clues != None) and level.clues):
        old_clues = ast.literal_eval(level.clues)
        for old_clue in old_clues:
            if fs.exists(old_clue):
                process = Thread(target=delete_file, args=[fs, old_clue])
                process.start()
                threads.append(process)
            
    clue_names = []    
    for file in lvl_photos:
        extension =  file.name.split('.')[-1]
        print (file.name)
        if ((extension.lower() != 'png') and (extension.lower() != 'jpg')):
            return fail_str
        clue_name = str(uuid4()) + "." + extension
        clue_names.append(clue_name)
        
        # Hack - Django keeps closing files. Clone it to keep it open.
        file_clone = clone_uploaded_file(file)
        
        process = Thread(target=save_file, args=[fs, file_clone, clue_name])
        process.start()
        threads.append(process)
        
    lvl_info = json.load(lvl_info_file)
    
    lvl_desc = ""
    lvl_desc_lines = lvl_desc_file.readlines()
    for line_enc in lvl_desc_lines:
        line = line_enc.decode("cp1251")
        if (line.strip()):
            lvl_desc = lvl_desc + line
           
    level.name = lvl_info.get('name');
    level.description = lvl_desc;
    level.latitude = lvl_info.get('latitude');
    level.longitude = lvl_info.get('longitude');
    level.tolerance = lvl_info.get('tolerance');
    level.clues = clue_names
    
    # We now pause execution on the main thread by 'joining' all of our started threads.
    # This ensures that each Dropbox operation completes before we return.
    for process in threads:
        process.join()
    
    try:
        level.save()
    except:
        return fail_str
    
    return '/hint-mgmt?success=True&next=' + str(int(lvl_num) + 1)
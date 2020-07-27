#!/usr/bin/env python
import os
import sys
import json
import time
import shutil
import threading
from datetime import datetime
from time import gmtime, strftime
from file_types import FileTypeFactory
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def run():
    for filename in os.listdir(folder_to_track):
        i = 0
        if not os.path.isdir(os.path.join(folder_to_track, filename)):
            extension = str(os.path.splitext(
                folder_to_track + '/' + filename)[1]).strip('.')
            if extension != 'crdownload':
                f = FileTypeFactory.factory(extension)
                path = f.get_path()
                if not os.path.exists(path):
                    os.makedirs(path)
                nname = filename
                while os.path.isfile(os.path.join(path, nname)):
                    i += 1
                    fn = nname.split('.')[0].split('_')[0]
                    nname = fn + '_' + str(i) + '.' + extension
                nfile_path = os.path.join(path, nname)
                src = os.path.join(folder_to_track, filename)
                new_name = os.path.join(nfile_path)
                os.rename(src, new_name)


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        run()


folder_to_track = os.path.join(os.path.expanduser('~'), "Downloads")
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, folder_to_track)
observer.start()

running = True


# Function for implementing the loading animation
def load_animation():
    # String to be displayed when the application is loading
    load_str = "watching downloads folder..."
    ls_len = len(load_str)
    # String for creating the rotating line
    animation = "|/-\\"
    anicount = 0
    # used to keep the track of
    # the duration of animation
    counttime = 0
    # pointer for travelling the loading string
    i = 0
    while running:
        # used to change the animation speed
        # smaller the value, faster will be the animation
        time.sleep(0.075)
        # converting the string to list
        # as string is immutable
        load_str_list = list(load_str)
        # x->obtaining the ASCII code
        x = ord(load_str_list[i])
        # y->for storing altered ASCII code
        y = 0
        # if the character is "." or " ", keep it unaltered
        # switch uppercase to lowercase and vice-versa
        if x != 32 and x != 46:
            if x > 90:
                y = x - 32
            else:
                y = x + 32
            load_str_list[i] = chr(y)
        # for storing the resultant string
        res = ''
        for j in range(ls_len):
            res = res + load_str_list[j]
        # displaying the resultant string
        sys.stdout.write("\r" + res + animation[anicount])
        sys.stdout.flush()
        # Assigning loading string
        # to the resultant string
        load_str = res
        anicount = (anicount + 1) % 4
        i = (i + 1) % ls_len
        counttime = counttime + 1
    print()


if __name__ == '__main__':
    try:
        t_anim = threading.Thread(target=load_animation)
        t_anim.start()
        run()
        while running:
            time.sleep(10)
    except KeyboardInterrupt:
        running = False
        observer.stop()
    observer.join()

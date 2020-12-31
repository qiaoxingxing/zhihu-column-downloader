# encoding=utf-8


import requests
import sys
import os
import re

import time
import threading
from queue import Queue
from threading import Thread
import tools

from column_downloader import download_url
from course import Course
import  datetime

def download(url):
    TRY_COUNT = 10
    try_times = 0
    while True:
        try:
            download_url(url, False)
            break
        except Exception as e:
            try_times += 1
            if try_times>= TRY_COUNT:
                raise e

def download_course(course):
    title = course.title
    url = course.url
    print(title, url)   
    if course.is_done: 
        return     
    try:
        download(url)
        course.is_done = True
        course.save()
    except Exception as e:
        msg = "%s: %s\n" % (datetime.datetime.now(),str(e))
        course.log  = str(course.log) + msg
        course.save()
        print(e)
def get_courses():
    courses = [x for x in Course.select()]
    courses.sort(key=lambda a: 10000*(a.priority if a.priority else 0) + a.price, reverse=True)
    return courses    

def download_all():
    '''
    下载base_dir及子目录下的文件;
    '''
    courses = get_courses()
    for c in courses:
        download_course(c)


queue = Queue()

def download_multi():
    while True:
        course = queue.get()    
        title = course.title
        print('thread: %s, url: %s' % (threading.current_thread(), title))
        download_course(course)
        queue.task_done()
        if queue.empty():
            break


def download_all_multi(thread_count=5):
    courses = get_courses()
    for c in courses:
        if c.is_done:
            continue
        queue.put(c)

    for i in range(thread_count):
        t = Thread(target=download_multi)
        t.daemon = True  # 设置线程daemon  主线程退出，daemon线程也会推出，即时正在运行
        t.start()
    queue.join()





if __name__ == "__main__":
    # download_all()
    download_all_multi()

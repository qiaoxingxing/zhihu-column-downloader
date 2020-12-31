#encoding=utf-8
import os,re

# 递归检查并创建文件夹
def check_or_make_dir(path):
    sep = os.path.sep
    if not os.path.exists(path):
        if path.find(sep) != -1:
            check_or_make_dir(path[0:path.rfind(sep)])
        os.mkdir(path)

def get_valid_filename(filename):
    filename = re.sub('[\?\*\/\\\!:|]', '&', filename)
    filename = filename.replace('\x01','')
    filename = filename.replace('\x02','')
    filename = filename.replace('\x03','')
    filename = filename.replace('\x04','')  
    filename = filename.replace('\x08','')  
    filename = filename.replace("<","【")
    filename = filename.replace(">","】")
    filename = filename.replace("=","等于")
    filename = filename.replace('"',"”")
    filename = filename.strip()
    return filename


# 获取“当前”文件所在目录
def get_dir_path(current_file):
    return os.path.split(os.path.realpath(current_file))[0]


# 获取当前文件所在目录的父目录
def get_parent_dir_path(current_file):
    return os.path.dirname(get_dir_path(current_file))


def join_path(path, *paths):
    return os.path.abspath(os.path.join(path, *paths))


def main_path():
    """当前程序的所在目录

    Returns:
        [type]: [description]
    """    
    main_script_path = sys.argv[0]
    return os.path.abspath(os.path.join(main_script_path, ".."))

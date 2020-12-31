import re
import requests
import os
import sys
import tools

import simplejson
import pdfkit

from requests.adapters import HTTPAdapter



root_path = r".\知乎盐选专栏"
session = None

"""
分析: 知乎专栏是一个course, course下有多个课时(section)
"""


def get_header():
    header_raw = '''
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36
'''
    header = {}
    for line in header_raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        name, value = line.split(":", maxsplit=1)
        header[name.strip()] = value.strip()
    # cookie从文件读取, 便于配置, 避免上传到git
    with open("cookie.txt") as f:
        cookie = f.read()
        header["cookie"] = cookie.strip()

    return header


def get_request_session():
    # if session:
    #     return session
    session = requests.Session()
    session.headers = get_header()
    session.mount('http://', HTTPAdapter(max_retries=10))
    session.mount('https://', HTTPAdapter(max_retries=10))
    return session


def is_login():
    url = "https://www.zhihu.com/api/v4/me"
    session = get_request_session()
    res = session.get(url)
    return ("url_token" in res.text)


def get_courses_data(id):
    if not is_login():
        raise RuntimeError("not login")
    offset = 0
    session = get_request_session()
    datas = []
    while(True):
        url = "https://api.zhihu.com/remix/well/%s/catalog?offset=%s&limit=20&order_by=global_idx" % (
            id, offset)
        print("get courses ", offset)
        response = session.get(url)
        text = response.text
        json = simplejson.loads(text)
        is_end = json["paging"]["is_end"]
        datas.extend(json["data"])
        # is_end = True
        if is_end:
            break
        else:
            offset += 20
    # dataString = simplejson.dumps(datas)
    print("courses count ", len(datas))
    return datas

# 测试代码: 获取所有的专栏课程
def get_all_course():
    if not is_login():
        raise RuntimeError("not login")
    offset = 0
    session = get_request_session()
    root = r"C:\users\qxx\Desktop\zhihu"
    datas = []
    while(True):
        json_file_path = os.path.join(root,str(offset)+".json")
        if os.path.exists(json_file_path):
            continue
        url = "https://api.zhihu.com/market/categories/all?limit=50&dataType=new&study_type=album&sort_type=hottest&offset=%s&level=1&right_type=svip_free%%2Csvip_privileges" % (offset)
        print("get all courses ", offset)
        response = session.get(url)
        text = response.text
        json = simplejson.loads(text)
        is_end = json["paging"]["is_end"]
        data = json["data"]
        datas.extend(data)
        dataString = simplejson.dumps(data, ensure_ascii=False, indent=2)
        with open(json_file_path,"w",encoding="utf8") as f:
            f.write(dataString)
        # is_end = True
        if is_end:
            break
        else:
            offset += 50
    # dataString = simplejson.dumps(datas)
    print("courses count ", len(datas))
    with open(os.path.join(root,"all.json"),"w",encoding="utf8") as f:
        f.write(simplejson.dumps(datas, ensure_ascii=False, indent=2))
    return datas


def parse_courses(courses):
    """处理course_data, 解析需要的数据

    Args:
        courses ([type]): 原始的course信息

    Raises:
        RuntimeError: [description]

    Returns:
        [type]: [description]
    """
    lines = []
    for course in courses:
        # chapter
        chapter_title = course['chapter']['title']
        # course['chapter']['idx']有些从0开始排序, 有些从1开始; serial_number_txt 可能更好一些
        chapter_index = course['chapter']['idx']+1
        chapter_name = "%s. %s" % (chapter_index, chapter_title)

        section_url = course['section_cell']['url']
        # name
        title = course["title"]
        index_global = course['index']['global']
        index_relative = course['index']['relative']
        type = course['section_cell']['type']
        if type == "audio":
            media_ext = "mp3"
            url = course['section_cell']['data']['playlist'][0]['url']
        elif type == "video":
            media_ext = "mp4"
            url = course['section_cell']['data']['playlist']['hd']['url']
        elif type == "article":
            media_ext = ""
            url = ''
            # 处理url
            # https://www.zhihu.com/market/paid_column/1217851259103186944/section/1218177490117570560
            # business_id=1217851259103186944&track_id=1218177490117570560
            match = re.search("business_id=(\d*)&track_id=(\d*)",section_url)
            if match:
                column_id = match.group(1)
                lesson_id = match.group(2)
                section_url = "https://www.zhihu.com/market/paid_column/%s/section/%s" % (column_id,lesson_id)
            else: 
                raise RuntimeError("article 地址匹配错误")
        else:
            raise RuntimeError("不支持的格式")
        name = "%s. %s" % (index_relative, title)
        # 章节url, 对应某一课的地址

        line = {
            "chapter_name": chapter_name,  # 章节目录, 带标号
            "name": name,  # 课时名称
            "section_url": section_url,  # 课时地址
            "media_url": url,  # 视频或音频的url
            "media_ext": "."+media_ext  # 文件后缀,.mp3或.mp4
        }
        lines.append(line)
    # 如果所有的folder都相同, 则设置为空
    chapter_names = set([x['chapter_name'] for x in lines])
    if len(chapter_names) <= 1:
        for line in lines:
            line["chapter_name"] = ""

    return lines


def download_file(url, path):
    """下载给定url的文件

    Args:
        url ([type]): 下载地址
        path ([type]): 文件路径
    """
    # print("download file: ", path, url)
    if os.path.exists(path):
        print("exists path ", path)
        return
    dir = tools.get_dir_path(path)
    tools.check_or_make_dir(dir)
    session = get_request_session()
    response = session.get(url,timeout=10.0)
    with open(path, 'wb') as f:
        f.write(response.content)


def download(id, name):
    """下载专栏课程

    Args:
        id ([type]): 课程id
        name ([type]):课程名称
    """
    if not name:
        name = "课程-"+id
    course_root_path = os.path.join(root_path, name)
    tools.check_or_make_dir(course_root_path)

    # 获取course信息;
    course_json_name = "%s-%s-courses_data.json" % (name, id)
    course_json_path = os.path.join(course_root_path, course_json_name)
    # 保存原始course信息到文件
    if os.path.exists(course_json_path) :
        with open(course_json_path, 'r', encoding="utf8") as f:
            content = f.read()
            courses_data = simplejson.loads(content)
    else:
        courses_data = get_courses_data(id)
        with open(course_json_path, "w", encoding="utf8") as f:
            content = simplejson.dumps(courses_data,ensure_ascii=False, indent=4)
            f.write(content)

    courses = parse_courses(courses_data)

    # 保存处理后的course信息到文件
    course_parsed_json_name = "%s-%s-courses_parsed.json" % (name, id)
    course_parsed_json_path = os.path.join(
        course_root_path, course_parsed_json_name)
    if not os.path.exists(course_parsed_json_path):
        with open(course_parsed_json_path, 'w', encoding="utf8") as f:
            s = simplejson.dumps(courses, ensure_ascii=False, indent=4)
            content = f.write(s)

    index = 0
    for course in courses:
        index += 1
        msg = "%s/%s" % (index, len(courses))
        print(msg)
        folder = course["chapter_name"]
        filename = course["name"]
        media_url = course['media_url']
        section_url = course['section_url']

        folder = tools.get_valid_filename(folder)
        filename = tools.get_valid_filename(filename)

        audio_dir_path = os.path.join(course_root_path, folder)
        # tools.check_or_make_dir(audio_dir_path)
        # 下载音频/视频
        if media_url:
            print("download audio......")
            audio_path = os.path.join(audio_dir_path, filename+course['media_ext'])
            download_file(media_url, audio_path)

        # 下载html
        print("download html......")
        if section_url == "https://www.zhihu.com/app/":
            continue
        html_path = os.path.join(audio_dir_path,
                                 "html", filename+".html")
        download_file(section_url, html_path)
        # 保存pdf
        print("download pdf......")
        pdf_path = os.path.join(audio_dir_path, filename+".pdf")
        if not os.path.exists(pdf_path) :
            with open(html_path, "r", encoding="utf8") as f:
                html_content = f.read()
            html2pdf(html_content,pdf_path)


def html2pdf(html_text, path):
    """html转pdf

    Args:
        html_text ([type]): html代码
        path ([type]): pdf文件路径
    """    
    html_text = html_text.replace('"//', '"http://')
    html_text = html_text.replace('data-src', 'src')
    # 解决图片被中间截断
    html_text = html_text.replace('</head>','''
  <style type="text/css">
    .ManuscriptIntro-root-ighpP {
      overflow-y: visible;
    }
  </style>
</head>
'''
)
    # 删除图片"加载中"的内容
    html_text = re.sub(
        '<span class="processImgLazyload.*?</span>', '', html_text, flags=re.DOTALL)
    try:
        pdfkit.from_string(html_text, path, options={
            "--encoding": "utf8"
        })    
    except OSError as e:
        print("OSError: ",e)
        pass
    except Exception as e:
        print("Exception: ",e)
        pass



def download_url(url, isConfirm=True):
    id = re.split("[\./]", url)[-1]
    name = get_name(url)
    name = tools.get_valid_filename(name)

    print("id: ", id)
    print("name: ", name)
    if not id or not name:
        print("id or name is null")
        return
    if isConfirm:
        input(u"确认后回车继续.............")
    download(id, name)


def get_name(url):
    """获取标题和作者
    """    
    # url = "https://www.zhihu.com/remix/albums/%s" % id
    # 2020-09-12: 还有这种格式的专栏:
    # url = "https://www.zhihu.com/xen/market/remix/paid_column/1266754142275534848"
    # url = "https://www.zhihu.com/xen/market/remix/paid_column/%s" % id

    session = get_request_session()
    res = session.get(url)
    if not res.status_code == 200:
        raise RuntimeError("获取html出错")
    text = res.text
    title = re.search(
        r'<title data-react-helmet="true">(.*?)</title>', text).group(1)
    author = re.search(r'<div class="HeaderInfo-subTitle-q4VSR">(.*?)<', text).group(1)
    author = author.strip()
    # 处理作者名的兼容问题; 这一段代码很扯, 凑合用
    author_names = [author.replace(" 等",""),author.replace("","")]
    for name in author_names:
        name = tools.get_valid_filename(name)
        course_root_path = os.path.join(root_path, "%s--%s" % (title, name))
        if os.path.exists(course_root_path):
            author = name
            break
    else:
        pass
    return "%s--%s" % (title, author)

def download_main():
    '''
    下载的入口
    '''
    arg1 = ""
    if len(sys.argv) >= 2:
        arg1 = sys.argv[1]
    print("arg1: "+arg1)
    url = arg1
    download_url(url,False)


def test_main():
    url = "https://www.zhihu.com/remix/albums/1159856000562819072"
    download_url(url, False)    
    # get_all_course()


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        download_main()
    else:
        test_main()


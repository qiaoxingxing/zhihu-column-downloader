# 说明
仅供学习交流; 个人使用的半成品项目; 

下载登录后能访问的知乎盐选专栏, 支持下载视频、音频、文稿(保存为pdf).


# 使用方法
1. 安装依赖  
```
pip install -r requirements.txt
```
安装`wkhtmltopdf`, 并加入path;

2. 登录  
目前的做法: 浏览器登陆后把cookie粘贴到根目录的`cookie.txt`(如果不存在需要手动创建); cookie其实只复制`z_c0`项即可;

3. 下载:  
默认下载到了当前文件夹下的"知乎盐选专栏"
下载某一个盐选专栏: 
```
python column_downloader.py url
# 比如:
# python column_downloader.py https://www.zhihu.com/remix/albums/123456
```
下载所有:   
```
python all_column_downloader.py
```
会读取course.db中的专栏列表并下载, course.db是sqlite数据库, 可以用[sqlitebrowser](https://sqlitebrowser.org/)打开.




# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup  # 网页解析，获取数据
import re  # 正则表达式，匹配文字
import urllib.request,urllib.error  # 制定url，获取网页数据
import xlwt   # 进行excel操作
import sqlite3  # 进行数据库操作


# 爬取网页
    # 获取网页
    # 解析内容
    # 保存数据


# 主函数
def main():
    # 准备静态数据
    baseurl = "https://movie.douban.com/top250?start="
    datalist = getdate(baseurl)
    savepath = "豆瓣电影top250.xls"
    dbpath = "movie.db"

    # 调用函数，执行相关任务
    # savedata(datalist, savepath)
    savedata2db(datalist, dbpath)


# 创建正则表达式对象，表达式规则:
# 获取影片链接详情的规则
findline = re.compile(r'<a href="(.*?)">')   # compile:生成/创建的意思； 创建正则表达式对象，表达式规则
# 获取影片图片链接详情的规则
findimgsrc = re.compile(r'<img.*src="(.*?)"/>', re.S)  # re.S让换行符也包含在字符串中
# 影片的片名
findtitle = re.compile(r'<span class="title">(.*)</span>')
# 影片评分
findrating = re.compile(r'<span class="rating_num" property="v:average">(.*</span>)')
# 找到评价人数
findjudge = re.compile(r'<span>(\d*)人评价</span>')
# 找概况
findinfo = re.compile(r'<span class="inq">(.*)</span>')
# 找电影相关内容
findabout = re.compile(r'<p class="">(.*?)</p>', re.S)   # re.S让换行符也包含在字符串中


# 爬取网页
def getdate(baseurl):
    datelist = []
    for i in range(0, 10):   # 调用获取页面信息的函数，10次
        url = baseurl + str(i*25)
        html = askURL(url)  # 保存获取到网页源码
        # 逐一解析数据
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("div", class_="item"):   # 查找符合要求的字符串形成列表，（有div标签 且class属性等于“item”)
            # print(item)  # 测试查看电影item信息
            date = []  # 保存一个电影的全部信息
            item = str(item)
            # print(item)
            # break  # 调试用 只打印出一部电影全部信息

            # 获取影片链接
            line = re.findall(findline, item)[0]  # re库通过正则表达式来查找特定的字符串
            # print(line)
            date.append(line)   # 添加链接

            imgsrc = re.findall(findimgsrc, item)
            imgsrc = str(imgsrc)
            imgsrc = re.sub('" width="100', " ", imgsrc)
            imgsrc = imgsrc.replace("['", "")
            imgsrc = imgsrc.replace("']", "")
            date.append(imgsrc)  # 添加图片

            titles = re.findall(findtitle, item)   # 片名可能只有一个中文名，没有英文名
            if len(titles) == 2:
                ctitle = titles[0]
                date .append(ctitle)
                otitle = titles[1].replace("/", "")   # 去掉无关名
                date.append(otitle)
            else:
                date.append(titles[0])
                date.append(" ")    # 没有英文名则留空

            rating = re.findall(findrating, item)[0]
            rating = rating.replace("</span>", "")
            date.append(rating)

            judge = re.findall(findjudge, item)[0]
            judge = judge.replace("</span>", "")
            date.append(judge)

            info = re.findall(findinfo, item)
            if len(info) != 0:
                info = info[0].replace("。", "")
                date.append(info)
            else:
                date.append(" ")

            about = re.findall(findabout, item)
            about = str(about)

            about = re.sub('<br(\s+)?/>(\s+)?', " ", about)  # 去掉<br/>  [\s]表示，只要出现空白就匹配
            about = about.replace("\\n", "")
            about = about.replace("['", "")
            about = about.replace("']", "")
            about = about.replace('["', "")
            about = about.replace('"]', "")
            about = about.replace('      ', "")
            about = about.replace('\\xa0', " ")
            # about = re.sub(" ", " ", about)
            about = re.sub("/", " ", about)   # 去掉/
            date.append(about.strip())   # 去掉前后空格
            datelist.append(date)   # 把一部电影信息存入datalist
    print(datelist)
    # print(len(datelist))

    return datelist


# 得到一个指定url的网页内容
# User-Agent：指定用户代理，告诉访问的服务器我是一个什么样的机器、浏览器，本质上是告诉浏览器我们可以接收什么样水平的文件内容
# 当需要指定多个信息时可以用列表，每个信息列表里用键值对
def askURL(url):
    head = {   # 头部信息用来模拟浏览器访问服务器
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
    }
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):   # 编码问题
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


# 保存数据到excel
def savedata(datalist, savepath):
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建book对象  style_compression=0:压缩
    sheet = book.add_sheet("sheet1", cell_overwrite_ok=True)  # 创建工作表  cell_overwrite_ok=True：设置覆盖
    col = ("电影链接", "电影图片链接", "电影中文名", "电影英文名", "评分", "评价数", "概述", "详情")
    for i in range(0, 8):
        sheet.write(0, i, col[i])
    for n in range(0, 250):
        print("第%d条" % (n+1))
        data = datalist[n]
        for j in range(0, 8):
            sheet.write(n+1, j, data[j])


    book.save(savepath)


# 创建movie250数据库
def init_db(dbpath):
    # 创建数据表
    sql = """
        create table movie250
        (id integer primary key autoincrement,
        info_link text,
        img_link text,
        cname varchar,
        enname varchar,
        score numeric,
        rated numeric,
        instruction text,
        info text
        );

    """
    con = sqlite3.connect(dbpath)  # 创建或打开数据库
    cursor1 = con.cursor()  # 获取游标
    cursor1.execute(sql)  # 执行sql语句
    con.commit()  # 提交sql事务
    con.close()  # 关闭


# 保存数据到已创建的movie250数据库
def savedata2db(datalist, dbpath):
    init_db(dbpath)
    cur = sqlite3.connect(dbpath)
    c = cur.cursor()
    for data in datalist:   # 遍历行数
        for index in range(len(datalist)):   # 遍历列数
            if index == 0 or index == 1 or index == 2 or index == 3 or index == 6 or index == 7:
                data[index] = '"' + data[index] + '"'
            # print(len(data))
            # print(data)
            # break
        sql = """
                insert into movie250(info_link, img_link, cname, enname, score, rated, instruction, info)
                values(%s)""" %",".join(data)   # %",".join(data)代替占位符%s
        print(sql)   # 调试用，方便观察
        c.execute(sql)
        cur.commit()
    c.close()
    cur.close()


if __name__ == '__main__':   # 程序入口，控制程序执行的流程
    main()

    # init_db("movicetest.db")   # 测试创建数据库
    print("爬取完毕")


# ValueError: cannot process flags argument with a compiled pattern: re.S 加在complic()，非findall()上
# TypeError: expected string or bytes-like object : 数据类型不匹配 ，about添加数据类型转换 about=str(about)
# TypeError: 'str' object is not callable: 字面上意思是str不可以被系统调用,正在调用一个不能被调用的变量或对象，具体表现调用函数、变量的方式错误

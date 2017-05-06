# -*- coding: utf-8 -*-
# -*- coding=utf-8 -*-
# -*- coding:utf-8 -*-


__author__ = 'CQC'
import urllib2
import re
import socket
import urllib
import httplib
import thread
import time
# import tool
import os


httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'



#抓取MM
class Spider:
    #页面初始化
    def __init__(self):
        self.siteURL = 'http://mm.taobao.com/json/request_top_list.htm'
        self.tool = Tool()

    #获取索引页面的内容
    def getPage(self,pageIndex):
        url = self.siteURL + "?page=" + str(pageIndex)
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        return response.read().decode('gbk')

    #获取索引界面所有MM的信息，list格式
    def getContents(self,pageIndex):
        page = self.getPage(pageIndex)
        pattern = re.compile('<div class="list-item".*?pic-word.*?<a href="(.*?)".*?<img src="(.*?)".*?<a class="lady-name.*?>(.*?)</a>.*?<strong>(.*?)</strong>.*?<span>(.*?)</span>',re.S)
        items = re.findall(pattern,page)
        contents = []
        for item in items:
            contents.append([item[0],item[1],item[2],item[3],item[4]])
        return contents

    #获取MM个人详情页面
    def getDetailPage(self,infoURL):
        response = urllib2.urlopen(infoURL)
        return response.read().decode('gbk')

    #获取个人文字简介
    def getBrief(self,page):
        pattern = re.compile('<div class="mm-aixiu-content".*?>(.*?)<!--',re.S)
        result = re.search(pattern,page)
        return self.tool.replace(result.group(1))

    #获取页面所有图片
    def getAllImg(self,page):
        pattern = re.compile('<div class="mm-aixiu-content".*?>(.*?)<!--',re.S)
        #个人信息页面所有代码
        content = re.search(pattern,page)
        #从代码中提取图片
        patternImg = re.compile('<img.*?src="(.*?)"',re.S)
        images = re.findall(patternImg,content.group(1))
        return images


    #保存多张写真图片
    def saveImgs(self,images,name):
        number = 1
        print u"发现",name,u"共有",len(images),u"张照片"
        for imageURL in images:
            splitPath = imageURL.split('.')
            fTail = splitPath.pop()
            if len(fTail) > 3:
                fTail = "jpg"
            fileName = name + "/" + str(number) + "." + fTail
            self.saveImg(imageURL,fileName)
            number += 1

    # 保存头像
    def saveIcon(self,iconURL,name):
        splitPath = iconURL.split('.')
        fTail = splitPath.pop()
        fileName = name + "/icon." + fTail
        self.saveImg(iconURL,fileName)

    #保存个人简介
    def saveBrief(self,content,name):
        fileName = name + "/" + name + ".txt"
        f = open(fileName,"w+")
        print u"正在偷偷保存她的个人信息为",fileName
        f.write(content.encode('utf-8'))


    #传入图片地址，文件名，保存单张图片
    def saveImg(self,imageURL,fileName):
         u = urllib.urlopen(imageURL)
         data = u.read()
         f = open(fileName, 'wb')
         f.write(data)
         print u"正在悄悄保存她的一张图片为",fileName
         f.close()

    #创建新目录
    def mkdir(self,path):
        path = path.strip()
        # 判断路径是否存在
        # 存在     True
        # 不存在   False
        isExists=os.path.exists(path)
        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            print u"偷偷新建了名字叫做",path,u'的文件夹'
            # 创建目录操作函数
            os.makedirs(path)
            return True
        else:
            # 如果目录存在则不创建，并提示目录已存在
            print u"名为",path,'的文件夹已经创建成功'
            return False

    #将一页淘宝MM的信息保存起来
    def savePageInfo(self,pageIndex):
        #获取第一页淘宝MM列表
        contents = self.getContents(pageIndex)
        for item in contents:
            #item[0]个人详情URL,item[1]头像URL,item[2]姓名,item[3]年龄,item[4]居住地
            print u"发现一位模特,名字叫",item[2],u"芳龄",item[3],u",她在",item[4]
            print u"正在偷偷地保存",item[2],"的信息"
            print u"又意外地发现她的个人地址是",item[0]
            #个人详情页面的URL
            detailURL = "http:"+item[0]
            #得到个人详情页面代码
            detailPage = self.getDetailPage(detailURL)
            #获取个人简介
            brief = self.getBrief(detailPage)
            #获取所有图片列表
            images = self.getAllImg(detailPage)
            self.mkdir(item[2])
            #保存个人简介
            self.saveBrief(brief,item[2])
            #保存头像
            self.saveIcon("http:"+item[1],item[2])
            #保存图片
            self.saveImgs(images,item[2])

    #传入起止页码，获取MM图片
    def savePagesInfo(self,start,end):
        for i in range(start,end+1):
            print u"正在偷偷寻找第",i,u"个地方，看看MM们在不在"
            self.savePageInfo(i)


#处理页面标签类
class Tool:
    #去除img标签,1-7位空格,&nbsp;
    removeImg = re.compile('<img.*?>| {1,7}|&nbsp;')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    #将多行空行删除
    removeNoneLine = re.compile('\n+')
    def replace(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)
        x = re.sub(self.removeNoneLine,"\n",x)
        #strip()将前后多余内容删除
        return x.strip()

#糗事百科爬虫类
class QSBK:
    #初始化方法，定义一些变量
    def __init__(self):
        self.pageIndex = 3
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        #初始化headers
        self.headers = { 'User-Agent' : self.user_agent }
        #存放段子的变量，每一个元素是每一页的段子们
        self.stories = []
        #存放程序是否继续运行的变量
        self.enable = False
    #传入某一页的索引获得页面代码
    def getPage(self,pageIndex):
        try:
            url = 'http://www.qiushibaike.com/hot/page/' + str(pageIndex)
            #构建请求的request
            request = urllib2.Request(url,headers = self.headers)
            #利用urlopen获取页面代码
            response = urllib2.urlopen(request)
            #将页面转化为UTF-8编码
            pageCode = response.read().decode('utf-8')
            return pageCode

        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"连接糗事百科失败,错误原因",e.reason
                return None


    #传入某一页代码，返回本页不带图片的段子列表
    def getPageItems(self,pageIndex):
        pageCode = self.getPage(pageIndex)
        if not pageCode:
            print "页面加载失败...."
            return None
        # print pageCode
        pattern = re.compile('<div.*?class="author.*?>.*?<a(.*?)</a>.*?<a.*?>(.*?)</a>.*?<div.*?class'+
                         '="content">(.*?)<!.*?title="(.*?)">(.*?)</div>(.*?)<div class="stats.*?class="number">(.*?)</i>',re.S)
        items = re.findall(pattern,pageCode)
        #用来存储每页的段子们
        pageStories = []
        #遍历正则表达式匹配的信息
        for item in items:
            #是否含有图片
            haveImg = re.search("img",item[0])
            #如果不含有图片，把它加入list中
            # if not haveImg:
            # if haveImg:
                #item[0]是一个段子的发布者，item[1]是发布时间,item[2]是内容，item[4]是点赞数
            pageStories.append([item[2].strip()])#[item[0].strip(),item[1].strip(),item[2].strip(),item[4].strip()])
        return pageStories

    #加载并提取页面的内容，加入到列表中
    def loadPage(self):
        #如果当前未看的页数少于2页，则加载新一页
        if self.enable == True:
            if len(self.stories) < 2:
                #获取新一页
                pageStories = self.getPageItems(self.pageIndex)
                #将该页的段子存放到全局list中
                if pageStories:
                    self.stories.append(pageStories)
                    #获取完之后页码索引加一，表示下次读取下一页
                    self.pageIndex += 1

    #调用该方法，每次敲回车打印输出一个段子
    def getOneStory(self,pageStories,page):
        #遍历一页的段子
        for story in pageStories:
            #等待用户输入
            input = "P" #raw_input()
            #每当输入回车一次，判断一下是否要加载新页面
            self.loadPage()
            #如果输入Q则程序结束
            if input == "Q":
                self.enable = False
                return
            # print u"第%d页\t发布人:%s\t发布时间:%s\n%s\n赞:%s\n" %(page,story[0],story[1],story[2],story[3])
            print u"第%d页\t发布人:%s\n" %(page,story[0])
            # return

    #开始方法
    def start(self):
        print u"正在读取糗事百科,按回车查看新段子，Q退出"
        #使变量为True，程序可以正常运行
        self.enable = True
        #先加载一页内容
        self.loadPage()
        #局部变量，控制当前读到了第几页
        nowPage = 0
        while self.enable:
            if len(self.stories)>0:
                #从全局list中获取一页的段子
                pageStories = self.stories[0]
                #当前读到的页数加一
                nowPage += 1
                #将全局list中第一个元素删除，因为已经取出
                del self.stories[0]
                #输出该页的段子
                self.getOneStory(pageStories,nowPage)


class MyException(Exception):
    pass

class MyHTTPConnection(httplib.HTTPConnection):
    def send(self, s):
        print('\n----> Http Request Sended ---->')
        print( s )
        httplib.HTTPConnection.send(self, s)

class TB():
    def __init__(self):
        # self.OpenWeb()
        self.OpenLocal()
        #print "respHtml=",respHtml; # you should see the ouput html
        #<h1 class="h1user">crifan</h1>
        regex = '"raw_title":"(.*?)","pic_url":".*?"detail_url":"(.*?)","view_price":"(.*?)","view_fee"'
        regexobject = re.compile(regex)
        ls_title=re.findall(regexobject,self.respHtml)
        # print regexobject.search(self.respHtml).group(2)
        f=open('workfile.txt', 'w')
        list_val = re.split('\"title\":\"',self.respHtml)
        # print(list_val[1])
        # f.write(list_val[1])
        print(len(list_val)/2)
        # for i in range(1,len(list_val),1):
        for item in ls_title:
            print "%s,%s,%s" %(item[0],item[2],item[1])
            # if(re.search(r'dom_class',list_val[i])):      #list_val[i].find('dom_class')==-1
            #     continue
            # found=re.search('("reserve_price":")(.*?)(")',list_val[i]) #(r"(reserve_price\":\")(.*?)(?\")",list_val[i])
            # if(found):
            #     print found.group(2)
            f.write("\n*****************************************************************************************\n")
            f.write("%s,%s,%s" %(item[0],item[2],item[1]))

        #regex=re.compile(r'(\"raw_title\":\").+(\"pic_url\":\")')
        #print regex.findall(respHtml)
        # foundH2user = re.match(r'\"raw_title\":\".+', respHtml);
        # foundH1user = re.search(r'(\"title\":\")(.+)(\"raw_title\":\").+(\"pic_url\":\").+(\"detail_url\":\")', respHtml)
        # print "foundH1user=",foundH1user;
        # print "foundH2user=",foundH2user;
        # for i in range(1,10):
         #    if(foundH1user):
         #        h1user = foundH1user.group(i);
         #        print "h1user=",h1user;
        f.close()

    def OpenWeb(self):
        # MyHTTPHandler = MyHTTPConnection("Suc!")
        # password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        # top_level_url = "http://s.taobao.com/search?spm=a230r.1.1998181369.3.ZuIsox&q=%E6%89%8B%E6%9C%BA&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&initiative_id=tbindexz_20150609&app=vproduct&cd=false&v=auction&vlist=1&tab=old&sort=price-asc&bcoffset=0&s=0"
        # opener = urllib2.build_opener(MyHTTPHandler)
        # urllib2.install_opener(opener)
        # req = urllib2.Request("http://www.taobao.com")
        # response = opener.open(req)
        # content = response.read()


        # url="http://www.taobao.com" #"http://s.taobao.com/search?spm=a230r.1.1998181369.3.ZuIsox&q=%E6%89%8B%E6%9C%BA&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&initiative_id=tbindexz_20150609&app=vproduct&cd=false&v=auction&vlist=1&tab=old&sort=price-asc&bcoffset=0&s=0"
        # req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        # 'Accept':'text/html;q=0.9,*/*;q=0.8',
        # 'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        # 'Accept-Encoding':'gzip',
        # 'Connection':'close',
        # 'Referer':None
        # }
        # req_timeout = 5
        # req = urllib2.Request(url,None,req_header)
        # resp = urllib2.urlopen(req,None,req_timeout)
        # html = resp.read()
        # print(html)
        userMainUrl = "http://s.taobao.com/search?spm=a230r.1.1998181369.3.ZuIsox&q=%E6%89%8B%E6%9C%BA&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&initiative_id=tbindexz_20150609&app=vproduct&cd=false&v=auction&vlist=1&tab=old&sort=price-asc&bcoffset=0&s=0"  #"http://s.taobao.com/search?q=%E7%94%B5%E8%84%91&ie=utf8"  #"http://www.taobao.com"
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        req = urllib2.Request(userMainUrl,headers = headers)
        socket.setdefaulttimeout(300)
        # try: resp =urllib2.urlopen(req)#, timeout = 10)
        # except urllib2.URLError, e:
        #     print e.reason
        # return
        try:
            resp =urllib2.urlopen(req)#, timeout = 10)
        except urllib2.URLError, e:
            if hasattr(e,"code"):
                print e.code
            if hasattr(e,"reason"):
                print e.reason

        self.respHtml = resp.read()
        print "urlopen success!"
        resp.close()
        # return respHtml
    def OpenLocal(self):
        ws=open('web_source.txt', 'r')
        self.respHtml = ws.read()
        print ws.read()
        ws.close()


class Example():
    def __init__(self):
        page = 1
        # url = 'http://www.qiushibaike.com/hot/page/' + str(page)
        # url = 'http://s.taobao.com/'
        # url = 'http://mm.taobao.com/json/request_top_list.htm?page=1'
        # url = 'http://www.163.com'
        url = "http://s.taobao.com/search?spm=a230r.1.1998181369.3.ZuIsox&q=%E6%89%8B%E6%9C%BA&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&initiative_id=tbindexz_20150609&app=vproduct&cd=false&v=auction&vlist=1&tab=old&sort=price-asc&bcoffset=0&s=0"
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        try:
            request = urllib2.Request(url,headers = headers)
            # request.set_proxy('http://s.blefans.com:8123','http')
            response = urllib2.urlopen(request)
            print response.read()
        except urllib2.URLError, e:
        # except httplib.BadStatusLine,e:
            if hasattr(e,"code"):
                print e.code
            if hasattr(e,"reason"):
                print e.reason
            print "error"

#------------------------------------------------------------------------------
def main():
    ########################################################################
    prntTB = TB()
    ########################################################################
    # prntExp = Example()
    ########################################################################
    # spider = QSBK()
    # spider.start()
    ########################################################################
    #传入起止页码即可，在此传入了2,10,表示抓取第2到10页的MM
    # spider = Spider()
    # spider.savePagesInfo(2,10)
###############################################################################
if __name__=="__main__":
    main();
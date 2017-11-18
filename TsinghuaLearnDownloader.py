# -*- coding: utf-8 -*-
import requests,os,chardet
from bs4 import BeautifulSoup
from time import sleep
import sys
reload(sys)
sys.setdefaultencoding('utf8')
def getUTF8(str):
    strEncode=chardet.detect(str)
    return str.decode(strEncode['encoding']).encode('utf8')

def getUnicode(str):
    strEncode=chardet.detect(str)
    return str.decode(strEncode['encoding'])

cookie=0 #全局变量

def getHtml(url):
    req=requests.get(url,cookies=cookie)
    return BeautifulSoup(req.content)

def downFile(url,dirname):
    req=requests.get(url,cookies=cookie)
    filename=req.headers['Content-Disposition'].split('"')[-2]
    filesize=req.headers['Content-Length']
    print "Donwloading",getUnicode(filename)
    f=file(filename,"w")
    f.write(req.content)
    f.close()

def writeNote(str1,filename):
    f=file(filename,"w")
    f.write(str(str1))
    f.close()

class Course:
    def __init__(self,id,name,ltsoup,hwsoup,notesoup):
        self.id=id
        self.name=name
        self.ltsoup=ltsoup
        self.hwsoup=hwsoup
        self.notesoup=notesoup

    def mkDir(self,basedir):
        os.chdir(basedir) #切换路径
        if not os.path.isdir(self.name):
            print 'Start Donloading',self.name
            os.mkdir(self.name)
        dirpath= os.path.abspath(self.name)
        os.chdir(dirpath) #切换到当前课程文件的路径

    def getNote(self):
        if not os.path.isdir(u"课程公告"):
            os.mkdir(u"课程公告")
        dirpath= os.path.abspath(u"课程公告")
        os.chdir(dirpath)
        td1=self.notesoup.find_all('tr',"tr1") #DOM表签 是tr class="tr1"
        td2=self.notesoup.find_all('tr',"tr2")
        td1.extend(td2)
        if len(td1)>0:
            for i in td1:
                notestatus=i.find_all('td') #获取的有发布的时间和是未读的状态：已读，未读
                notename=notestatus[1].text.strip()  #g公告的名字
                noteauthor=notestatus[2].text.strip() #发布者
                notetime=notestatus[3].text.strip()# 发布的时间
                noteread=notestatus[4].text.strip() #是否已读
                notefilename=notetime+"_"+notename+"_"+noteread+'.txt'
                content=getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/public/bbs/"+i.a["href"])
                c1=content.find_all(attrs={"id":"table_box"})  #找寻id=tablebox 的属性
                c2=c1[0].find_all('tr')  #发现DOM元素
                c3=c2[1].find_all('td')
                c4=c3[1].text.strip()  #公告的具体内容
                writeNote(c4,notefilename)
            os.chdir("../")


    def getLtDownload(self):
        if not os.path.isdir(u"课程文件"):
            os.mkdir(u"课程文件")
        dirpath= os.path.abspath(u"课程文件")
        os.chdir(dirpath)

        tr1=self.ltsoup.find_all('tr',"tr1")
        tr2=self.ltsoup.find_all('tr',"tr2")
        tr1.extend(tr2)
        for lt in tr1:
            try:
                url="http://learn.tsinghua.edu.cn"+lt.a['href']
                name=lt.a.text.strip()
                downFile(url,dirpath)
            except Exception,e:
                pass
        os.chdir("../")

    def getHwDownload(self):
        if not os.path.isdir(u"课程作业"):
            os.mkdir(u"课程作业")
        dirpath= os.path.abspath(u"课程作业")
        os.chdir(dirpath)
        tr1=self.hwsoup.find_all(attrs={'class':"tr1"})
        #print len(tr1)
        tr2=self.hwsoup.find_all(attrs={'class':'tr2'})
        tr1.extend(tr2)
        for hw in tr1:
            try:
                hwpage=getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/"+hw.a['href'])
                name=hw.a.text.strip()
                dlurl=hwpage.find_all("a")#,attrs={"target","_top"})
                for url in dlurl:
                    downFile("http://learn.tsinghua.edu.cn"+url['href'],dirpath)
            except Exception, e:
                print e.message
              #  pass
        os.chdir("../")

def login():
    print u'清华大学网络学堂下载器'
    print u'--Create By SeaFish'

    username = raw_input('输入用户名:')
    password = raw_input("输入密码:")
    params = {'userid': username, 'userpass': password, 'submit1': '登录'}
    print ('login...')
    req = requests.post("http://learn.tsinghua.edu.cn/use_go.jsp", data=params)
    global cookie
    cookie=req.cookies  #获取登录所需的cookie

    if 'window.location = "loginteacher_action.jsp";' not in req.content:
        print u'登录错误,10s后自动退出'
        sleep(10)
    else:
        soup=getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?typepage=1")
        courses=soup.findAll(attrs={"width":"55%"})  #找到属性是width:55%的内ring
        print u'共有',courses.__len__(),u'门课程需要下载'
        basedir=os.path.dirname(os.path.abspath("__file__"))  #找到当前文件所在的路径
        try:
            for i in courses[0:]:
                course_url=i.a["href"]
                course_name=i.a.text.strip() #strip() 方法用于移除字符串头尾指定的字符（默认为空格）
                course_id =i.a["href"].split("=")[-1]

                # 课程公告的soup
                notesoup=getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/public/bbs/getnoteid_student.jsp?course_id="+str(course_id))
                #课程文件的soup
                ltsoup = getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/download.jsp?course_id=" + str(course_id))
                #课程作业的soup
                hwsoup = getHtml("http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/hom_wk_brw.jsp?course_id=" + str(course_id))

                c=Course(course_id,course_name,ltsoup,hwsoup,notesoup)
                c.mkDir(basedir)
                c.getNote()         #下载公告
                #c.getHwDownload()  #下载作业
                #c.getLtDownload()  #下载课程文件
                sleep(60)
        except Exception,e:
                print  e.message
                sleep(180)
'''
if __name__=="__main__":
    login()
'''
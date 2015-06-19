#-*- coding=utf-8 -*-
import requests
import Queue
from bs4 import BeautifulSoup
import time
import threading
import datetime

visitedQueue = Queue.Queue()
unvisitedQueue = Queue.Queue()
imgQueue = Queue.Queue()

class Spider(object):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.39 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6'
    }

    def __init__(self, startUrl, prefix="http://www.zappos.com", deep=3):
        self.startUrl = startUrl
        self.deep = deep
        self.currentDeep = 0
        self.prefix = prefix
        self.putSeed()
        self.bloomFilter = {}


    def putSeed(self):
        unvisitedQueue.put(self.startUrl)

    def getContent(self, url):
        for i in range(3):
            try:
                r = requests.get(url,headers=self.headers, timeout=20)
                time.sleep(0.3)
                return r.content
            except Exception,e:
                print e
                continue

    def findUrl(self,content, coding="utf-8"):
        if not content:
            return []
        content = BeautifulSoup(content, from_encoding=coding)
        links = content.find_all("a")
        return links

    def bloomfiter(self, url):
        if self.bloomFilter.get(url):
            print "has visited this url %s", url
            return True
        self.bloomFilter[url] = 1
        return False

    def analyse(self):
        while self.currentDeep <= self.deep:
            links = []
            while not unvisitedQueue.empty():
                print "the current deep is %s" %self.currentDeep
                url = unvisitedQueue.get()
                print "pop from unvisited queue: %s" %(url)
                if not url or self.bloomfiter(url):
                    continue
                content = self.getContent(url)
                links = self.findUrl(content, coding="gbk")
                visitedQueue.put(url)
            for link in links:
                try:
                    href = link.attrs.get("href")
                    unvisitedUrl = href if href.find("://") >= 0 else self.prefix+href
                    unvisitedQueue.put(unvisitedUrl)
                except Exception, e:
                    continue
            self.currentDeep += 1

class TheadGetImg(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = False

    def run(self):
        while not self.stop:
            print "url thread is coming"
            try:
                url = visitedQueue.get(False) # arg1 means "Don't wait for items
                # to appear"
            except Queue.Empty:
                time.sleep(3)
                continue
            print '==========to do url is:' + url +"============="
            try:
                r = requests.get(url, timeout=20)
                if r.status_code != 200:
                    continue
                content = r.content
                content_bs = BeautifulSoup(content, from_encoding="gbk")
                imgs = content_bs.find_all("img")
                for img in imgs:
                    src = img.get("src")
                    picUrl = src if src.find("://") >=0 else "http://pp.ueos.pw/" + src
                    imgQueue.put(picUrl)
            except Exception,e:
                print e
                continue

class DownLoadImg(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = False

    def run(self):
        while not self.stop:
            print "download img loop!!!"
            try:
                src = imgQueue.get(False) # arg1 means "Don't wait for items
                # to appear"
            except Queue.Empty:
                time.sleep(3)
                continue
            self.downLoad(src)

    def downLoad(self,url):
        try:
            print "!!!!!!start download picture!!!!!!", url
            r = requests.get(url, timeout=20)
            path = "img/"
            name = str(int(time.time()*1000000))
            type = url[-3:]
            path_new = path+name+"."+type
            with open(path_new, "wb") as jpg:
                jpg.write(r.content)
        except Exception,e:
            pass

if __name__ == "__main__":
    t = TheadGetImg()
    t.start()

    s = DownLoadImg()
    s.start()

    a = Spider("http://pp.ueos.pw/thread0806.php?fid=7", "http://pp.ueos.pw/")
    a.analyse()
    print visitedQueue._qsize()


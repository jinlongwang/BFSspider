#-*- coding=utf-8 -*-
import requests
import Queue
from bs4 import BeautifulSoup
import time

visitedQueue = Queue.Queue()
unvisitedQueue = Queue.Queue()

class Spider(object):
    prefix = "http://www.zappos.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.39 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6'
    }

    def __init__(self, startUrl,deep=3):
        self.startUrl = startUrl
        self.deep = deep
        self.currentDeep = 0
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

    def findUrl(self,content):
        if not content:
            return []
        content = BeautifulSoup(content)
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
                links = self.findUrl(content)
                visitedQueue.put(url)
            for link in links:
                try:
                    href = link.attrs.get("href")
                    unvisitedUrl = href if href.find("://") >= 0 else self.prefix+href
                    unvisitedQueue.put(unvisitedUrl)
                except Exception, e:
                    continue
            self.currentDeep += 1

if __name__ == "__main__":
    a = Spider("http://www.zappos.com/running-shoes")
    a.analyse()
    print visitedQueue._qsize()

import Pyro4
from Pyro4 import naming
import os
import _pickle as cPickle
import threading
import queue as Queue
import time
import linecache
import sys


def print_exce():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


class Director:

    def __init__(self):
        self.target_urls = []
        if os.path.exists('Visited.pkl'):
            visited = open('Visited.pkl', 'rb')
            self.visited_urls = cPickle.load(visited)
            visited.close()
        else:
            self.visited_urls = []

    def add_new(self, url):
        if url not in self.visited_urls:
            self.target_urls.append(url)

    def new_urls(self):
        return self.target_urls

    def update_record(self):
        self.visited_urls.append(self.target_urls)
        visited_list = open('Visited.pkl', 'wb')
        cPickle.dump(self.visited_urls, visited_list)
        visited_list.close()


class CrawlerThread(threading.Thread):

    def __init__(self, nameserver, crawler_ident, queue):
        threading.Thread.__init__(self)
        crawler_uri = nameserver.lookup('Crawler'+crawler_ident)
        self.queue = queue
        self.crawler = Pyro4.Proxy(crawler_uri)
        self.crawler_ident = crawler_ident
        self.count = 0

    def run(self):
        while self.count < 3:
            target = self.queue.get()
            print(target +' - '+ self.crawler_ident)
            try:
                self.crawler.crawl(target)
                self.count += 1

            except Exception as e:
                print_exce()
                print(e)
            else:
                url_file = open('URLlist'+self.crawler_ident, 'a')
                for line in self.crawler.return_urls():
                    url_file.write(line+'\n')
                url_file.close()
                time.sleep(3)
            self.queue.task_done()


class Executive:
    def __init__(self):
        ns_host = input('enter nameserver ip: ')
        self.crawler_count = int(input('enter the number of crawler instances: '))
        self.director = Director()
        self.ns = naming.locateNS(ns_host)
        self.queue = Queue.Queue()

    def begin(self):
        current = os.getcwd()
        for document in os.listdir(current):
            if document.startswith('URLlist'):
                url_file = open(document, 'r')
                for line in url_file:
                    line = line.strip()
                    self.director.add_new(line)
        target_urls = self.director.new_urls()
        for url in target_urls:
            self.queue.put(url)
        for i in range(self.crawler_count):
            crawler = CrawlerThread(self.ns, str(i), self.queue)
            crawler.setDaemon(True)
            crawler.start()
        self.queue.join()

    def update(self):
        self.director.update_record()


if __name__ == "__main__":
    executive = Executive()
    executive.begin()
    print('Completed Begin')
    executive.update()

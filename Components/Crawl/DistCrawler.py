#!/usr/bin/env python

from urllib.parse import urlparse, urljoin
import mechanize
import re
# import ipaddress
import Pyro4
# TODO: BS -> bs4
# from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
from time import sleep
from DataReduce import DataReduce
import requests
from Pyro4 import naming

@Pyro4.expose
class Crawler:
    def __init__(self):
        self.datareduce = DataReduce()
        self.visited = []
        self.internal_urls = []
        # self.br = mechanize.Browser()
        # self.br.addheaders =[('User-agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
        #                                    'Ubuntu Chromium/45.0.2454101')]

    def crawl(self, target):
        current_url_parts = urlparse(target)
        # TODO: try just bs4 instead of mechanize
        # try:
        #     response = self.br.open(target)
        #     self.br._factory.is_html = True
        #
        # except requests.HTTPError as error:
        #     print(error)
        # except mechanize._mechanize.BrowserStateError as p:
        #     print(p)
        # else:
        if target.startswith('https') or target.startswith('http'):
            self.visited.append(target)
        else:
            self.visited.append('https://'+target)
        print(target)

        soup = BeautifulSoup(requests.get('https://' + target, 'GET').text, 'lxml')
        # soup = BeautifulSoup(response)
        page_content = soup.findAll('p')
        for p_tag in page_content:

            p_tag = re.sub('\<\/?p\>|\<a href.*\<\/a\>', '', str(p_tag))
            p_tag = re.sub('\<\/?[a-zA-Z0-9]+\>', '', p_tag)
            p_tag = re.sub('[^A-Za-z]', ' ', p_tag)
            self.datareduce.reduce_content(p_tag.lower())

        # Change: for LINKS
        #for link in list(self.br.links()):
        for link in soup.find_all('a', href=True):
            link = link['href']

            """if '@' not in link.url and '?' not in link.url and '#' not in link.url:
                link_parts =  urlparse.urlparse(link.url)
                if not bool(link_parts.netloc) or link_parts.netloc == current_url_parts.netloc:
                    link = 'http://'+current_url_parts.netloc+link_parts.path
                    if link not in self.visited and link not in self.internal_urls:
                        self.internal_urls.append(link)
                else:
                    link = 'http://%s' % (urlparse.urlparse(link.url).netloc)
                    self.datareduce.reduce_links(link)"""

            if '@' not in link and '?' not in link and '#' not in link:
                link_parts = urlparse(link)
                if not bool(link_parts.netloc) or link_parts.netloc == current_url_parts.netloc:
                    link = 'http://'+current_url_parts.netloc+link_parts.path
                    if link not in self.visited and link not in self.internal_urls:
                        self.internal_urls.append(link)
                    else:
                        link = 'http://%s' % urlparse(link).netloc
                        self.datareduce.reduce_links(link)

            elif link.startswith('#') or link.startswith('?'):
                pass
            elif link.startswith('/'):
                self.internal_urls.append(urljoin(target, link))

            sleep(1)

        # if len(self.internal_urls) > 0:
        #     next_target = self.internal_urls.pop()
        #     print(next_target)
        #     self.crawl(next_target)

    def return_urls(self):
        print(self.datareduce.return_urls())
        return self.datareduce.return_urls()

        
if __name__ == '__main__':
    hostname = input('enter host ip: ')
    ident = input('enter crawler identifier: ')
    crawler = Crawler()
    nameserver = naming.locateNS(host='10.7.1.137', port= 9090)
    print(nameserver)
    Pyro4.config.NS_HOST = "10.7.1.137"
    Pyro4.Daemon.serveSimple(
            {
                crawler: 'Crawler%s' % (ident)
            },
            host = hostname,
            ns = True, verbose = True)
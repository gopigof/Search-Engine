import requests
import bs4
from urllib.parse import urlparse
# from DataReduce import reduce_links


internal_urls, current_url_parts, visited = [], [], []
target = 'www.crummy.com/software/BeautifulSoup/bs4/doc/'

if target.startswith('https') or target.startswith('http'):
    visited.append(target)
else:
    visited.append('https://' + target)
    target = 'https://'+target

req = requests.get(target, 'GET')
print(req)

soup = bs4.BeautifulSoup(req.text, 'html.parser')

# datareduce = DataReduce()
# for link in soup.find_all('a', href=True):
#     link = link['href']
#     if '@' not in link and '?' not in link and '#' not in link:
#         link_parts = urlparse(link)
#         if not bool(link_parts.netloc) or link_parts.netloc == current_url_parts.netloc:
#             link = 'http://' + current_url_parts.netloc + link_parts.path
#             if link not in visited and link not in internal_urls:
#                 internal_urls.append(link)
#             else:
#                 link = 'http://%s' % urlparse(link).netloc
#                 datareduce.reduce_links(link)

# print(soup.get_text)
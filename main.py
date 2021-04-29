# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import code
import datetime
import random
import time
import urllib
from bs4 import BeautifulSoup

import builtwith
import whois
import re
from urllib.request import urlopen
from urllib.error import URLError
from urllib import parse
from urllib import robotparser


class Downloader:
    def __init__(self, delay=5, user_agent='wswp', proxies=None, num_retries=1, cache=None):
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        self.cache = cache

    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                pass
            else:
                if self.num_retries > 0 and \
                        500 <= result['code'] < 600:
                    result = None
        if result is None:
            self.throttle.wait(url)
            proxy = random.choice(self.proxies) if self.proxies else None
            headers = {'User_agent': self.user_agent}
            result = self.download(url, headers, proxy, self.num_retries)
            if self.cache:
                self.cache[url] = result
        return result['html']

    def download(self, url, headers, proxy=None, num_retries=2, data=None):
        print("Downloading:", url)
        headers = {'User-agent': headers}
        request = urllib.request.Request(url, headers=headers)
        opener = urllib.request.build_opener()
        if proxy:
            proxy_params = {parse.urlparse(url).scheme: proxy}
            opener.add_handler(urllib.request.ProxyHandler(proxy_params))
        try:
            html = urllib.request.urlopen(request).read()
        except urllib.error.HTTPError as e:
            print("Download error:", e.reason)
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    return self.download(url, headers, proxy, num_retries - 1)
        print(html)
        return {'html': html, 'code': code}


def crawl_sitemap(url):
    downloader = Downloader()
    sitemap = downloader.download(url)
    links = re.findall('<loc>(.*?)</loc>', sitemap)
    for link in links:
        html = downloader.download(link)
        print(html)


def link_crawler(seed_url, link_regex, max_depth=2, cache=None):
    rp = robotparser.RobotFileParser()
    user_agent = 'GoodCrawler'
    crawl_queue = [seed_url]
    seen = {}
    D = Downloader()
    while crawl_queue:
        url = crawl_queue.pop()
        rp.set_url(url)
        if rp.can_fetch(user_agent, url):
            html = D.download(url)
            depth = seen[url]
            if depth != max_depth:
                for link in get_links(html):
                    if re.match(link_regex, link):
                        link = parse.urljoin(seed_url, link)
                        if link not in seen:
                            seen[link] = depth + 1
                            crawl_queue.append(link)
        else:
            print('Blocked bu robot.txt:', url)


def get_links(html):
    webpage_regex = re.compile('a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


class Throttle:
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = parse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.datetime.now()


broken_html = '<ul class=country><li><li>Area<li>Population</ul>'
soup = BeautifulSoup(broken_html, 'html.parser')
fixed_html = soup.prettify()
print(fixed_html)

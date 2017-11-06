# -*- coding:utf-8 -*-  
"""
--------------------------------
    @Author: Dyson
    @Contact: Weaver1990@163.com
    @file: crawler.py
    @time: 2017/10/30 11:47
--------------------------------
"""
import sys
import os
import traceback
import json
import pandas as pd
import bs4

sys.path.append(sys.prefix + "\\Lib\\MyWheels")
reload(sys)
sys.setdefaultencoding('utf8')
import set_log  # log_obj.debug(文本)  "\x1B[1;32;41m (文本)\x1B[0m"
import driver_manager
import requests_manager
requests_manager = requests_manager.requests_manager()
driver_manager = driver_manager.driver_manager()

log_obj = set_log.Logger('crawler.log', set_log.logging.WARNING,
                         set_log.logging.DEBUG)
log_obj.cleanup('crawler.log', if_cleanup=True)  # 是否需要在每次运行程序前清空Log文件

class crawler(object):
    def __init__(self):
        with open('page_count.json', 'r') as f:
            self.page_count = json.load(f)
        self.used_urls = set()

    def main(self):
        #s_list = self.get_urls()
        with open('urls.txt', 'r') as f:
            s = f.read()
            s_list = s.split('\n')

        for s0 in s_list:
            s, url = s0.split('|')
            if os.path.exists(s + '.csv'):
                print "正在读取文件", s + '.csv'
                df = pd.read_csv(s+'.csv', encoding='utf_8_sig')
                if 'url' in df.columns:
                    self.used_urls = set(df['url'].tolist())
            else:
                df = pd.DataFrame([])
            print s, url

            # 一定要获得一个学科的总页数
            while s not in self.page_count:
                self.get_max_page(s, url)

            for ser in self.parse_catalog(s, url):
                if ser.empty:
                    continue
                df = df.append(ser, ignore_index=True)
                df.to_csv(s+'.csv', encoding='utf_8_sig', index=None)

    def get_urls(self):
        root_url = "https://www.usnews.com/education/best-global-universities"
        bs_obj = bs4.BeautifulSoup(driver_manager.get_html(root_url, engine='Chrome'), 'html.parser')
        #print bs_obj.prettify()
        e_div = bs_obj.find_all('div', class_='media block')[2]
        l = []
        for e_a in e_div.find_all('a'):
            s = e_a.get_text()
            url = "https://www.usnews.com/" + e_a.get('href')
            with open('urls.txt', 'a') as f:
                f.write(s + '|' + url + '\n')
            l.append(s + '|' + url)
        return l

    def parse_catalog(self, subject, url0):
        max_page = self.page_count[subject]
        urls0 = [url0 + ('?page=%s' %(i+1)) for i in range(max_page) if i > 0]
        urls = [url0,] + urls0
        for url in urls:
            print "正在解析：", url
            if url in self.used_urls:
                print '%s pass page %s' %(subject, url)
                continue

            driver = driver_manager.initialization(engine='Chrome')
            try:
                driver.get('about:blank')
                driver.get(url)
                bs_obj = bs4.BeautifulSoup(driver.page_source, 'html.parser')
                e_div = bs_obj.find('div', id='resultsMain')
                e_rows = e_div.find_all('div', class_='sep')

                for e_row in e_rows:
                    point = e_row.find('div', class_='t-large t-strong t-constricted').get_text(strip=True)
                    rank = e_row.find('span', class_='rankscore-bronze').get_text(strip=True)
                    university = e_row.find('h2', class_='h-taut').get_text()
                    address = e_row.find('div', class_='t-taut').get_text()
                    addition = e_row.find_all('div')[-1].get_text()
                    d = {
                        u"得分":point,
                        u"排名":rank,
                        u"大学":university,
                        u"地址":address,
                        u"其他":addition,
                        u"url":url
                    }

                    d = {key: d[key].strip() for key in d}
                    ser = pd.Series(d)

                    print pd.DataFrame(ser).T
                    yield ser

            except:
                log_obj.error(url)
                log_obj.error(traceback.format_exc())

            driver.quit()

    def get_max_page(self, subject, url):
        driver = driver_manager.initialization(engine='Chrome')
        try:
            driver.get('about:blank')
            driver.get(url)
            bs_obj = bs4.BeautifulSoup(driver.page_source, 'html.parser')

            page_row = bs_obj.find('div', class_='pagination')
            max_page = page_row.find_all('a')[-2].get_text(strip=True)
            self.page_count[subject] = int(max_page)
            print "这学科%s排名一共%s页" % (subject, max_page)
            with open('page_count.json', 'w') as f:
                 json.dump(self.page_count, f)
        except:
            log_obj.error(url)
            log_obj.error(traceback.format_exc())
        driver.quit()


if __name__ == '__main__':
    crawler = crawler()
    crawler.main()
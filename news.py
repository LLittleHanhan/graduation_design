import json
import time

import requests
from bs4 import BeautifulSoup as bs
import pymysql
from pymysql.converters import escape_string
from pymysql.cursors import DictCursor
import datetime

'''
('“五一”假期出行报告：机票、火车票、酒店数据加速回温',
 '2023-05-03', 
 'https://news.cctv.com/2023/05/03/ARTIbTbRSiYY7WXAz5aGZ5gQ230503.shtml', 
  None)
'''


class news_spider:
    """
    platform:
        yangshi:0
        xinlang:1
    """
    # requests
    _headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/73.0.3683.103 Safari/537.36",
    }
    # mysql
    _host = '114.116.7.188'
    _port = 3306
    _user = 'white'
    _password = 'Byf.473882'
    _db = 'news'

    def __init__(self, reset=False):
        self._cre_table()
        if reset:
            self._del_table()
        self._dis_info()

    # mysql管理
    def _connect(self):
        try:
            db = pymysql.connect(host=self._host, port=self._port, user=self._user, password=self._password,
                                 db=self._db,
                                 charset='utf8')
        except pymysql.Error:
            print('connect fail')
            raise
        return db

    def _del_table(self):
        print('删除表中所有内容')
        db = self._connect()
        cursor = db.cursor()
        cursor.execute('drop table news')
        db.close()
        self._cre_table()

    def _cre_table(self):
        db = self._connect()
        cursor = db.cursor()
        sql = 'create table if not exists news(platform int not null,title text not null,date date not null,url char(255) primary key,text mediumtext)'
        cursor.execute(sql)
        db.close()

    def _dis_info(self):
        db = self._connect()
        cursor = db.cursor()
        cursor.execute('select count(*) from news')
        print('database现有url数量:', cursor.fetchone()[0])
        db.close()

    def _sum_url(self):
        db = self._connect()
        cursor = db.cursor()
        cursor.execute('select count(*) from news')
        sum_url = cursor.fetchone()[0]
        db.close()
        return sum_url

    def _insert_news_url(self, news_list, platform):
        before = self._sum_url()
        # insert table
        db = self._connect()
        cursor = db.cursor()
        for news in news_list:
            sql = 'insert ignore into news(title,date,url,platform) values("{title}","{date}","{url}",{platform})'.format(
                title=escape_string(news['title']),
                date=escape_string(news['date']),
                url=escape_string(news['url']),
                platform=platform)
            cursor.execute(sql)
        db.commit()
        db.close()
        after = self._sum_url()
        print('净增加url数量:', after - before)

    # 央视更新最新url
    def _update_yangshi_news_url(self):
        # url提取
        news_list = []
        cls = ['china', 'world', 'society', 'law', 'ent', 'tech', 'life']
        for idx in range(len(cls)):
            page = 1
            while True:
                url = 'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/' + cls[
                    idx] + f'_{page}' + '.jsonp?cb=' + cls[idx]
                resp = requests.get(url, headers=self._headers)
                if resp.status_code != 200:
                    break
                else:
                    json_str = resp.content.decode('utf-8')[len(cls[idx]) + 1:-1]
                    json_data = json.loads(json_str)
                    for news in json_data['data']['list']:
                        if news['url'][8:12] != 'news':
                            continue
                        dic = {'title': news['title'], 'date': str(news['focus_date']).split(' ')[0],
                               'url': news['url']}
                        news_list.append(dic)
                page += 1
        print('更新央视网url数量', len(news_list))
        self._insert_news_url(news_list, 0)

    # 新浪网指定日期url;begin,end默认为时间戳格式
    def _update_xinlang_news_url(self, begin_stamp, end_stamp):
        news_list = []
        # 长时间段分天抓取
        while begin_stamp != end_stamp:
            page = 1
            total_page = 1
            # 一页50个
            while page <= total_page:
                url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&etime={begin}&stime={end}&num=50&page={page}' \
                    .format(begin=begin_stamp, end=begin_stamp + 86400, page=page)
                resp = requests.get(url, headers=self._headers)
                if resp.status_code != 200:
                    print("请求失败!")
                else:
                    json_data = json.loads(resp.content.decode('utf-8'))
                    if page == 1:
                        total_num = json_data['result']['total']
                        total_page = total_num // 50 + 1
                    for news in json_data['result']['data']:
                        time_str = time.strftime("%Y-%m-%d", time.localtime(begin_stamp))
                        dic = {'title': news['title'], 'date': time_str, 'url': news['url']}
                        news_list.append(dic)
                page += 1
            begin_stamp += 86400
        print('更新新浪网url数量:', len(news_list))
        self._insert_news_url(news_list, 1)

    def get_news(self, begin=None, end=None):
        # 更新url
        today = '{year}-{month}-{day}'.format(year=datetime.datetime.now().year, month=datetime.datetime.now().month,
                                              day=datetime.datetime.now().day)
        today_stamp = int(time.mktime(time.strptime(today, "%Y-%m-%d")))

        if begin is None:
            begin_stamp = today_stamp
            end_stamp = today_stamp + 86400
        else:
            begin_stamp = int(time.mktime(time.strptime(begin, "%Y-%m-%d")))
            end_stamp = int(time.mktime(time.strptime(end, "%Y-%m-%d")))
        # 央视新闻策略
        if today_stamp - end_stamp <= 7 * 24 * 60 * 60:
            print('yes')
            self._update_yangshi_news_url()
        self._update_xinlang_news_url(begin_stamp, end_stamp)

        news_list = []
        db = self._connect()
        cursor = db.cursor(DictCursor)
        while begin_stamp < end_stamp:
            date = time.strftime("%Y-%m-%d", time.localtime(begin_stamp))
            sql = 'select * from news where date = "{date}"'.format(date=date)
            cursor.execute(sql)
            data = cursor.fetchall()
            print('date is ' + date + ' 准备解析text，获取当日url数量:', len(data))
            for news in data:
                if news['text'] is None:
                    text = ''
                    if news['platform'] == 0:
                        text = self._analyse_yangshi_url(news['url'])
                    elif news['platform'] == 1:
                        text = self._analyse_xinlang_url(news['url'])
                    # match news['platform']:
                    #     case 0:
                    #         text = self._analyse_yangshi_url(news['url'])
                    #     case 1:
                    #         text = self._analyse_xinlang_url(news['url'])
                    if text == '' or len(text) < 15:
                        continue
                    news['text'] = text
                    sql = 'update news set text = "{text}" where url = "{url}"'.format(text=escape_string(text),
                                                                                       url=news['url'])
                    cursor.execute(sql)
                news_list.append(news)
            begin_stamp += 86400
        db.commit()
        db.close()
        print('成功解析数量', len(news_list))
        return news_list

    def _analyse_yangshi_url(self, url):
        text = ''
        html = requests.get(url, self._headers).content
        parent = bs(html, 'lxml').find(class_='content_area')
        if parent is not None:
            for child in parent.findAll(name='p'):
                for string in child.stripped_strings:
                    text += string
        return text

    def _analyse_xinlang_url(self, url):
        text = ''
        html = requests.get(url, self._headers).content
        parent = bs(html, 'lxml').find(class_='article')
        if parent is not None:
            for child in parent.findAll(name='p'):
                for string in child.stripped_strings:
                    text += string
        return text


spider = news_spider(reset=True)

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
        sql = 'create table if not exists news(platform int not null,title text not null,date date not null,url char(255) primary key,text text)'
        cursor.execute(sql)
        db.close()

    def _dis_info(self):
        db = self._connect()
        cursor = db.cursor()
        cursor.execute('show tables')
        print(cursor.fetchall())
        cursor.execute('select count(*) from news')
        print('本地url数量:', cursor.fetchone()[0])
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
        print('增加url数量:', after - before)

    # 央视更新最新url
    def update_yangshi_news_url(self):
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
        print('获取央视网url数量', len(news_list))
        self._insert_news_url(news_list, 0)

    # 新浪网指定日期url;begin,end默认为时间戳格式
    def update_xinlang_news_url(self, begin, end, is_stamp=False):
        news_list = []
        if is_stamp:
            begin_stamp = begin
            end_stamp = end
        else:
            begin_stamp = int(time.mktime(time.strptime(begin, "%Y-%m-%d")))
            end_stamp = int(time.mktime(time.strptime(end, "%Y-%m-%d")))
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
        print('获取新浪网url数量:', len(news_list))
        self._insert_news_url(news_list, 1)

    def update_url(self):
        pass

    def get_news(self):
        news_list = []
        today = '{year}-{month}-{day}'.format(year=datetime.datetime.now().year, month=datetime.datetime.now().month,
                                              day=datetime.datetime.now().day)
        today_stamp = int(time.mktime(time.strptime(today, "%Y-%m-%d")))
        self.update_yangshi_news_url()
        self.update_xinlang_news_url(today_stamp, today_stamp + 86400, is_stamp=True)

        db = self._connect()
        cursor = db.cursor(DictCursor)
        sql = 'select * from news where date = "{today}"'.format(today=today)
        cursor.execute(sql)
        data = cursor.fetchall()

        print('today is ' + today)
        print('获取最新url数量', len(data))

        for news in data:
            if news['text'] is None:
                text = ''
                match news['platform']:
                    case 0:
                        text = self._analyse_yangshi_url(news['url'])
                    case 1:
                        text = self._analyse_xinlang_url(news['url'])
                if text == '':
                    continue
                news['text'] = text
                sql = 'update news set text = "{text}" where url = "{url}"'.format(text=escape_string(text),
                                                                                   url=news['url'])
                cursor.execute(sql)
            news_list.append(news)
        db.commit()

        # 显示结果
        sql = 'select * from news where date = "{today}" and text is not null'.format(today=today)
        cursor.execute(sql)
        for data in cursor.fetchall():
            print(data)

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
        return text


spider = news_spider(reset=False)
spider.get_news()
# spider.update_xinlang_news_url('2022-8-5', '2022-8-9')

# url = 'https://finance.sina.com.cn/china/gncj/2022-05-03/doc-imcwipii7755771.shtml'
# page = requests.get(url,headers).content.decode('utf8')
# html=bs(page, "lxml")
# print(html.find(class_ = 'main-title').string)
# father = html.find(class_ = 'article')
# for child in father.findAll(name = 'p'):
#     print(child.string)

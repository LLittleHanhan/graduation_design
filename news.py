import json
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


class news():
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
        db = self._connect()
        cursor = db.cursor()
        cursor.execute('truncate table news')
        db.close()

    def _cre_table(self):
        db = self._connect()
        cursor = db.cursor()
        sql = 'create table if not exists news(title text not null,date date not null,url char(255) primary key,text text)'
        cursor.execute(sql)
        db.close()

    def _dis_info(self):
        db = self._connect()
        cursor = db.cursor()
        cursor.execute('show tables')
        print(cursor.fetchall())
        cursor.execute('select * from news')
        print(cursor.fetchone())
        cursor.execute('select count(*) from news')
        print(cursor.fetchone())
        db.close()

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
                    print("请求失败!")
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
        print(len(news_list))
        # insert table
        db = self._connect()
        cursor = db.cursor()
        for news in news_list:
            sql = 'insert ignore into news(title,date,url) values("{title}","{date}","{url}")'.format(
                title=escape_string(news['title']),
                date=escape_string(news['date']),
                url=escape_string(news['url']))
            print(sql)
            cursor.execute(sql)
        db.commit()

        # # 解析url
        # path = './yangshi.csv'
        # with open(path, 'w', encoding='utf-8-sig') as f:
        #     header = ['title', 'date', 'url', 'text']
        #     writer = csv.DictWriter(f, header)
        #     writer.writeheader()
        #     for news in news_list:
        #         url = news['url']
        #         html = requests.get(url, self._headers).content
        #         parent = bs(html, 'lxml').find(class_='content_area')
        #         if parent is not None:
        #             text = ''
        #             for child in parent.findAll(name='p'):
        #                 for string in child.stripped_strings:
        #                     text += string
        #             if text == '':
        #                 continue
        #             news['text'] = text
        #             writer.writerow(news)

    # 新浪网指定日期url
    def update_xinlang_news_url(self, begin, end):
        pass

    def get_last_news(self):
        news_list = []
        self.update_yangshi_news_url()
        today = '{year}-{month}-{day}'.format(year=datetime.datetime.now().year, month=datetime.datetime.now().month,
                                              day=datetime.datetime.now().day)
        db = self._connect()
        cursor = db.cursor(DictCursor)
        sql = 'select * from news where date = "{today}"'.format(today=today)
        print(sql)
        cursor.execute(sql)
        for news in cursor.fetchall():



    def get_news(self, begin, end):
        pass

    def analyse_yangshi_url(self,url):
        text = ''

        return text
spider = news(reset=False)
spider.get_last_news()
# spider.get_yangshi_news_url()

# def get_xinlang_news():
#     url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2510&etime=1651590000&stime=1651680000' \
#           '&k=&num=50&page=1'
#     resp = requests.get(url, headers=headers)
#     if resp.status_code != 200:
#         print("请求失败!")
#     else:
#         json_data = json.loads(resp.content.decode('utf-8'))
#         print(json_data)
#         print(len(json_data['result']['data']))
#         for data in json_data['result']['data']:
#             print(data)

# news_info = get_yangshi_news()


# url = 'https://finance.sina.com.cn/china/gncj/2022-05-03/doc-imcwipii7755771.shtml'
# page = requests.get(url,headers).content.decode('utf8')
# html=bs(page, "lxml")
# print(html.find(class_ = 'main-title').string)
# father = html.find(class_ = 'article')
# for child in father.findAll(name = 'p'):
#     print(child.string)

import gzip
import json
import requests
import newspaper
from bs4 import BeautifulSoup as bs
import lxml

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/73.0.3683.103 Safari/537.36",
}


def get_yangshi_news():
    news_info = []
    cls = ['china', 'world', 'society', 'law', 'ent', 'tech', 'life']
    max_page = [7, 7, 7, 6, 3, 3, 7]
    for idx in range(len(cls)):
        page = 1
        while page <= max_page[idx]:
            url = 'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/' + cls[idx] + f'_{page}' + '.jsonp?cb=' + \
                  cls[idx]
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                print("请求失败!")
                break
            else:
                print(resp.content)
                json_str = resp.content.decode('utf-8')[len(cls[idx]) + 1:-1]
                # print(json_str)
                json_data = json.loads(json_str)
                news_info.extend(json_data['data']['list'])
            page += 1
    print(len(news_info))
    return news_info


def get_xinlang_news():
    url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&etime=1651420800&stime=1651507200&ctime' \
          '=1651507200&date=2022-05-02&k=&num=50&page=1&r=0.36221773091657283'
    resp = requests.get(url, headers=headers)
    print(resp.encoding)
    print(resp.headers['content-encoding'])
    if resp.status_code != 200:
        print("请求失败!")
    else:
        json_data = json.loads(resp.content.decode('utf-8'))
        for data in json_data['result']['data']:
            print(data)




# news_info = get_yangshi_news()
# for news in news_info:
#     print(news['url'])
#     # print(news[])
#     article = newspaper.Article(news['url'], language='zh')
#     article.download()
#     article.parse()
#     print('题目：', article.title)  # 新闻题目
#     print('正文：\n', article.text)  # 正文内容
#     print(article.authors)  # 新闻作者
#     print(article.keywords)  # 新闻关键词
#     print(article.summary)  # 新闻摘要
#     break

url = 'https://finance.sina.com.cn/china/gncj/2022-05-03/doc-imcwipii7755771.shtml'
page = requests.get(url,headers).content.decode('utf8')
html=bs(page, "lxml")
print(html.find(class_ = 'main-title').string)
father = html.find(class_ = 'article')
for child in father.findAll(name = 'p'):
    print(child.string)
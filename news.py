import json
import requests
import newspaper

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
}
news_info = []
def get_news():
    page = 1
    while True:
        origin = f'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/news_{page}.jsonp?cb=news'
        resp = requests.get(origin, headers=headers)
        if resp.status_code != 200:
            print("请求失败!")
            break
        else:
            # print(resp.content.decode('utf-8'))
            json_str = resp.content.decode('utf-8')[5:-1]
            json_data = json.loads(json_str)
            # print(json_data['data']['total'])
            news_info.extend(json_data['data']['list'])
            # print(len(news_info))
        page += 1
    print(len(news_info))
    for news in news_info:
        print(news)




get_news()
for news in news_info:
    print(news['url'])
    # print(news[])
    article = newspaper.Article(news['url'],language = 'zh')
    article.download()
    article.parse()
    print('题目：', article.title)  # 新闻题目
    print('正文：\n', article.text)  # 正文内容
    print(article.authors)  # 新闻作者
    print(article.keywords)  # 新闻关键词
    print(article.summary)  # 新闻摘要
    break
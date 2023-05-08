from news import news_spider


class Data:

    def __init__(self):
        self.news_list = None
        self.spider = news_spider(reset=False)

    def get_news(self, begin=None, end=None):
        self.news_list = self.spider.get_news(begin, end)

    def get_news_list(self):
        return self.news_list

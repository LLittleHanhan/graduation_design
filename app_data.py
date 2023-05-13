from news import news_spider
from wordcloud import WordCloud
import jieba
import jieba.analyse


class Data:
    def __init__(self):
        self.news_list = None
        self.spider = news_spider(reset=False)
        jieba.analyse.set_stop_words('./jieba/stopwords.txt')

    def get_news(self, begin=None, end=None):
        self.news_list = self.spider.get_news(begin, end)
        self.get_wordCloud()

    def get_news_list(self):
        return self.news_list

    def get_wordCloud(self):
        all = ''
        for news in self.news_list:
            text = news['title'] + news['text']
            all += text
            keywords = jieba.analyse.extract_tags(text, 5, False)
            news['keywords'] = keywords
        keywords = dict(jieba.analyse.extract_tags(all, 100, True, ['a', 'n','v']))

        w = WordCloud(font_path='msyh.ttc', background_color=None,
                      mode='RGBA', scale=10)
        w.generate_from_frequencies(keywords)
        w.to_file('cloud.png')


if __name__ == '__main__':
    data = Data()
    data.get_news('2022-1-4', '2022-1-5')
    data.get_wordCloud()

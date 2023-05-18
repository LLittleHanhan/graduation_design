import json

import numpy as np
import torch
from transformers import AutoConfig, AutoTokenizer

from news import news_spider
from wordcloud import WordCloud
import jieba
import jieba.analyse
from model.trigger_model import trigger_model
from model.role_model import role_model


class Data:
    tokenizer = AutoTokenizer.from_pretrained('./chinese-roberta-wwm-ext')
    config = AutoConfig.from_pretrained('./chinese-roberta-wwm-ext')

    trigger_model = trigger_model(config)
    trigger_model.load_state_dict(torch.load('./train_model/trigger.bin'))

    role_model = role_model(config)
    role_model.load_state_dict(torch.load('./train_model/role.bin'))

    label_path = './schema/label.txt'
    schema_path = './schema/duee_event_schema.json'
    id2label = {}
    role_dic = {}

    def __init__(self):
        self.news_list = None
        self.spider = news_spider(reset=False)
        jieba.analyse.set_stop_words('./jieba/stopwords.txt')

        with open(self.label_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                idx, label = line.strip().split(' ')
                self.id2label[int(idx)] = label
        print(self.id2label)
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                json_data = json.loads(line)
                role_list = []
                for role in json_data['role_list']:
                    role_list.append(role['role'])
                self.role_dic[json_data['event_type']] = role_list
        print(self.role_dic)

    def get_news(self, begin=None, end=None, news_class=None):
        self.news_list = self.spider.get_news(begin, end, news_class)
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
        keywords = dict(jieba.analyse.extract_tags(all, 100, True, ['a', 'n', 'v']))

        w = WordCloud(font_path='msyh.ttc', background_color=None,
                      mode='RGBA', scale=10)
        w.generate_from_frequencies(keywords)
        w.to_file('cloud.png')

    def get_trigger(self, sentence):
        # sentence = '如何看待“恒大国脚因伤退出国足后迅速在联赛复出”这个热议话题'
        self.trigger_model.eval()
        with torch.no_grad():
            inputs = self.tokenizer(sentence, truncation=True, return_tensors="pt", return_offsets_mapping=True,
                                    max_length=480)
            offsets = inputs.pop('offset_mapping').squeeze(0).tolist()
            pred = self.trigger_model(inputs)[1][0][0:-1]
            idx = 1
            event_list = []
            start_list = []
            end_list = []
            while idx < len(pred):
                if pred[idx] % 2 == 1:
                    _type = pred[idx]
                    event_list.append(self.id2label[_type].split('B-')[1])
                    start, end = offsets[idx]
                    start_list.append(start)
                    while idx + 1 < len(pred) and pred[idx + 1] == _type + 1:
                        idx += 1
                    _, end = offsets[idx]
                    end_list.append(end)
                idx += 1
        return event_list, start_list, end_list

    def get_role(self, sentence, event_list, start_list, end_list):
        # sentence = '政府企业多措并举不负所“托” 缓解职工“带娃”难题央视网消息：孩子上幼儿园前，有没有什么好的途径解决“带娃”的焦虑？早上7时30分，家住厦门的潘女士正在帮刚起床的女儿垚垚洗漱。潘女士是一位“90后”，在厦门的一家国企任职。两年前，女儿垚垚的出生。'
        # event_list = ['人生-产子/女']
        # start_list = [120]
        # end_list = [122]

        self.role_model.eval()
        with torch.no_grad():
            for index, event in enumerate(event_list):
                trigger = sentence[start_list[index]:end_list[index]]

                for role in self.role_dic[event]:
                    question = '触发词为' + trigger + '的事件' + event.split('-')[1] + '中角色' + role + '是什么？'
                    print(question)
                    inputs = self.tokenizer(question, sentence, truncation=True, return_tensors="pt", max_length=512,
                                            return_offsets_mapping=True)
                    mapping = inputs.pop('offset_mapping').squeeze(0)
                    offset = (inputs['attention_mask'] - inputs['token_type_ids']).squeeze(0).sum().item()

                    # 位置信息
                    trigger_position = np.zeros(inputs['input_ids'].shape, dtype=int)
                    trigger_start = inputs.char_to_token(start_list[index], sequence_index=1) - 1
                    trigger_end = inputs.char_to_token(end_list[index] - 1, sequence_index=1) + 1
                    second_seq_start = offset
                    second_seq_end = inputs['attention_mask'].squeeze(0).sum().item() - 2
                    count = 1
                    mark = ['。', '？', '！', '；', '?', '!', ';']
                    while trigger_start >= second_seq_start:
                        trigger_position[0][trigger_start] = count
                        if inputs.tokens()[trigger_start] in mark and count < 4:
                            count += 1
                        trigger_start -= 1
                    count = 1

                    while trigger_end <= second_seq_end:
                        trigger_position[0][trigger_end] = count
                        if inputs.tokens()[trigger_end] in mark and count < 4:
                            count += 1
                        trigger_end += 1

                    _, pred = self.role_model(inputs, torch.tensor(trigger_position))
                    pred = pred[0]
                    idx = 0
                    answer = []
                    while idx < len(pred):
                        if pred[idx] == 1:
                            start, end = mapping[idx + offset]
                            while idx + 1 < len(pred) and pred[idx + 1] == 2:
                                idx += 1
                            _, end = mapping[idx + offset]
                            answer.append(sentence[start:end])
                        idx += 1
                    print('answer is', answer)

    def get_event_info(self):
        for news in self.news_list:
            if news['platform'] == 0:
                text = news['title'] + news['text']
                event_list, start_list, end_list = self.get_trigger(text)
                if len(event_list) != 0:
                    print(text)
                    print(event_list, start_list, end_list)
                    self.get_role(text, event_list, start_list, end_list)


if __name__ == '__main__':
    data = Data()
    data.get_news(news_class=['education'])
    data.get_event_info()

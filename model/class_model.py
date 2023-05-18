from torch import nn
from transformers import BertPreTrainedModel, BertModel


class class_model(BertPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.bert = BertModel(config, add_pooling_layer=True)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(768, 9)
        self.loss_fn = nn.CrossEntropyLoss()
        self.post_init()

    def forward(self, x, label=None):
        bert_output = self.bert(**x)
        sequence_output = bert_output.pooler_output
        sequence_output = self.dropout(sequence_output)
        logits = self.classifier(sequence_output)

        loss = None
        if label is not None:
            loss = self.loss_fn(logits, label)
        return logits, loss

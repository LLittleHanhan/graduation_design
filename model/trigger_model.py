from torch import nn
from transformers import BertPreTrainedModel, BertModel
from crf import CRF


class trigger_model(BertPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.bert = BertModel(config, add_pooling_layer=False)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(768, 131)
        self.crf = CRF(131, batch_first=True)
        self.post_init()

    def forward(self, x, label=None):
        bert_output = self.bert(**x)
        sequence_output = bert_output.last_hidden_state
        sequence_output = self.dropout(sequence_output)
        logits = self.classifier(sequence_output)
        if label is not None:
            loss = -self.crf(emissions=logits,
                             tags=label, mask=x['attention_mask'], reduction="token_mean")
        else:
            loss = self.crf.decode(emissions=logits, mask=x['attention_mask'])
        return logits, loss

from collections import deque

import torch.nn as nn
from transformers import BertModel


class MetaLearner(nn.Module):
    def __init__(self, config):
        super(MetaLearner, self).__init__()
        self.encoder = BertModel.from_pretrained("bert-base-uncased")
        self.encoder.requires_grad_(False)
        # TODO: unfreeze top n layers
        for block in self.encoder.encoder.layer[-(config.unfreeze_num):]:
            for params in block.parameters():
                params.requires_grad = True

        # top_n_bert_layers = deque(
        #    self.encoder.parameters(),
        #    maxlen=config.n_layers_bert_trained)
        # for params in top_n_bert _layers:
        #   params.requires_grad = True

        n_emotions = config.num_classes

        n_bert_embed = 768
        self.emo_classifier = MLPClassifier(n_bert_embed, n_emotions)

    def forward(self, sentences):
        encoded = self.encoder(sentences)[0]
        cls_token_enc = encoded[:, 0, :]
        return self.emo_classifier(cls_token_enc)


class MLPClassifier(nn.Module):
    """
    Class for Multi-Layer Perceptron Classifier
    """
    def __init__(self, input_dim, target_dim):
        super(MLPClassifier, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, target_dim)
        )

    def forward(self, input):
        output = self.network(input)
        return output

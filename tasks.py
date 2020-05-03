import math
import pandas as pd
from models import MLPClassifier

from util import create_iters

class TaskSampler(object):
    """
    Args:
        tasks: Task's list
        freq_factors: list of sampling frequency factors by task
    """
    def __init__(self, tasks, batch_size):
        pass


class Task(object):
    """

    """
    NAME = 'TASK_NAME'
    def __init__(self):
        pass

    # TODO: allow for
    # train_iter = task.get_iter('train')
    # len(train_iter) -> returns the number of batches
    def get_iter(self, split, batch_size=16, shuffle=False, random_state=1):
        raise NotImplementedError

    def get_num_batches(self, split, batch_size=1):
        raise NotImplementedError

    def get_classifier(self):
        raise NotImplementedError


class SemEval18Task(Task):
    NAME = 'SemEval18'
    """
    Multi-labeled tweet data classified in 11 emotions: anger, anticipation,
    disgust, fear, joy, love, optimism, pessimism, sadness, surprise and trust.
    """
    def __init__(self, fn_tokenizer=None):
        self.emotions = [
            'anger', 'anticipation', 'disgust', 'fear', 'joy',
            'love', 'optimism', 'pessimism', 'sadness', 'surprise', 'trust'
        ]
        self.fn_tokenizer = fn_tokenizer
        self.splits = {}
        self.classifier = MLPClassifier(target_dim=len(self.emotions))
        for split in ['train', 'dev', 'test']:
            self.splits.setdefault(
                split,
                pd.read_table('data/semeval18_task1_class/{}.txt'.format(split)))

        # TODO:
        # - pre-process dataset

    def get_iter(self, split, batch_size=16, shuffle=False, random_state=1):
        """
        Returns an iterable over the single
        Args:
            split: train/dev/test
        Returns:
            Iterable for the specified split
        """
        assert split in ['train', 'dev', 'test']
        df = self.splits.get(split)
        ix = 0
        while ix < len(df):
            df_batch = df.iloc[ix:ix+batch_size]
            sentences = df_batch.Tweet.values
            labels = df_batch[self.emotions].values
            if self.fn_tokenizer:
                sentences = self.fn_tokenizer(list(sentences))
            yield sentences, labels
            ix += batch_size

    def get_num_batches(self, split, batch_size=1):
        assert split in ['train', 'dev', 'test']
        return math.ceil(len(self.splits.get(split))/batch_size)

    def get_classifier(self):
        return self.classifier


class SemEval18SingleEmotionTask(Task):
    """
    Serves as a single emotion tasks. It leverages the SemEval18 dataset which
    contains 11 emotions (anger, anticipation, disgust, fear, joy, love,
    optimism, pessimism, sadness, surprise and trust) creating an individual
    dataset for the single emotion task. This subset that we call single emotion
    tasks uses all the positive entries for the target emotion plus a random
    sampling of the remaining entries, creating a balanced dataset for this
    single emotion.
    """
    def __init__(self, emotion, num_samples=16):
        self.emotion = emotion
        self.num_samples = num_samples

    def get_iter(self, split, batch_size=16):
        """
        Returns an iterable over the single
        Args:
            split: train/dev/test
        Returns:
            Iterable for the specified split
        """
        assert split in ['train', 'dev', 'test']

        df = pd.read_table('data/semeval18_task1_class/{}.txt'.format(split))
        df_emotion = df[df[self.emotion] == 1]
        df_other = df[df[self.emotion] == 0].sample(df_emotion.shape[0])
        df = pd.concat([df_emotion, df_other]).sample(frac=1, random_state=1)
        ix = 0
        while ix < len(df):
            df_batch = df.iloc[ix:ix+batch_size]
            sentences = df_batch.Tweet.values
            labels = df_batch[self.emotion].values
            yield sentences, labels
            ix += batch_size


class SemEval18AngerTask(SemEval18SingleEmotionTask):
    def __init__(self):
        super(SemEval18AngerTask, self).__init__('anger')

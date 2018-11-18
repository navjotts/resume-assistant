import os
import numpy as np
from py_files.AccuracyAnalysis import AccuracyAnalysis

class SentenceClassifier(object):
    def __init__(self, name, feature_type):
        self.num_classes = 4
        self.name = name
        self.feature_type = feature_type
        self.model = None # todo should be a dict => so that we can hold more than 1 models in memory together
        self.seed = 12 # fix the random seed for consistency of results
        np.random.seed(self.seed)

    def train(self, samples, labels):
        # build the model and populate `self.labels_pred` in subclasses
        score = AccuracyAnalysis.score(self, labels, self.labels_pred)
        report = AccuracyAnalysis.report(self, labels, self.labels_pred)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, self.labels_pred, self.words_to_sents(samples))

        return {'score': score, 'report': report, 'misclassifications': misclassifications}

    # loads the model from local disk (if needed)
    def load(self):
        if not self.model:
            print('SentenceClassifier: error: unable to load model')

    def test(self, samples, labels):
        # build the model and populate `self.labels_pred` in subclasses
        score = AccuracyAnalysis.score(self, labels, self.labels_pred)
        report = AccuracyAnalysis.report(self, labels, self.labels_pred)
        confusion_matrix = AccuracyAnalysis.confusion_matrix(self, labels, self.labels_pred)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, self.labels_pred, self.words_to_sents(samples))

        return {'score': score, 'report': report, 'confusion_matrix': confusion_matrix, 'misclassifications': misclassifications}

    def classify(self, samples):
        # build the model and populate `self.labels_pred` and `self.prob_pred` in subclasses
        return list(zip(self.labels_pred, self.prob_pred))

    def words_to_sents(self, samples):
        return [(' ').join(s) for s in samples]

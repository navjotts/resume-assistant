import os
import numpy as np

from py_files.AccuracyAnalysis import AccuracyAnalysis

class SentenceClassifier(object):
    def __init__(self, name, feature_type):
        self.num_classes = 5
        self.name = name
        self.feature_type = feature_type
        self.model = None # todo should be a dict => so that we can hold more than 1 models in memory together
        self.seed = 42 # fix the random seed for consistency of results
        np.random.seed(self.seed) # todo => doesn't setting this gets rid of the need of the above? CHECK (then we don't need to set `random_state` everywhere)

    def train(self, samples, features, labels):
        # build the model and populate `self.labels_pred` in subclasses
        score = AccuracyAnalysis.score(self, labels, self.labels_pred)
        report = AccuracyAnalysis.report(self, labels, self.labels_pred)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, self.labels_pred, samples)

        return {'score': score, 'report': report, 'misclassifications': misclassifications}

    # loads the model from local disk (if needed)
    def load(self):
        if not self.model:
            print('Vectorizer: error: unable to load model')

    def test(self, samples, features, labels):
        # build the model and populate `self.labels_pred` in subclasses
        score = AccuracyAnalysis.score(self, labels, self.labels_pred)
        report = AccuracyAnalysis.report(self, labels, self.labels_pred)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, self.labels_pred, samples)

        return {'score': score, 'report': report, 'misclassifications': misclassifications}

    def classify(self, features):
        # build the model and populate `self.labels_pred` and `self.prob_pred` in subclasses
        return list(zip(self.labels_pred, self.prob_pred))
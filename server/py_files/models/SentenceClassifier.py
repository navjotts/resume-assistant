import os

from py_files.AccuracyAnalysis import AccuracyAnalysis

class SentenceClassifier(object):
    def __init__(self, name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model = None
        self.seed = 42 # fix the random seed for consistency of results

    def train(self, samples, features, labels):
        # build the model and populate `self.labels_pred` in subclasses

        print('features', features.shape)

        score = AccuracyAnalysis.score(self, labels, self.labels_pred)
        report = AccuracyAnalysis.report(self, labels, self.labels_pred)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, self.labels_pred, samples)

        print(score)
        print(report)

        return {'score': score, 'report': report, 'misclassifications': misclassifications}

    # loads the model from local (if needed)
    def load(self):
        if not self.model:
            print('Vectorizer: error: unable to load model')

    def test(self, samples, features, labels):
        # build the model and populate `self.labels_pred` in subclasses

        print('features', features.shape)

        score = AccuracyAnalysis.score(self, labels, self.labels_pred)
        report = AccuracyAnalysis.report(self, labels, self.labels_pred)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, self.labels_pred, samples)

        print(score)
        print(report)

        return {'score': score, 'report': report, 'misclassifications': misclassifications}

    def classify(self, features):
        # build the model and populate `self.labels_pred` and `self.prob_pred` in subclasses
        return list(zip(self.labels_pred, self.prob_pred))

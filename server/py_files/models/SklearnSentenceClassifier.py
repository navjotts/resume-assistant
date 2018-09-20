import os
import numpy as np
from sklearn.externals import joblib

from py_files.models.SentenceClassifier import SentenceClassifier

class SklearnSentenceClassifier(SentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)

    def words_to_sents(self, samples):
        return [(' ').join(s) for s in samples]

    def train(self, samples, features, labels):
        # create the model and in subclasses
        samples = self.words_to_sents(samples)
        self.model.fit(features, labels)
        self.labels_pred = self.model.predict(features)

        joblib.dump(self.model, self.path)

        return super().train(samples, features, labels)

    def load(self):
        if not self.model:
            self.model = joblib.load(self.path)

        super().load()

    def test(self, samples, features, labels):
        self.load()
        samples = self.words_to_sents(samples)
        self.labels_pred = self.model.predict(features)

        return super().test(samples, features, labels)

    def classify(self, features):
        self.load()
        self.labels_pred = self.model.predict(features)
        self.prob_pred = np.max(self.model.predict_proba(features), axis=1)

        return super().classify(features)
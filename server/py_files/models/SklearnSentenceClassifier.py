import os
import numpy as np
import pickle

from py_files.models.SentenceClassifier import SentenceClassifier
from py_files.models.Vectorizer.Vectorizer import Vectorizer
from py_files.models.Embeddings.Embeddings import Embeddings

class SklearnSentenceClassifier(SentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)

    def train(self, samples, labels):
        # create the model and in subclasses
        features = self.choose_features(samples, True)
        self.model.fit(features, labels)
        self.labels_pred = self.model.predict(features)

        pickle.dump(self.model, open(self.path, 'wb'))

        return super().train(samples, labels)

    def load(self):
        if not self.model:
            self.model = pickle.load(open(self.path, 'rb'))

        super().load()

    def test(self, samples, labels):
        self.load()
        features = self.choose_features(samples)
        self.labels_pred = self.model.predict(features)

        return super().test(samples, labels)

    def classify(self, samples):
        self.load()
        features = self.choose_features(samples)
        self.labels_pred = self.model.predict(features)
        self.prob_pred = np.max(self.model.predict_proba(features), axis=1)

        return super().classify(samples)

    def choose_features(self, samples, retrain=False):
        if self.feature_type in ['tf-idf', 'bow']:
            return Vectorizer(self.name, self.feature_type).vectors(samples, retrain).toarray()
        elif self.feature_type == 'word-embeddings':
            return Embeddings(self.name, 100).encode_samples(samples)
        else:
            return samples # no change/manipulation
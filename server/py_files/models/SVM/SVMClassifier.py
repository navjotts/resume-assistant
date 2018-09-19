import os
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.externals import joblib

from py_files.models.SentenceClassifier import SentenceClassifier

class SVMClassifier(SentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type + '.pkl')

    def process_samples(self, samples):
        return [(' ').join(s) for s in samples]

    def train(self, samples, features, labels):
        samples = self.process_samples(samples)

        self.model = LinearSVC(random_state=self.seed, class_weight='balanced', tol=.00001, max_iter=5000) # todo Cross Valdiation
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
        samples = self.process_samples(samples)
        self.labels_pred = self.model.predict(features)

        return super().test(samples, features, labels)

    def classify(self, features):
        self.load()
        self.labels_pred = self.model.predict(features)
        self.prob_pred = np.max(self.model.predict_proba(features), axis=1)
        return super().classify(features)
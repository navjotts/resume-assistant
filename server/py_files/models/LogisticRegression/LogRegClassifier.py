import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

from py_files.models.SentenceClassifier import SentenceClassifier

class LogRegClassifier(SentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type + '.pkl')

    def train(self, samples, features, labels):
        # todo using the default LogReg (check options which is the most suited for multi-class case)
        # http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
        self.model = LogisticRegression(random_state=42) # todo place random_state in the parent class
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
        self.labels_pred = self.model.predict(features)

        return super().test(samples, features, labels)

    def classify(self, features):
        self.load()
        self.labels_pred = self.model.predict(features)
        self.prob_pred = np.max(self.model.predict_proba(features), axis=1)
        return super().classify(features)
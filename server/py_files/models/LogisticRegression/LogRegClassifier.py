import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

from py_files.AccuracyAnalysis import AccuracyAnalysis

class LogRegClassifier(object):
    def __init__(self, name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type + '.pkl')
        self.model = None

    def train(self, samples, features, labels):
        print('features', features.shape)

        # todo using the default LogReg (check options which is the most suited for multi-class case)
        # http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
        self.model = LogisticRegression(random_state=42) # todo place random_state in the parent class
        self.model.fit(features, labels)
        labels_pred = self.model.predict(features)

        score = AccuracyAnalysis.score(self, labels, labels_pred)
        report = AccuracyAnalysis.report(self, labels, labels_pred)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, labels_pred, samples)

        print(score)
        print(report)

        joblib.dump(self.model, self.path)
        return {'score': score, 'report': report, 'misclassifications': misclassifications}

    # loads the model from local (if needed)
    def load(self):
        if not self.model:
            self.model = joblib.load(self.path)

        if not self.model:
            print('Vectorizer: error: unable to load model')

    def test(self, samples, features, labels):
        print('features', features.shape)

        self.load()
        labels_pred = self.model.predict(features)

        score = AccuracyAnalysis.score(self, labels, labels_pred)
        report = AccuracyAnalysis.report(self, labels, labels_pred)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, labels_pred, samples)

        print(score)
        print(report)

        return {'score': score, 'report': report, 'misclassifications': misclassifications}

    def classify(self, features):
        self.load()
        labels_pred = self.model.predict(features)
        prob_pred = np.max(self.model.predict_proba(features), axis=1)

        return list(zip(labels_pred, prob_pred))





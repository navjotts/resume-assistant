import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

from py_files.models.SklearnSentenceClassifier import SklearnSentenceClassifier

class LogRegClassifier(SklearnSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type + '.pkl')

    def train(self, samples, features, labels):
        # todo using the default LogReg (check options which is the most suited for multi-class case)
        # http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
        self.model = LogisticRegression(random_state=self.seed)
        return super().train(samples, features, labels)
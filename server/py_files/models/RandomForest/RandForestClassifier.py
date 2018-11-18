import os
from sklearn.ensemble import RandomForestClassifier
from py_files.models.SklearnSentenceClassifier import SklearnSentenceClassifier

class RandForestClassifier(SklearnSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type + '.pkl')

    def train(self, samples, labels):
        self.model = RandomForestClassifier(random_state=self.seed, max_depth=110, n_estimators=150) # todo Cross Valdiation
        return super().train(samples, labels)
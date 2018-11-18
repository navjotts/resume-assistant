import os
from sklearn.svm import LinearSVC
from py_files.models.SklearnSentenceClassifier import SklearnSentenceClassifier

class SVMClassifier(SklearnSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type + '.pkl')

    def train(self, samples, labels):
        self.model = LinearSVC(random_state=self.seed, class_weight='balanced', tol=.00001, max_iter=5000) # todo Cross Valdiation
        return super().train(samples, labels)
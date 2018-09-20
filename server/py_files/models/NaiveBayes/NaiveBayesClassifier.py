import os

from sklearn.naive_bayes import MultinomialNB

from py_files.models.SklearnSentenceClassifier import SklearnSentenceClassifier

class NaiveBayesClassifier(SklearnSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type + '.pkl')

    def train(self, samples, features, labels):
        self.model = MultinomialNB() # todo Cross Valdiation
        return super().train(samples, features, labels)
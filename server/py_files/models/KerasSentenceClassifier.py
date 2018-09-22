import os
import keras
from keras.models import load_model

from py_files.models.SentenceClassifier import SentenceClassifier
from py_files.models.Vectorizer.Vectorizer import Vectorizer
from py_files.models.Embeddings.Embeddings import Embeddings

class KerasSentenceClassifier(SentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)

    def train(self, samples, labels):
        # create the model and in subclasses
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.model.save(self.path + '/model_weights.h5')
        print('Saved model to disk...')
        return super().train(samples, labels)

        # todo consolidate with AccuracyAnalysis => super().train()
        return self.accuracy

    def load(self):
        if not self.model:
            self.model = load_model(self.path + '/model_weights.h5')
            print('Loaded model from disk...')
            print(self.path)

        super().load()

    def test(self, samples, labels):
        return super().train(samples, labels)

        # todo consolidate with AccuracyAnalysis => super().train()
        return self.accuracy

    def classify(self, samples):
        return super().classify(samples)

    def choose_features(self, samples, retrain=False):
        if self.feature_type in ['tf-idf', 'bow']:
            return Vectorizer(self.name, self.feature_type).vectors(samples, retrain).todense()
        elif self.feature_type == 'word-embeddings':
            return Embeddings(self.name, 100).encode_samples(samples)
        else:
            return samples # no change/manipulation
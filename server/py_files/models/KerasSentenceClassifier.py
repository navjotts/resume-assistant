import os
import keras
from keras.models import model_from_json, load_model
import simplejson

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

        # with open(os.path.join(self.path, 'config.json'), "w") as f:
        #     f.write(simplejson.dumps(simplejson.loads(self.model.to_json()), indent=4))

        # self.model.save_weights(os.path.join(self.path, 'model_weights.h5'))
        self.model.save(self.path + '/model_weights.h5')
        print('Saved model to disk...')

        # todo consolidate with AccuracyAnalysis => super().train()
        return self.accuracy

    def load(self):
        if not self.model:
            # json_file = open(os.path.join(self.path, 'config.json'), 'r')
            # loaded_model_json = json_file.read()
            # json_file.close()
            # loaded_model = model_from_json(loaded_model_json)

            # loaded_model.load_weights(os.path.join(self.path, 'model_weights.h5'))
            self.model = load_model(self.path + '/model_weights.h5')
            print('Loaded model from disk...')
            print(self.path)

        super().load()

    def test(self, samples, labels):
        # todo consolidate with AccuracyAnalysis => super().test()
        return self.accuracy

    def classify(self, samples):
        return super().classify(samples)

    def choose_features(self, samples, retrain):
        if self.feature_type in ['tf-idf', 'bow']:
            return Vectorizer(self.name, self.feature_type).vectors(samples, retrain).todense()
        elif self.feature_type == 'word-embeddings':
            return Embeddings(self.name, 100).encode_samples(samples)
        else:
            return samples # no change/manipulation
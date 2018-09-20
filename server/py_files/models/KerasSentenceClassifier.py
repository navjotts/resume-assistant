import os
import keras
from keras.models import model_from_json
import simplejson

from py_files.models.SentenceClassifier import SentenceClassifier

class KerasSentenceClassifier(SentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)

    def train(self, samples, features, labels):
        # create the model and in subclasses
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        with open(os.path.join(self.path, 'config.json'), "w") as f:
            f.write(simplejson.dumps(simplejson.loads(self.model.to_json()), indent=4))

        self.model.save_weights(os.path.join(self.path, 'model_weights.h5'))
        print('Saved model to disk...')

        # todo consolidate with AccuracyAnalysis => super().train()
        return self.accuracy

    def load(self):
        if not self.model:
            json_file = open(os.path.join(self.path, 'config.json'), 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            loaded_model = model_from_json(loaded_model_json)

            loaded_model.load_weights(os.path.join(self.path, 'model_weights.h5'))
            self.model = loaded_model
            print('Loaded model from disk...')
            print(self.path)

        super().load()

    def test(self, samples, features, labels):
        # todo consolidate with AccuracyAnalysis => super().test()
        return self.accuracy

    def classify(self, features):
        return super().classify(features)
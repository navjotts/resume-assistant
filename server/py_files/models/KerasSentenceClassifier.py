import os
import keras
from keras.models import load_model
from keras.layers import Embedding
from keras.preprocessing.sequence import pad_sequences

from py_files.models.Vectorizer.Vectorizer import Vectorizer
from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.SentenceLabelEncoder import SentenceLabelEncoder
from py_files.models.SentenceClassifier import SentenceClassifier

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

    def load(self):
        if not self.model:
            self.model = load_model(self.path + '/model_weights.h5')
            print('Loaded model from disk...')
            print(self.path)

        super().load()

    def test(self, samples, labels):
        self.load()
        features = self.choose_features(samples)

        if self.feature_type == 'word-embeddings':
            x_test = pad_sequences(features, maxlen=self.max_len, padding='post')
        elif self.feature_type in ['tf-idf', 'bow']:
            x_test = features
        else:
            raise Exception('Please select a valid feature')

        y_test = SentenceLabelEncoder().encode_categorical(labels)

        loss, accuracy = self.model.evaluate(x_test, y_test)
        print('loss, accuracy:', loss, accuracy)

        self.labels_pred = SentenceLabelEncoder().decode(self.model.predict_classes(x_test))

        return super().test(samples, labels)

    def classify(self, samples):
        return super().classify(samples)

    def choose_features(self, samples, retrain=False):
        if self.feature_type in ['tf-idf', 'bow']:
            return Vectorizer(self.name, self.feature_type).vectors(samples, retrain).todense()
        elif self.feature_type == 'word-embeddings':
            return Embeddings(self.name, 100).encode_samples(samples)
        else:
            return samples # no change/manipulation

    def embedding_layer(self, embedding_size, trainable, features):
        embedding_layer = None
        if self.feature_type == 'word-embeddings':
            x_train = pad_sequences(features, maxlen=self.max_len, padding='post')
            pretrained_embeddings = Embeddings(self.name, embedding_size).vectors()
            vocab_size = pretrained_embeddings.shape[0]
            embedding_layer = Embedding(input_dim=vocab_size, output_dim=embedding_size,
                                input_length=self.max_len, trainable=trainable, weights=[pretrained_embeddings])
        elif self.feature_type in ['tf-idf', 'bow']:
            x_train = features
            vocab_size = x_train.shape[1]
            embedding_layer = Embedding(input_dim=vocab_size, output_dim=embedding_size,
                                input_length=vocab_size, trainable=trainable)
        else:
            raise Exception('Please select a valid feature')

        return embedding_layer, x_train
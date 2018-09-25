import os
import sys
import numpy as np

from keras.models import Sequential
from keras.optimizers import adam
from keras.layers import LSTM, Dense, Dropout, Embedding, Conv1D, MaxPool1D, Flatten
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from sklearn.utils import class_weight

from py_files.models.SentenceLabelEncoder import SentenceLabelEncoder
from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.KerasSentenceClassifier import KerasSentenceClassifier

class CNNClassifier(KerasSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type)
        self.max_len = 100

    def train(self, samples, labels):
        features = self.choose_features(samples, True)

        embedding_size = 100
        embedding_layer = None
        if self.feature_type == 'word-embeddings':
            x_train = pad_sequences(features, maxlen=self.max_len, padding='post')
            pretrained_embeddings = Embeddings(self.name, embedding_size).vectors()
            vocab_size = pretrained_embeddings.shape[0]
            embedding_layer = Embedding(input_dim=vocab_size, output_dim=embedding_size,
                                input_length=self.max_len, trainable=True, weights=[pretrained_embeddings])
        elif self.feature_type in ['tf-idf', 'bow']:
            x_train = features
            vocab_size = x_train.shape[1]
            embedding_layer = Embedding(input_dim=vocab_size, output_dim=embedding_size,
                                input_length=vocab_size, trainable=True)
        else:
            raise Exception('Please select a valid feature')

        self.model = self.vanilla_CNN(embedding_layer)

        numeric_labels = SentenceLabelEncoder().encode_numerical(labels)
        class_weights = class_weight.compute_class_weight('balanced', np.unique(numeric_labels), numeric_labels)
        y_train = SentenceLabelEncoder().encode_categorical(labels)

        self.model.fit(x_train, y_train, validation_split=0.2, epochs=20, batch_size=128,
                        verbose=2, shuffle=True, class_weight=class_weights)
        loss, accuracy = self.model.evaluate(x_train, y_train)
        print('loss, accuracy:', loss, accuracy)

        self.labels_pred = SentenceLabelEncoder().decode(self.model.predict_classes(x_train))

        return super().train(samples, labels)

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
        self.load()
        features = self.choose_features(samples)
        # todo
        return super().classify(samples)

    def experimental_CNN(self, embedding_layer):
        model = Sequential()
        model.add(embedding_layer)
        model.add(Conv1D(filters=256, kernel_size=5, strides=4, padding='valid', activation='relu', data_format='channels_first'))
        model.add(MaxPool1D(pool_size=5))
        model.add(Dropout(rate=0.3))
        model.add(Conv1D(filters=128, kernel_size=5, strides=2, padding='valid', activation='relu', data_format='channels_first'))
        model.add(MaxPool1D(pool_size=50))
        model.add(Flatten())
        model.add(Dense(units=64, activation='relu'))
        model.add(Dropout(rate=0.5))
        model.add(Dense(units=32, activation='relu'))
        model.add(Dropout(rate=0.5))
        model.add(Dense(units=self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
        print(model.summary())

        return model

    def vanilla_CNN(self, embedding_layer):
        model = Sequential()
        model.add(embedding_layer)
        model.add(Conv1D(filters=256, kernel_size=5, padding='same', activation='relu'))
        model.add(MaxPool1D(pool_size=5))
        model.add(Dropout(rate=0.3))
        model.add(Flatten())
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
        print(model.summary())

        return model
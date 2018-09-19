import os
import numpy as np

from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Embedding
from keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical

from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.KerasSentenceClassifier import KerasSentenceClassifier

class LSTMClassifier(KerasSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type)

    def train(self, samples, features, labels):
        max_length = max([len(s) for s in samples]) # todo think: might be a costly step if huge data, may be it should just be a constant (100)
        x_train = pad_sequences(features, maxlen=100, padding='post')

        embedding_vecs = Embeddings(self.name, 100).vectors()
        vocab_size = embedding_vecs.shape[0]

        model = Sequential()
        model.add(Embedding(vocab_size ,100, input_length = 100, trainable =True, weights = [embedding_vecs] ))
        model.add(LSTM(50))
        model.add(Dense(32, activation='relu'))
        model.add(Dropout(0.3))
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        self.model = model

        numeric_labels = LabelEncoder().fit_transform(labels)
        y_train = to_categorical(numeric_labels, self.num_classes)

        self.model.fit(x_train, y_train, epochs=100, batch_size=128, verbose=1)
        loss, self.accuracy = self.model.evaluate(x_train, y_train)
        print('accuracy:', self.accuracy)

        return super().train(samples, features, labels)

    def test(self, samples, features, labels):
        self.load()

        max_length = max([len(s) for s in samples]) # todo think: might be a costly step if huge data, may be it should just be a constant (100)
        x_test = pad_sequences(features, maxlen=max_length, padding='post')

        numeric_labels = LabelEncoder().fit_transform(labels)
        y_test = to_categorical(numeric_labels, self.num_classes)

        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        loss, self.accuracy = self.model.evaluate(x_test, y_test)
        print('accuracy:', self.accuracy)

        # self.labels_pred = self.model.predict(x_test)
        # print(self.labels_pred)
        # return super().test(samples, features, labels)

        return super().test(samples, features, labels)

    def classify(self, features):
        # todo
        pass
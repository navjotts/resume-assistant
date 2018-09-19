import os
import numpy as np

from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder

from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.KerasSentenceClassifier import KerasSentenceClassifier

class LSTMClassifier(KerasSentenceClassifier):
    def __init__(self, name, feature_type):
        self.num_classes = 5
        self.name = name
        self.feature_type = feature_type
        self.model = None # todo should be a dict => so that we can hold more than 1 models in memory together
        self.seed = 42 # fix the random seed for consistency of results
        np.random.seed(self.seed)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type)

    def train(self, samples, features, labels):
        max_length = 100 # todo change
        x_train = pad_sequences(features, maxlen=max_length, padding='post')

        model = Sequential()
        model.add(Embeddings(self.name, 100).keras_embeddings_layer())
        model.add(LSTM(100))
        model.add(Dropout(0.2))
        model.add(Dense(32, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        self.model = model

        numeric_labels = LabelEncoder().fit_transform(labels)
        y_train = to_categorical(numeric_labels, self.num_classes)

        self.model.fit(x_train, y_train, epochs=3, batch_size=32, verbose=2)
        loss, self.accuracy = self.model.evaluate(x_train, y_train)
        print('accuracy:', self.accuracy)

        return super().train(samples, features, labels)

    def test(self, samples, features, labels):
        self.load()

        max_length = 100 # todo change
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
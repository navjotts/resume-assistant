import os
import numpy as np

from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Embedding
from keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from sklearn.utils import class_weight

from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.KerasSentenceClassifier import KerasSentenceClassifier

class LSTMClassifier(KerasSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type)

    def train(self, samples, labels):
        features = self.choose_features(samples, True)
        model = Sequential()

        embedding_size = 100
        if self.feature_type == 'word-embeddings':
            x_train = pad_sequences(features, maxlen=100, padding='post')
            pretrained_embeddings = Embeddings(self.name, embedding_size).vectors()
            vocab_size = pretrained_embeddings.shape[0]
            model.add(Embedding(input_dim=vocab_size, output_dim=embedding_size, weights=[pretrained_embeddings]))
        elif self.feature_type in ['tf-idf', 'bow']:
            x_train = features
            vocab_size = x_train.shape[1]
            model.add(Embedding(input_dim=vocab_size, output_dim=embedding_size, trainable=True))
        else:
            raise Exception('Please select a valid feature')

        model.add(LSTM(50))
        model.add(Dense(16, activation='relu'))
        model.add(Dropout(0.3))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        self.model = model

        numeric_labels = LabelEncoder().fit_transform(labels)

        class_weights = class_weight.compute_class_weight('balanced',
                                                 np.unique(numeric_labels),
                                                 numeric_labels)

        y_train = to_categorical(numeric_labels, self.num_classes)

        self.model.fit(x_train, y_train, validation_split=0.2, epochs=20, batch_size=128, verbose=2, shuffle=True, class_weight=class_weights)
        loss, self.accuracy = self.model.evaluate(x_train, y_train)
        print('accuracy:', self.accuracy)

        return super().train(samples, labels)

    def test(self, samples, labels):
        self.load()
        features = self.choose_features(samples)

        if(self.feature_type != 'word-embeddings'):
            raise Exception('LSTM model is only configured for word-embeddings at the moment please train wiht word embeddings')

        x_test = pad_sequences(features, maxlen=100, padding='post')

        numeric_labels = LabelEncoder().fit_transform(labels)
        y_test = to_categorical(numeric_labels, self.num_classes)

        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        loss, self.accuracy = self.model.evaluate(x_test, y_test)
        print('accuracy:', self.accuracy)

        # self.labels_pred = self.model.predict(x_test)
        # print(self.labels_pred)
        # return super().test(samples, labels)

        return super().test(samples, labels)

    def classify(self, samples):
        self.load()
        features = self.choose_features(samples)
        # todo
        return super().classify(samples)
import os
import numpy as np

from keras.models import Sequential
from keras.optimizers import adam
from keras.layers import LSTM, Dense, Dropout, Embedding, Conv1D, MaxPool1D, Flatten
from keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from sklearn.utils import class_weight

from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.KerasSentenceClassifier import KerasSentenceClassifier

class CNNClassifier(KerasSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type)

    def train(self, samples, labels):
        features = self.choose_features(samples, True)

        if(self.feature_type != 'word-embeddings'):
            raise Exception('CNN model is only configured for word-embeddings at the moment please train wiht word embeddings')

        x_train = pad_sequences(features, maxlen=100, padding='post')

        embedding_vecs = Embeddings(self.name, 100).vectors()
        vocab_size = embedding_vecs.shape[0]


        model = Sequential()
        model.add(Embedding(vocab_size,100,input_length = 100, trainable =True, weights = [embedding_vecs] ))
        model.add(Conv1D(256, 5, activation='relu',data_format='channels_first', padding = 'valid', strides = 4))
        model.add(MaxPool1D(5))
        model.add(Dropout(0.3))
        model.add(Conv1D(128, 5, activation='relu',data_format='channels_first',padding = 'valid', strides = 2))
        model.add(MaxPool1D(50))
        model.add(Flatten())
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(32, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(5, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
        print(model.summary())
        self.model = model

        numeric_labels = LabelEncoder().fit_transform(labels)

        class_weights = class_weight.compute_class_weight('balanced',
                                            np.unique(numeric_labels),
                                            numeric_labels)

        y_train = to_categorical(numeric_labels, self.num_classes)

        self.model.fit(x_train, y_train, validation_split=0.2, epochs=200, batch_size=128, verbose=1, shuffle=True, class_weight=class_weights)
        loss, self.accuracy = self.model.evaluate(x_train, y_train)
        print('accuracy:', self.accuracy)

        return super().train(samples, labels)

    def test(self, samples, labels):
        self.load()
        features = self.choose_features(samples)

        if(self.feature_type != 'word-embeddings'):
            raise Exception('CNN model is only configured for word-embeddings at the moment please train wiht word embeddings')

        x_test = pad_sequences(features, maxlen=100, padding='post')

        numeric_labels = LabelEncoder().fit_transform(labels)
        y_test = to_categorical(numeric_labels, self.num_classes)

        optimizer = adam(lr=0.001)

        self.model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
        loss, self.accuracy = self.model.evaluate(x_test, y_test)
        print('accuracy:', self.accuracy)

        # self.labels_pred = self.model.predict(x_test)
        # print(self.labels_pred)
        # return super().test(samples, features, labels)

        return super().test(samples, labels)

    def classify(self, samples):
        self.load()
        features = self.choose_features(samples)
        # todo
        return super().classify(samples)
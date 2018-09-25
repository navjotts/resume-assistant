import os
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Embedding
from keras.preprocessing.sequence import pad_sequences
from keras.optimizers import adam
from sklearn.utils import class_weight

from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.KerasSentenceClassifier import KerasSentenceClassifier
from py_files.models.SentenceLabelEncoder import SentenceLabelEncoder

class NeuralNetClassifier(KerasSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type)
        self.max_len = 100

    def train(self, samples, labels):
        features = self.choose_features(samples, True)

        # self.train_experimental_NN(features=features, labels=labels, trainable_embeddings=True)
        self.train_vanilla_NN(features=features, labels=labels, trainable_embeddings=True)

        return super().train(samples, labels)

    # todo shift to KerasSentenceClassifier
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

    def train_vanilla_NN(self, features, labels, trainable_embeddings):
        model = Sequential()
        embedding_size = 100
        if self.feature_type == 'word-embeddings':
            x_train = pad_sequences(features, maxlen=self.max_len, padding='post')
            pretrained_embeddings = Embeddings(self.name, embedding_size).vectors()
            vocab_size = pretrained_embeddings.shape[0]
            model.add(Embedding(input_dim=vocab_size, output_dim=embedding_size,
                                input_length=self.max_len, trainable=trainable_embeddings, weights=[pretrained_embeddings]))
            model.add(Flatten())
            model.add(Dense(units=4*embedding_size, activation='relu'))
        elif self.feature_type in ['tf-idf', 'bow']:
            x_train = features
            vocab_size = x_train.shape[1]
            model.add(Dense(units=4*embedding_size, activation='relu', input_dim=vocab_size))
        else:
            raise Exception('Please select a valid feature')

        model.add(Dropout(rate=0.5))
        model.add(Dense(units=self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        self.model = model

        numeric_labels = SentenceLabelEncoder().encode_numerical(labels)
        class_weights = class_weight.compute_class_weight('balanced', np.unique(numeric_labels), numeric_labels)
        y_train = SentenceLabelEncoder().encode_categorical(labels)

        self.model.fit(x_train, y_train, validation_split=0.2, epochs=10, batch_size=32,
                        verbose=2, shuffle=True, class_weight=class_weights)
        loss, accuracy = self.model.evaluate(x_train, y_train)
        print('loss, accuracy:', loss, accuracy)

        self.labels_pred = SentenceLabelEncoder().decode(self.model.predict_classes(x_train))

    def train_experimental_NN(self, features, labels, trainable_embeddings):
        model = Sequential()
        embedding_size = 100
        if self.feature_type == 'word-embeddings':
            x_train = pad_sequences(features, maxlen=self.max_len, padding='post')
            pretrained_embeddings = Embeddings(self.name, embedding_size).vectors()
            vocab_size = pretrained_embeddings.shape[0]
            model.add(Embedding(input_dim=vocab_size, output_dim=embedding_size,
                                input_length=self.max_len, trainable=trainable_embeddings, weights=[pretrained_embeddings]))
            model.add(Flatten())
            model.add(Dense(units=64, activation='relu'))
        elif self.feature_type in ['tf-idf', 'bow']:
            x_train = features
            vocab_size = x_train.shape[1]
            model.add(Dense(units=128, activation='relu', input_dim=vocab_size)) # todo discuss - no embeddings?
        else:
            raise Exception('Please select a valid feature')

        model.add(Dropout(rate=0.5))
        model.add(Dense(units=64, activation='relu'))
        model.add(Dense(units=16, activation='relu'))
        model.add(Dropout(rate=0.4))
        model.add(Dense(units=self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        self.model = model

        numeric_labels = SentenceLabelEncoder().encode_numerical(labels)
        class_weights = class_weight.compute_class_weight('balanced', np.unique(numeric_labels), numeric_labels)
        y_train = SentenceLabelEncoder().encode_categorical(labels)

        self.model.fit(x_train, y_train, validation_split=0.2, epochs=10, batch_size=2,
                        verbose=2, shuffle=True, class_weight=class_weights)
        loss, accuracy = self.model.evaluate(x_train, y_train)
        print('loss, accuracy:', loss, accuracy)

        self.labels_pred = SentenceLabelEncoder().decode(self.model.predict_classes(x_train))
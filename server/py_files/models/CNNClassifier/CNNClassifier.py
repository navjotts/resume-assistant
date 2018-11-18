import os
import sys

import numpy as np
from keras.models import Sequential
from keras.optimizers import adam
from keras.layers import LSTM, Dense, Dropout, Embedding, Conv1D, MaxPool1D, Flatten, Input, concatenate
from keras.models import Model
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from sklearn.utils import class_weight

from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.SentenceLabelEncoder import SentenceLabelEncoder
from py_files.models.KerasSentenceClassifier import KerasSentenceClassifier

class CNNClassifier(KerasSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type)
        self.max_len = 100

    def train(self, samples, labels):
        features = self.choose_features(samples, True)

        # self.train_experimental_CNN(features=features, labels=labels, trainable_embeddings=True)
        # self.train_vanilla_CNN(features=features, labels=labels, trainable_embeddings=False) # f1 0.85 cross_valwith frozen word_embeddings on cross_val
        self.train_common_baseline_CNN(features=features, labels=labels, trainable_embeddings=False)

        return super().train(samples, labels)

    def classify(self, samples):
        self.load()
        features = self.choose_features(samples)
        # todo
        return super().classify(samples)

    def train_vanilla_CNN(self, features, labels, trainable_embeddings):
        embedding_size = 100

        if self.feature_type == 'word-embeddings':
            x_train = pad_sequences(features, maxlen=self.max_len, padding='post')
            pretrained_embeddings = Embeddings(self.name, embedding_size).vectors()
            vocab_size = pretrained_embeddings.shape[0]
            embedding_layer = Embedding(input_dim=vocab_size, output_dim=embedding_size,
                                input_length=self.max_len, trainable=trainable_embeddings, weights=[pretrained_embeddings])
        elif self.feature_type in ['tf-idf', 'bow']:
            x_train = features
            vocab_size = x_train.shape[1]
            embedding_layer = Embedding(input_dim=vocab_size, output_dim=embedding_size,
                                input_length=vocab_size, trainable=trainable_embeddings)
        else:
            raise Exception('Please select a valid feature')

        model = Sequential()
        model.add(embedding_layer)
        model.add(Conv1D(filters=256, kernel_size=5, padding='same', activation='relu'))
        model.add(MaxPool1D(pool_size=5))
        model.add(Dropout(rate=0.3))
        model.add(Flatten())
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
        print(model.summary())
        self.model = model

        numeric_labels = SentenceLabelEncoder().encode_numerical(labels)
        class_weights = class_weight.compute_class_weight('balanced', np.unique(numeric_labels), numeric_labels)
        y_train = SentenceLabelEncoder().encode_categorical(labels)

        self.model.fit(x_train, y_train, validation_split=0.2, epochs=15, batch_size=128,
                        verbose=2, shuffle=True, class_weight=class_weights)
        print('##########################\n\n\t Cross Validation completed \n\n\t##########################')

        self.model.fit(x_train, y_train, epochs=15, batch_size=128,
                        verbose=2, shuffle=True, class_weight=class_weights)
        loss, accuracy = self.model.evaluate(x_train, y_train)
        print('loss, accuracy:', loss, accuracy)

        self.labels_pred = SentenceLabelEncoder().decode(self.model.predict_classes(x_train))

    def train_experimental_CNN(self, features, labels, trainable_embeddings):
        embedding_size = 100

        if self.feature_type == 'word-embeddings':
            x_train = pad_sequences(features, maxlen=self.max_len, padding='post')
            pretrained_embeddings = Embeddings(self.name, embedding_size).vectors()
            vocab_size = pretrained_embeddings.shape[0]
            embedding_layer = Embedding(input_dim=vocab_size, output_dim=embedding_size,
                                input_length=self.max_len, trainable=trainable_embeddings, weights=[pretrained_embeddings])
        elif self.feature_type in ['tf-idf', 'bow']:
            x_train = features
            vocab_size = x_train.shape[1]
            embedding_layer = Embedding(input_dim=vocab_size, output_dim=embedding_size,
                                input_length=vocab_size, trainable=trainable_embeddings)
        else:
            raise Exception('Please select a valid feature')

        model = Sequential()
        model.add(embedding_layer)
        model.add(Conv1D(filters=256, kernel_size=5, activation='relu'))
        model.add(MaxPool1D(pool_size=5)) # output size 20 (self.max_len/5) (MaxPool acts on the input dimension/size)
        model.add(Dropout(rate=0.3))
        model.add(Conv1D(filters=128, kernel_size=5, activation='relu'))
        model.add(MaxPool1D(pool_size=15)) # filter of size 5 applied on the size 20 output of 1st MaxPool1D
        model.add(Flatten())
        model.add(Dense(units=64, activation='relu'))
        model.add(Dropout(rate=0.5))
        model.add(Dense(units=32, activation='relu'))
        model.add(Dropout(rate=0.5))
        model.add(Dense(units=self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
        print(model.summary())
        self.model = model

        numeric_labels = SentenceLabelEncoder().encode_numerical(labels)
        class_weights = class_weight.compute_class_weight('balanced', np.unique(numeric_labels), numeric_labels)
        y_train = SentenceLabelEncoder().encode_categorical(labels)

        self.model.fit(x_train, y_train, validation_split=0.2, epochs=20, batch_size=128,
                        verbose=2, shuffle=True, class_weight=class_weights)
        print('##########################\n\n\t Cross Validation completed \n\n\t##########################')

        self.model.fit(x_train, y_train, epochs=20, batch_size=128,
                        verbose=2, shuffle=True, class_weight=class_weights)
        loss, accuracy = self.model.evaluate(x_train, y_train)
        print('loss, accuracy:', loss, accuracy)

        self.labels_pred = SentenceLabelEncoder().decode(self.model.predict_classes(x_train))

    # https://machinelearningmastery.com/best-practices-document-classification-deep-learning/
    # todo either convert this to use Keras' non-functional API, or update other functions
    def train_common_baseline_CNN(self, features, labels, trainable_embeddings):
        embedding_size = 100

        x_train = pad_sequences(features, maxlen=self.max_len, padding='post')
        pretrained_embeddings = Embeddings(self.name, embedding_size).vectors()
        vocab_size = pretrained_embeddings.shape[0]
        embedding_layer = Embedding(input_dim=vocab_size, output_dim=embedding_size,
                            input_length=self.max_len, trainable=trainable_embeddings, weights=[pretrained_embeddings])

        main_input = Input(shape=(self.max_len, ))
        x = embedding_layer(main_input)
        x3 = Conv1D(filters=100, kernel_size=2, activation='relu')(x) # generalization of bigrams
        x4 = Conv1D(filters=100, kernel_size=4, activation='relu')(x) # generalization of ngrams, n=4
        x5 = Conv1D(filters=100, kernel_size=5, activation='relu')(x) # generalization of ngrams, n=5
        x3 = MaxPool1D(pool_size=99)(x3)
        x4 = MaxPool1D(pool_size=97)(x4)
        x5 = MaxPool1D(pool_size=96)(x5)
        out = concatenate([x3, x4, x5])
        out = Dropout(rate=0.5)(out)
        out = Flatten()(out) # todo - check should we use a Dense (fully connected layer)?
        main_output = Dense(self.num_classes, activation='softmax')(out)
        model = Model(inputs=main_input, outputs=main_output)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
        print(model.summary())
        self.model = model

        numeric_labels = SentenceLabelEncoder().encode_numerical(labels)
        class_weights = class_weight.compute_class_weight('balanced', np.unique(numeric_labels), numeric_labels)
        y_train = SentenceLabelEncoder().encode_categorical(labels)

        self.model.fit(x_train, y_train, validation_split=0.2, epochs=30, batch_size=128,
                        verbose=2, shuffle=True, class_weight=class_weights)
        print('##########################\n\n\t Cross Validation completed \n\n\t##########################')

        self.model.fit(x_train, y_train, epochs=30, batch_size=128,
                        verbose=2, shuffle=True, class_weight=class_weights)
        loss, accuracy = self.model.evaluate(x_train, y_train)
        print('loss, accuracy:', loss, accuracy)

        self.labels_pred = SentenceLabelEncoder().decode(np.argmax(self.model.predict(x_train), axis=1))
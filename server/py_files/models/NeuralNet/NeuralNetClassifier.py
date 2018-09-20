import os
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Embedding
from keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical

from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.KerasSentenceClassifier import KerasSentenceClassifier

class NeuralNetClassifier(KerasSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type)

    def train(self, samples, features, labels):
        #not sure we can use this max length if the length is diff than trained model is expecting then it will crash
        # max_length = max([len(s) for s in samples]) # todo think: might be a costly step if huge data, may be it should just be a constant (100)
        x_train = pad_sequences(features, maxlen=100, padding='post')



        model = Sequential()
        if(self.feature_type == 'word-embeddings'):
            embedding_vecs = Embeddings(self.name, 100).vectors()
            vocab_size = embedding_vecs.shape[0]
            model.add(Embedding(vocab_size,100,input_length = 100, trainable =True, weights = [embedding_vecs] ))
            model.add(Flatten())
            model.add(Dense(128, activation='relu'))
        else:
            model.add(Dense(128, activation='relu', input_dim = input_shape[1]))

        model.add(Dropout(0.5))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(16, activation='relu'))
        model.add(Dropout(0.4))
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        self.model = model

        numeric_labels = LabelEncoder().fit_transform(labels)
        y_train = to_categorical(numeric_labels, self.num_classes)

        self.model.fit(x_train, y_train, epochs=100, batch_size=32, verbose=2)
        loss, self.accuracy = self.model.evaluate(x_train, y_train)
        print('accuracy:', self.accuracy)

        return super().train(samples, features, labels)

    def test(self, samples, features, labels):
        self.load()

        #not sure we can use this max length if the length is diff than trained model is expecting then it will crash
        # max_length = max([len(s) for s in samples]) # todo think: might be a costly step if huge data, may be it should just be a constant (100)
        x_test = pad_sequences(features, maxlen=100, padding='post')

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
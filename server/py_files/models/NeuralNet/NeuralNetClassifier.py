import os
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Embedding
from keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from sklearn.utils import class_weight

from py_files.models.Vectorizer.Vectorizer import Vectorizer

from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.KerasSentenceClassifier import KerasSentenceClassifier

class NeuralNetClassifier(KerasSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type)
        self.num_inputs = Vectorizer(name, feature_type).num_inputs()

    def train(self, samples, labels):
        features = self.choose_features(samples, True)

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
            model.add(Dense(128, activation='relu', input_dim = self.num_inputs))

        model.add(Dropout(0.5))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(16, activation='relu'))
        model.add(Dropout(0.4))
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        self.model = model

        numeric_labels = LabelEncoder().fit_transform(labels)

        class_weights = class_weight.compute_class_weight('balanced',
                                                 np.unique(numeric_labels),
                                                 numeric_labels)

        y_train = to_categorical(numeric_labels)

        self.model.fit(x_train, y_train,validation_split=0.05, epochs=200, batch_size=128, verbose=1, shuffle=True, class_weight=class_weights)
        loss, self.accuracy = self.model.evaluate(x_train, y_train)
        print('accuracy:', self.accuracy)

        return super().train(samples, labels)

    def test(self, samples, labels):
        self.load()
        features = self.choose_features(samples, False)

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
        # return super().test(samples, labels)

        return super().test(samples, labels)

    def classify(self, samples):
        self.load()
        features = self.choose_features(samples, False)
        # todo
        return super().classify(samples)
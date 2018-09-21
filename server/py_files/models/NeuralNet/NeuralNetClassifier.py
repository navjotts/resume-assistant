import os
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Embedding
from keras.preprocessing.sequence import pad_sequences
# from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from sklearn.utils import class_weight

from py_files.models.Vectorizer.Vectorizer import Vectorizer
from py_files.models.SentenceLabelEncoder import LabelEncoder

from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.KerasSentenceClassifier import KerasSentenceClassifier

class NeuralNetClassifier(KerasSentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + feature_type)

    def train(self, samples, labels):
        features = self.choose_features(samples, True)

        x_train = pad_sequences(features, maxlen=100, padding='post')

        model = Sequential()
        if(self.feature_type == 'word-embeddings'):
            embedding_vecs = Embeddings(self.name, 100).vectors()
            vocab_size = embedding_vecs.shape[0]
            model.add(Embedding(vocab_size,100,input_length = 100, trainable =True, weights = [embedding_vecs] ))
            model.add(Flatten())
            model.add(Dense(128, activation='relu'))
        else:
            num_inputs = Vectorizer(name, feature_type).num_inputs()
            model.add(Dense(128, activation='relu', input_dim = num_inputs))

        model.add(Dropout(0.5))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(16, activation='relu'))
        model.add(Dropout(0.4))
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        self.model = model

        print(labels)
        numeric_labels = LabelEncoder().encode_numerical(labels)

        class_weights = class_weight.compute_class_weight('balanced',
                                                 np.unique(numeric_labels),
                                                 numeric_labels)

        y_train = LabelEncoder().encode_catigorical(labels)
        print(y_train)

        self.model.fit(x_train, y_train, validation_split=0.2, epochs=200, batch_size=128, verbose=1, shuffle=True, class_weight=class_weights)
        loss, self.accuracy = self.model.evaluate(x_train, y_train)
        print('accuracy:', self.accuracy)

        self.labels_pred = LabelEncoder().decode(self.model.predict(x_test))
        return super().train(samples, labels)

    def test(self, samples, labels):
        self.load()
        features = self.choose_features(samples)

        x_test = pad_sequences(features, maxlen=100, padding='post')


        y_test = LabelEncoder().encode_catigorical(labels)

        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        loss, self.accuracy = self.model.evaluate(x_test, y_test)
        print('accuracy:', self.accuracy)
        self.labels_pred = LabelEncoder().decode(self.model.predict_classes(x_test))
        # print(self.labels_pred)

        return super().test(samples, labels)

    def classify(self, samples):
        self.load()
        features = self.choose_features(samples)
        # todo
        return super().classify(samples)
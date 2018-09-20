import zerorpc

from py_files.Spacy import Spacy
from py_files.models.FastText.FastTextClassifier import FastTextClassifier
from py_files.models.LogisticRegression.LogRegClassifier import LogRegClassifier
from py_files.models.SVM.SVMClassifier import SVMClassifier
from py_files.models.RandomForest.RandForestClassifier import RandForestClassifier
from py_files.models.NaiveBayes.NaiveBayesClassifier import NaiveBayesClassifier
from py_files.models.LSTM.LSTMClassifier import LSTMClassifier
from py_files.models.NeuralNet.NeuralNetClassifier import NeuralNetClassifier
from py_files.models.CNNClassifier.CNNClassifier import CNNClassifier
from py_files.models.classifier import CNN
from py_files.Preprocess.NLP_preprocess import process_sent
from py_files.models.Vectorizer.Vectorizer import Vectorizer
from py_files.models.Embeddings.Embeddings import Embeddings

class PythonServer(object):
    def sentences(self, text):
        return Spacy.sentences(self, text, False)

    def sentences_from_file_lines(self, filepath, drop_stop = False, drop_punct = False):
        sents = []
        with open(filepath, encoding = 'utf8') as f:
            for line in f:
                # todo we are assuming incorrectly that each paragraph can be treated as a single sentence
                sentence = Spacy.tokenize(self, line, drop_stop, drop_punct)
                if sentence:
                    sents.append(sentence)
        return sents

    def train_classifier(self, model_name, model_type, feature_type, samples, labels):
        features = self.choose_features(model_name, feature_type, samples, True)
        model = self.choose_model(model_name, model_type, feature_type)
        return model.train(samples, features, labels)

    def test_classifier(self, model_name, model_type, feature_type, samples, labels):
        features = self.choose_features(model_name, feature_type, samples, False)
        model = self.choose_model(model_name, model_type, feature_type)
        return model.test(samples, features, labels)

    def classify_sentences(self, model_name, model_type, feature_type, samples):
        features = self.choose_features(model_name, feature_type, samples, False)
        model = self.choose_model(model_name, model_type, feature_type)
        return model.classify(features)

    # helper function to choose the appropriate class based on the model details provided
    def choose_model(self, model_name, model_type, feature_type):
        if model_type == 'FastText':
            return FastTextClassifier(model_name, feature_type)
        elif model_type == 'LogisticRegression':
            return LogRegClassifier(model_name, feature_type)
        elif model_type == 'SVM':
            return SVMClassifier(model_name, feature_type)
        elif model_type == 'RandomForest':
            return RandForestClassifier(model_name, feature_type)
        elif model_type == 'NaiveBayes':
            return NaiveBayesClassifier(model_name, feature_type)
        elif(model_type == 'LSTM'):
            return LSTMClassifier(model_name, feature_type)
        elif(model_type == "NeuralNet"):
            return NeuralNetClassifier(model_name, feature_type)
        elif(model_type == "CNN"):
            return CNNClassifier(model_name, feature_type)
        else:
            raise Exception('Please enter a valid model')

    # helper function to choose the appropriate feature vectorization based on the feature details provided
    def choose_features(self, model_name, feature_type, samples, retrain):
        if feature_type in ['tf-idf', 'bow']:
            return Vectorizer(model_name, feature_type).vectors(samples, retrain).toarray()
        elif feature_type == 'sentence-embeddings':
            return process_sent(samples)
        elif feature_type == 'word-embeddings':
            return Embeddings(model_name, 100).encode_samples(samples)
        else:
            return samples # no change/manipulation

    def train_embeddings(self, model_name, dimension, sents):
        embeddings = Embeddings(model_name, dimension)
        embeddings.train(sents)

    def generate_embeddings_coordinates(self, model_name, dimension, reduced_dimension):
        embeddings = Embeddings(model_name, dimension)
        embeddings.words_coordinates(reduced_dimension)

    def encode_samples(self, model_name, dimension, samples):
        embeddings = Embeddings(model_name, dimension)
        return embeddings.encode_samples(samples)

# print(Embeddings('resumes', 100).vectors()) # for testing other classes directly (comment out the below zerorps server if you do this)

try:
    s = zerorpc.Server(PythonServer())
    s.bind('tcp://0.0.0.0:4242')
    s.run()
    print('PythonServer running...')
except Exception as e:
    print('unable to start PythonServer:', e)
    raise e
import zerorpc

from py_files.Spacy import Spacy
from py_files.models.FastText.FastTextClassifier import FastTextClassifier
from py_files.models.LogisticRegression.LogRegClassifier import LogRegClassifier
from py_files.models.SVM.SVMClassifier import SVMClassifier
from py_files.models.classifier import RandomForest, NaiveBayes, LSTM, NeuralNet, CNN
from py_files.Preprocess.NLP_preprocess import process_sent
from py_files.models.Vectorizer.Vectorizer import Vectorizer
from py_files.models.Embeddings import Embeddings

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

    def test_sentence_classifier(self, name, path, samples, labels):
        FastTextClassifier.test(self, samples, labels)

    # helper function to choose the appropriate class based on the model details provided
    def choose_model(self, model_name, model_type, feature_type):
        if model_type == 'FastText':
            return FastTextClassifier(self)
        elif model_type == 'LogisticRegression':
            return LogRegClassifier(model_name, feature_type)
        elif model_type == 'SVM':
            return SVMClassifier(model_name, feature_type)
        elif model_type == 'RandomForest':
            return RandomForest(model_name, feature_type)
        elif model_type == 'NaiveBayes':
            return NaiveBayes(model_name, feature_type)
        elif(model_type == "LSTM"):
            return LSTM(model_name, feature_type)
        elif(model_type == "NeuralNet"):
            return NeuralNet(model_name, feature_type)
        elif(model_type == "CNN"):
            return CNN(model_name, feature_type)
        else:
            raise Exception('Please enter a valid model')

    # helper function to choose the appropriate feature vectorization based on the feature details provided
    def choose_features(self, model_name, feature_type, samples, retrain):
        if feature_type in ['tf-idf', 'bow']:
            return Vectorizer(model_name, feature_type).vectors(samples, retrain).toarray()
        elif feature_type == 'sentence-embeddings':
            return process_sent(samples)
        elif feature_type == 'keras-embeddings':
            Embedding_model  = Embeddings.Embeddings(model_name, 100)
            return Embedding_model.encode_samples(samples), Embedding_model.keras_embeddings_layer().input_dim
        else:
            print('no feature engineering!')
            return samples # no change/manipulation

    def train_embeddings(self, model_name, dimension, sents):
        embeddings = Embeddings(model_name, dimension)
        embeddings.train(sents)

    def generate_embeddings_coordinates(self, model_name, dimension, reduced_dimension):
        embeddings = Embeddings(model_name, dimension)
        embeddings.words_coordinates(reduced_dimension)

    def embeddings_layer(self, model_name, dimension):
        embeddings = Embeddings(model_name, dimension)
        return embeddings.keras_embeddings_layer()

    def encode_samples(self, model_name, dimension, samples):
        embeddings = Embeddings(model_name, dimension)
        return embeddings.encode_samples(samples)

# print(Embeddings('resumes', 100).word_to_index('React')) # for testing other classes directly (comment out the below zerorps server if you do this)

try:
    s = zerorpc.Server(PythonServer())
    s.bind('tcp://0.0.0.0:4242')
    s.run()
    print('PythonServer running...')
except Exception as e:
    print('unable to start PythonServer:', e)
    raise e
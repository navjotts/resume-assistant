import zerorpc

from py_files.Spacy import Spacy
from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.FastText.FastTextClassifier import FastTextClassifier
from py_files.models.classifier import SVM, LogisticRegression, RandomForest, NaiveBayes, LSTM
from py_files.Preprocess.NLP_preprocess import train_d2v,process_sent,SK_TFIDF_train, SK_TFIDF_predict, process_sentences

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
        samples = self.choose_samples(samples, True)
        features = self.choose_features(feature_type, samples)
        model = self.choose_model(model_name, model_type, feature_type)
        return model.train(features, labels)

    def test_classifier(self, model_name, model_type, feature_type, samples, labels):
        samples = self.choose_samples(samples, True)
        features = self.choose_features(feature_type, samples)
        model = self.choose_model(model_name, model_type, feature_type)
        return model.prediction(features, test = True, labels = labels, samples=samples)

    def classify_sentences(self, model_name, model_type, feature_type, samples):
        samples = self.choose_samples(samples, True)
        features = self.choose_features(feature_type, samples)
        model = self.choose_model(model_name, model_type, feature_type)
        return model.prediction(features)

    def test_sentence_classifier(self, name, path, samples, labels):
        FastTextClassifier.test(self, samples, labels)

    # helper function to choose the appropriate class based on the model details provided
    def choose_model(self, model_name, model_type, feature_type):
        if model_type == 'FastText':
            return FastTextClassifier(self)
        elif model_type == 'LogisticRegression':
            return LogisticRegression(model_name, feature_type)
        elif model_type == 'RandomForest':
            return RandomForest(model_name, feature_type)
        elif model_type == 'SVM':
            return SVM(model_name, feature_type)
        elif model_type == 'NaiveBayes':
            return NaiveBayes(model_name, feature_type)
        elif(model_type == "LSTM"):
            return LSTM(model_name, feature_type)
        else:
            raise Exception('Please enter a valid model')

    # todo clean this up
    def choose_samples(self, samples, combine_to_sents=False):
        if combine_to_sents:
            return [(' ').join(s) for s in samples]
        return samples

    # helper function to choose the appropriate feature vectorization based on the feature details provided
    def choose_features(self, feature_type, samples):
        if feature_type == 'tf-idf':
            return SK_TFIDF_predict(sents)
        elif feature_type == 'sentence-embeddings':
            return process_sent(sents)
        else:
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
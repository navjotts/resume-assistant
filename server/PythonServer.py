import zerorpc

from py_files.Spacy import Spacy
from py_files.ML_models.Embeddings.Embeddings import Embeddings
from py_files.ML_models.FastText.FastTextClassifier import FastTextClassifier
from py_files.ML_models.classifier import svm,Log_reg,Random_forest, naive_bayes, LSTM_model
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
        samples = self.choose_features(feature_type, samples)
        model = self.choose_model(model_name, model_type, feature_type)
        return model.train(samples, labels)

    def test_classifier(self, model_name, model_type, feature_type, samples, labels):
        sample_vecs = self.choose_features(feature_type, samples)
        model = self.choose_model(model_name, model_type, feature_type)
        return model.prediction(sample_vecs, test = True, labels = labels, samples=samples)

    def classify_sentences(self, model_name, model_type, feature_type, samples):
        samples = self.choose_features(feature_type, samples)
        model = self.choose_model(model_name, model_type, feature_type)
        return model.prediction(samples)

    def test_sentence_classifier(self, name, path, samples, labels):
        FastTextClassifier.test(self, samples, labels)

    # helper function to choose the appropriate class based on the model details provided
    def choose_model(self, model_name, model_type, feature_type):
        if model_type == 'FastText':
            return FastTextClassifier(self)
        elif model_type == 'LogisticRegression':
            return Log_reg(model_name, feature_type)
        elif model_type == 'RandomForest':
            return Random_forest(model_name, feature_type)
        elif model_type == 'SVM':
            return svm(model_name, feature_type)
        elif model_type == 'NaiveBayes':
            return naive_bayes(model_name, feature_type)
        elif(model_type == "LSTM"):
            return LSTM_model(model_name, feature_type)
        else:
            raise Exception('Please enter a valid model')

    # helper function to choose the appropriate feature vectorization based on the feature details provided
    def choose_features(self, feature_type, samples):
        if feature_type == 'tf-idf':
            return SK_TFIDF_predict(samples)
        elif feature_type == 'sentence-embeddings':
            return process_sent(samples)
        else:
            return samples # feature vector construction happens inside the model

    def train_embeddings(self, model_name, dimension, sents):
        embeddings = Embeddings(model_name, dimension)
        embeddings.train(sents)

    def most_similar_word(self, model_name, dimension, word):
        embeddings = Embeddings(model_name, dimension)
        return embeddings.most_similar(word)

    def generate_embeddings_coordinates(self, model_name, dimension, reduced_dimension):
        embeddings = Embeddings(model_name, dimension)
        embeddings.words_coordinates(reduced_dimension)

    def embeddings_layer(self, model_name, dimension):
        embeddings = Embeddings(model_name, dimension)
        return embeddings.keras_embeddings_layer()

try:
    s = zerorpc.Server(PythonServer())
    s.bind('tcp://0.0.0.0:4242')
    s.run()
    print('PythonServer running...')
except Exception as e:
    print('unable to start PythonServer:', e)
    raise e
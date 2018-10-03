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
from py_files.models.LSA.LSAModel import LSAModel
from py_files.models.Embeddings.Embeddings import Embeddings
from py_files.models.SentenceEmbeddings.SentenceEmbeddings import SentenceEmbeddings

class PythonServer(object):
    def sentences(self, text, drop_stop=False, drop_punct=False):
        return Spacy.sentences(self, text, drop_stop, drop_punct)

    def sentences_from_file_lines(self, filepath, drop_stop=False, drop_punct=False):
        sents = []
        with open(filepath, encoding = 'utf8') as f:
            for line in f:
                # todo we are assuming incorrectly that each paragraph can be treated as a single sentence
                sentence = Spacy.tokenize(self, line, drop_stop, drop_punct)
                if sentence:
                    sents.append(sentence)
        return sents

    def train_sentence_classifier(self, model_name, model_type, feature_type, samples, labels):
        model = self.choose_model(model_name, model_type, feature_type)
        return model.train(samples, labels)

    def test_sentence_classifier(self, model_name, model_type, feature_type, samples, labels):
        model = self.choose_model(model_name, model_type, feature_type)
        return model.test(samples, labels)

    def classify_sentences(self, model_name, model_type, feature_type, samples):
        model = self.choose_model(model_name, model_type, feature_type)
        return model.classify(samples)

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
        elif model_type == 'LSTM':
            return LSTMClassifier(model_name, feature_type)
        elif model_type == 'NeuralNet':
            return NeuralNetClassifier(model_name, feature_type)
        elif model_type == 'CNN':
            return CNNClassifier(model_name, feature_type)
        else:
            raise Exception('Please enter a valid model')

    def train_embeddings(self, model_name, dimension, sents):
        embeddings = Embeddings(model_name, dimension)
        embeddings.train(sents)

    def train_sent_embeddings(self, model_name, dimension, sents):
        sent_embeddings = SentenceEmbeddings(model_name, dimension)
        sent_embeddings.train(sents)

    def generate_embeddings_coordinates(self, model_name, dimension, reduced_dimension):
        embeddings = Embeddings(model_name, dimension)
        embeddings.words_coordinates(reduced_dimension)

    def sentence_group_similarity_score(self, model_name, dimension, sents, reverse_comparison=False, method='gensim'):
        sent_embeddings = SentenceEmbeddings(model_name, dimension)
        return sent_embeddings.group_similarity_score(sents, reverse_comparison, method)

    def top_topics(self, model_name, doc, num_topics, words_per_topic):
        lsa = LSAModel(model_name)
        return lsa.top_topics(doc, num_topics, words_per_topic)

    def document_similarity_score(self, model_name, doc1, doc2):
        lsa = LSAModel(model_name)
        return lsa.document_similarity_score(doc1, doc2)

# Embeddings('resumes', 100).vectors('glove') # for testing other classes directly (comment out the below zerorpc server if you do this)
# print(SentenceEmbeddings('resumes_jobs', 100).similarity_score(('Full', 'Stack', 'Internship', '·', 'July', '2017', 'to', 'Oct.', '2017'), ('5', 'years', 'of', 'experience', 'in', 'technical', 'leadership', 'and', 'people', 'management', '.'), 'gensim'))
# print(SentenceEmbeddings('resumes_jobs', 100).similarity_score(('5', 'years', 'of', 'experience', 'in', 'technical', 'leadership', 'and', 'people', 'management', '.'), ('Full', 'Stack', 'Internship', '·', 'July', '2017', 'to', 'Oct.', '2017'), 'gensim'))
# print(SentenceEmbeddings('resumes_jobs', 100).similarity_score(('10', 'years', 'of', 'relevant', 'industry', 'experience', '.'), ('Software', 'Engineer', '·', 'Nov.', '2017', 'to', 'Current'), 'gensim')) # todo this where sentence comparison with the current embeddings is completely failing

try:
    s = zerorpc.Server(PythonServer())
    s.bind('tcp://0.0.0.0:4242')
    s.run()
    print('PythonServer running...')
except Exception as e:
    print('unable to start PythonServer:', e)
    raise e
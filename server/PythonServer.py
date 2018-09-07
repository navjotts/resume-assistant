from hashlib import sha256
import zerorpc

from py_files.Spacy import Spacy
from py_files.SentenceClassifier import SentenceClassifier
from py_files.ML_models.Log_reg.Logistic_reg import Log_reg
from py_files.ML_models.Random_forest.Random_forest import Random_forest
from py_files.ML_models.SVM.SVM import svm_model
from py_files.Preprocess.NLP_preprocess import train_d2v,process_sent,SK_TFIDF_train, SK_TFIDF_predict


class PythonServer(object):

    def hash_file_name(self, filename):
        return sha256(str(filename).encode('utf-8')).hexdigest()

    def sentences(self, text):
        return Spacy.sentences(self, text, False)

    def sentences_from_file_lines(self, filepath):
        sents = []
        with open(filepath, encoding = 'utf8') as f:
            for line in f:
                # todo we are assuming incorrectly that each paragraph can be treated as a single sentence
                sentence = Spacy.tokenize(self, line, False)
                if sentence:
                    sents.append(sentence)
        return sents

    #intitial sentence classifier using fasttext
    def train_sentence_classifier(self, name, path, samples, labels):
        return SentenceClassifier.train(self, name, path, samples, labels)

    #new training classifier method, can take any available model
    def train_classifier(self, name, samples, labels):
        vectors = SK_TFIDF_train(samples) #enables TFIDF sentence vectors
        # vectors = process_sent(samples) #enables Doc2vec sentence vectors
        model = self.choose_model(name)
        results = model.train(vectors,labels)
        return results

    #new testing classifier method, can take any available model
    def test_classifier(self, name, samples, labels):
        vectors = SK_TFIDF_predict(samples) #enables TFIDF sentence vectors
        # vectors = process_sent(samples) #enables Doc2vec sentence vectors
        model = self.choose_model(name)
        results = model.prediction(vectors, Load_best=True, test=True, labels=labels)
        return results

    #new classifier method, can take any available model
    def classifier(self, name, samples):
        vectors = SK_TFIDF_predict(samples) #enables TFIDF sentence vectors
        # vectors = process_sent(samples) #enables Doc2vec sentence vectors
        model = self.choose_model(name) 
        results = model.prediction(vectors, Load_best=True)
        return results

    def test_sentence_classifier(self, name, path, samples, labels):
        SentenceClassifier.test(self, name, path, samples, labels)

    def classify_sentences(self, name, path, samples):
        return SentenceClassifier.classify(self, name, path, samples)

    #helper funtion to call any model to train
    def choose_model(self,  name, model = "svm"):
        """
        Helper function to choose which model is being used.
        """
        if(model == "Log_reg"):
            return Log_reg(name)
        elif(model == "Random_forest"):
            return Random_forest(name)
        elif(model == "svm"):
            return svm_model(name)
        else:
            raise Exception("Please enter a valid model")

try:
    s = zerorpc.Server(PythonServer())
    s.bind("tcp://0.0.0.0:4242")
    s.run()
    print("PythonServer running...")
except Exception as e:
    print('unable to start PythonServer:', e)
    raise e
from hashlib import sha256
import zerorpc

from py_files.Spacy import Spacy
from py_files.SentenceClassifier import SentenceClassifier
from py_files.ML_models.Log_reg.Logistic_reg import Log_reg
from py_files.Preprocess.NLP_preprocess import train_d2v,process_sent

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

    def train_sentence_classifier(self, name, path, samples, labels):
        return SentenceClassifier.train(self, name, path, samples, labels)

    def train_classifier(self, name, samples, labels):
        train_d2v(samples)
        vectors = process_sent(samples)
        model = Log_reg(name)
        results = model.train(vectors,labels)
        return results

    def test_classifier(self, name, samples, labels):
        vectors = process_sent(samples)
        model = Log_reg(name)
        results = model.prediction(vectors, Load_best=True, test=True, labels=labels)
        return results

    def classifier(self, name, samples):
        vectors = process_sent(samples)
        model = Log_reg(name)
        results = model.prediction(vectors, Load_best=True)
        return results

    def test_sentence_classifier(self, name, path, samples, labels):
        SentenceClassifier.test(self, name, path, samples, labels)

    def classify_sentences(self, name, path, samples):
        return SentenceClassifier.classify(self, name, path, samples)

try:
    s = zerorpc.Server(PythonServer())
    s.bind("tcp://0.0.0.0:4242")
    s.run()
    print("PythonServer running...")
except Exception as e:
    print('unable to start PythonServer:', e)
    raise e
import zerorpc

from py.Spacy import Spacy

class PythonServer(object):
    def sentences(self, text):
        return Spacy.sentences(self, text, True)

    def sentences_from_file_line(self, filepath):
        sents = []
        with open(filepath, encoding = 'utf8') as f:
            for line in f:
                sentence = Spacy.tokenize(self, line, False)
                sents.append(sentence)
        return sents


try:
    s = zerorpc.Server(PythonServer())
    s.bind("tcp://0.0.0.0:4242")
    s.run()
    print("PythonServer running...")
except Exception as e:
    print('unable to start PythonServer:', e)
    raise e
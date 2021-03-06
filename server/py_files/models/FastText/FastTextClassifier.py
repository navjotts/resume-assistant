import os
import tempfile
import fastText
from py_files.models.SentenceClassifier import SentenceClassifier

class FastTextClassifier(SentenceClassifier):
    def __init__(self, name, feature_type):
        super().__init__(name, feature_type)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '.bin')

    def train(self, samples, labels):
        features = self.choose_features(samples)

        fd, labelPath = tempfile.mkstemp()
        try:
            self.generate_data_file(labelPath, features, labels)
            print('Training started ...')
            self.model = fastText.train_supervised(labelPath, epoch=30, wordNgrams=2)
            print('Training ended ...')

            print("Quantizing ...")
            self.model.quantize()

            result = self.model.test(labelPath)
            result = f'precision: {result[1]}, recall: {result[2]}'
            print(result)
        finally:
            os.remove(labelPath)

        self.model.save_model(self.path)

        return result # todo consolidate with AccuracyAnalysis => super().train()

    def load(self):
        if not self.model:
            try:
                self.model = fastText.load_model(self.path)
            except:
                print('Unable to locate model', self.name)

        super().load()

    def test(self, samples, labels):
        self.load()
        features = self.choose_features(samples)
        pred, prob = self.model.predict(list(features))
        self.labels_pred = [each[0][len('__label__'):] for each in pred]

        return super().test(samples, labels)

    def classify(self, samples):
        self.load()
        features = self.choose_features(samples)
        pred, prob = self.model.predict(list(features))
        self.labels_pred = [each[0][len('__label__'):] for each in pred]
        self.prob_pred = [each[0] for each in prob]

        return super().classify(samples)

    def choose_features(self, samples, retrain=False):
        return self.words_to_sents(samples)

    def generate_data_file(self, file, samples, labels):
        text = ''
        for i, sample in enumerate(samples):
            line = '__label__' + labels[i] + ' ' + sample + '\n'
            text += line
        file = open(file,'w', encoding = 'utf-8')
        file.write(text)
        file.close()
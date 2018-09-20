import os
import tempfile
import fastText
import numpy as np

from py_files.AccuracyAnalysis import AccuracyAnalysis

class FastTextClassifier(object):
    def __init__(self, name):
        self.name = name
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weights', 'resumes')
        self.models = {}

    def train(self, samples, labels):
        model = None
        fd, labelPath = tempfile.mkstemp()

        try:
            self.generate_data_file(labelPath, samples, labels)
            print('Training started ...')
            model = fastText.train_supervised(labelPath, epoch=30, wordNgrams=2)
            self.models[self.name] = model
            print('Training ended ...')

            print("Quantizing ...")
            model.quantize()

            result = model.test(labelPath)
            result = {'precision': result[1],  'recall': result[2], 'examples': result[0]}
            print('Precision:', result['precision'])
            print('Recall:', result['recall'])
        finally:
            os.remove(labelPath)

        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        model.save_model(self.path + '.bin')

        return result

    def test(self, samples, labels):
        if self.name not in self.models:
            self.load()

        model = self.models[self.name]

        pred, prob = model.predict(list(samples))
        labels_pred = [each[0][len('__label__'):] for each in pred]

        score = AccuracyAnalysis.score(self, labels, labels_pred)
        report = AccuracyAnalysis.report(self, labels, labels_pred)
        confusion_matrix = AccuracyAnalysis.confu_matrix(self, labels, labels_pred)
        print('> ********* CoNFuSioN MaTRiX ************ <')
        print(confusion_matrix)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, labels_pred, samples)
        # todo : it seems like some of the pred_label are empty ==> please check Cc @darwin (we can check with if each['pred_label'] is empty string inside the for loop `for each in misclassifications`)

        return {'score': score, 'report': report, 'misclassifications': misclassifications, 'confusion_matrix': confusion_matrix}

    # todo rename to predcit or classify
    def prediction(self, samples_true, test=False, labels="None", samples="None"):
        if test:
            return self.test(samples, labels)

        if self.name not in self.models:
            self.load()

        model = self.models[self.name]

        pred, prob = model.predict(list(samples_true))
        labels_pred = [each[0][len('__label__'):] for each in pred]
        prob_pred = [each[0] for each in prob]

        return list(zip(labels_pred, prob_pred))

    def load(self):
        model = None
        if self.name not in self.models:
            try:
                model = fastText.load_model(self.path + '.bin')
            except:
                print('Unable to locate model', self.name)

        self.models[self.name] = model

    def generate_data_file(self, file, samples, labels):
        text = ''
        for i, sample in enumerate(samples):
            line = '__label__' + labels[i] + ' ' + sample + '\n'
            text += line
        file = open(file,'w', encoding = 'utf-8')
        file.write(text)
        file.close()

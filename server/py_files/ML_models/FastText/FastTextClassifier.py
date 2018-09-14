import os
import tempfile
import fastText
import numpy as np

from py_files.AccuracyAnalysis import AccuracyAnalysis

class FastTextClassifier(object):
    models = {}

    def __init__(self, name):
        self.name = name
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weights', 'resumes')

    def train(self, samples, labels):
        model = None
        fd, labelPath = tempfile.mkstemp()

        try:
            FastTextClassifier.generate_data_file(self, labelPath, samples, labels)
            print('Training started ...')
            model = fastText.train_supervised(labelPath, epoch=30, wordNgrams=2)
            FastTextClassifier.models[self.name] = model
            print('Training ended ...')

            # print("Quantizing ...")
            # model.quantize()

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
        if self.name not in FastTextClassifier.models:
            FastTextClassifier.load(self)

        model = FastTextClassifier.models[self.name]

        pred, prob = model.predict(list(samples))
        labels_pred = [each[0][len('__label__'):] for each in pred]

        report = AccuracyAnalysis.report(self, labels, labels_pred)
        print()
        print(report)

        misclassifications = AccuracyAnalysis.misclassifications(self, labels, labels_pred, samples)
        print()
        print('Index          Sample                         Predicted          Actual')
        for each in misclassifications:
            print('%d          %.20s          %s          %s' % (each['sample_index'], each['sample'], each['pred_label'], each['actual_label']))
        # todo : it seems like some of the actual_labels are empty ==> please check Cc @darwin (we can check with if each['actual_label'] is empty string inside the above for loop)

        score = AccuracyAnalysis.score(self, labels, labels_pred)
        print()
        print(score)

        return score

    # todo rename to predcit or classify
    def prediction(self, samples, test=False, labels="None"):
        if test:
            return self.test(samples, labels)

        if self.name not in FastTextClassifier.models:
            FastTextClassifier.load(self)

        model = FastTextClassifier.models[self.name]

        pred, prob = model.predict(list(samples))
        labels_pred = [each[0][len('__label__'):] for each in pred]
        prob_pred = [each[0] for each in prob]

        return list(zip(labels_pred, prob_pred))

    def load(self):
        model = None
        if self.name not in FastTextClassifier.models:
            try:
                model = fastText.load_model(self.path + '.bin')
            except:
                print('Unable to locate model', self.name)

        FastTextClassifier.models[self.name] = model

    def generate_data_file(self, file, samples, labels):
        text = ''
        for i, sample in enumerate(samples):
            line = '__label__' + labels[i] + ' ' + sample + '\n'
            text += line
        file = open(file,'w', encoding = 'utf-8')
        file.write(text)
        file.close()
import os
import tempfile
import fastText
import numpy as np

class SentenceClassifier(object):
    models = {}

    def train(self, name, path, samples, labels):
        model = None
        fd, labelPath = tempfile.mkstemp()

        try:
            SentenceClassifier.generate_data_file(self, labelPath, samples, labels)
            print('Training started ...')
            model = fastText.train_supervised(labelPath, epoch=30, wordNgrams=2)
            SentenceClassifier.models[name] = model
            print('Training ended ...')

            print("Quantizing ...")
            model.quantize()

            result = model.test(labelPath)
            result = {'precision': result[1],  'recall': result[2], 'examples': result[0]}
            print('Precision:', result['precision'])
            print('Recall:', result['recall'])
        finally:
            os.remove(labelPath)

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        model.save_model(path + '.bin')

        return result

    def test(self, name, path, samples, labels):
        if name not in SentenceClassifier.models:
            SentenceClassifier.load(self, name, path)

        model = SentenceClassifier.models[name]
        print('Testing using model', model)

        pred, prob = model.predict(list(samples))
        labels_pred = [each[0][len('__label__'):] for each in pred]
        accuracy = np.array([int(labels_pred[i] == label) for i, label in enumerate(labels)])
        print("Number of misclassifications: %d (out of %d)" % (sum(accuracy == 0), len(accuracy)))
        print("Accuracy:", sum(accuracy != 0)/len(accuracy))

    def classify(self, name, path, samples):
        if name not in SentenceClassifier.models:
            SentenceClassifier.load(self, name, path)

        model = SentenceClassifier.models[name]
        print('Predicting using model', model)

        pred, prob = model.predict(list(samples))
        labels_pred = [each[0][len('__label__'):] for each in pred]
        prob_pred = [each[0] for each in prob]

        return list(zip(labels_pred, prob_pred))

    def load(self, name, path):
        model = None
        if name not in SentenceClassifier.models:
            try:
                model = fastText.load_model(path + '.bin')
            except:
                print('Unable to locate model', name)

        SentenceClassifier.models[name] = model

    def generate_data_file(self, file, samples, labels):
        text = ''
        for i, sample in enumerate(samples):
            line = '__label__' + labels[i] + ' ' + sample + '\n'
            text += line
        file = open(file,'w', encoding = 'utf-8')
        file.write(text)
        file.close()
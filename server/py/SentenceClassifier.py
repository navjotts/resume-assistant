import os
import tempfile
import fastText
from sklearn.metrics import precision_recall_fscore_support

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

            #model.quantize()

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
        model = None
        if name not in SentenceClassifier.models:
            try:
                model = fastText.load_model(path + '.bin')
            except:
                pass

            if not model:
                print('Unable to locate model', name)
                return

        SentenceClassifier.models[name] = model
        print('Testing using model', model)

        pred = model.predict(list(samples))
        pred_labels = [each[0][len('__label__'):] for each in pred[0]]
        print(list(zip(labels, pred_labels)))

    def generate_data_file(self, file, samples, labels):
        text = ''
        for i, sample in enumerate(samples):
            line = '__label__' + labels[i] + ' ' + sample + '\n'
            text += line
        file = open(file,'w', encoding = 'utf-8')
        file.write(text)
        file.close()
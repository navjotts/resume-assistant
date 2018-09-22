import numpy as np
from sklearn.metrics import precision_recall_fscore_support, f1_score, classification_report, confusion_matrix

class AccuracyAnalysis(object):
    def score(self, y_true, y_predict):
        '''
            given y and y_predict,
            returns a score object with keys 'precision', 'recall' and 'f1_score'
        '''
        precision, recall, fscore, _ = precision_recall_fscore_support(y_true, y_predict, average='micro')
        return {'precision':precision, 'recall':recall, 'f1_score':fscore}

    def misclassifications(self, y_true, y_predict, samples):
        '''
            given y, y_predict and samples
            returns a list of misclassification objects,
            each with keys 'sample_index', 'sample', 'pred_label', 'actual_label'
        '''
        assert len(y_true) == len(y_predict) == len(samples)
        ret = []
        for i in range(len(y_true)):
            if y_true[i] != y_predict[i]:
                ret.append({
                    'sample_index':i,
                    'sample': samples[i],
                    'pred_label': y_predict[i],
                    'actual_label': y_true[i]
                    })

        return ret

    def report(self, y_true, y_predict):
        '''
            returns a text report (string) showing the classification metrics per label
        '''
        return classification_report(y_true, y_predict, digits = 3)

    def confusion_matrix(self, y_true, y_predict):
        '''
            returns an sklearn confusion matrix
        '''
        return confusion_matrix(y_true, y_predict)

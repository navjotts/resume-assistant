import numpy as np
from sklearn.metrics import precision_recall_fscore_support, f1_score, classification_report

class AccuracyAnalysis(object):
    def analyze(self, y_true, y_predict, samples):

        print(len(y_true), len(y_predict))

        mispredictions = []
        for n in range(len(y_true)):
            if y_true[n] != y_predict[n]:
                mispredictions.append({"actual_label": y_true[n], "pred_label": y_predict[n], "sample": samples[n], "sample_index":n})

        print('\n\t\t*** %d mispredictions out of %d samples ***\n' % (len(mispredictions),len(y_true)))

        return tuple(mispredictions)

    def report(self, y_true, y_predict):
        print('\nscikit_learn Classification Report\n\n', classification_report(y_true, y_predict), '\n')

        accuracy = np.array([int(y_predict[i] == label) for i, label in enumerate(y_true)])
        print("\n\n\tNumber of mispredictions: %d (out of %d)\n" % (sum(accuracy == 0), len(accuracy)))

    def score(self, y_true, y_predict):
        precision, recall, fscore, _ = precision_recall_fscore_support(y_true, y_predict, average="micro")
        return {'precision':precision, 'recall':recall, 'f1_score':fscore }

    def f1_score(self, y_true, y_predict):
        return {'f1_score':f1_score(y_true,y_predict, average="micro") }
#        return(f1_score(y_true, y_predict, average="micro"))



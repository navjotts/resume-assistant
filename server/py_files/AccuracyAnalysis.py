import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, f1_score, classification_report

class AccuracyAnalysis(object):
    def analyze(self, y_true, y_predict):
        
        accuracy = np.array([int(y_predict[i] == label) for i, label in enumerate(y_true)])
        print("\n\n\tNumber of misclassifications: %d (out of %d)" % (sum(accuracy == 0), len(accuracy)))

        prfs = precision_recall_fscore_support(y_true, y_predict, average="micro")
        print('scikit_learn Accuracy', prfs[0])

        print('scikit_learn Classification Report\n\n', classification_report(y_true, y_predict))
        
        precision, recall, fscore, _ = precision_recall_fscore_support(y_true, y_predict, average="micro")


        return {'precision':precision, 'recall':recall, 'fscore':fscore }





from sklearn.metrics import precision_recall_fscore_support, accuracy_score, f1_score, classification_report

class AccuracyAnalysis(object):
    def analyze(self, y_true, y_predict):
        print('\n ---- From the AccuracyAnalysis Module ----')

        
        prfs = precision_recall_fscore_support(y_true, y_predict, average="micro")
        print('scikit_learn Accuracy', prfs[0])
        print('scikit_learn Accuracy Module', accuracy_score(y_true, y_predict))
        print('scikit_learn f1_score', f1_score(y_true, y_predict, average="micro"))
        print('scikit_learn Classification Report', classification_report(y_true, y_predict))
        

        
        print('\n ____ From the AccuracyAnalysis Module ____')
        
        precision, recall, fscore, _ = precision_recall_fscore_support(y_true, y_predict, average="micro")

        
        return {'precision':precision, 'recall':recall, 'fscore':fscore }





# import relevent modules
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib
from glob import glob
from os.path import basename

# General classifier object, call this to instantiate a model.
class base_classifier():  
    """
    Class used to easily call train, test, prediction, and load on to act on a ml model object.

    """
    def __init__(self, name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = None
        self.path = "server/py_files/ML_models/weights/"
        ## create the acutal model
        self.model = None

    # traing the model on the given samples and labels.
    # input the whole data set, this method will split into train and test
    def train(self,samples,labels):
        """
        Given a list of samples and labels this method will do a trai/test split and
        train the modeol on that data.
        """
        # split data into test train split
        x_train, x_test, y_train, y_test = train_test_split(samples, labels,
                                                            test_size=0.25, random_state=42)
        print("\n++++ Begin Training ++++\n\n")
        # train model
        self.model.fit(x_train, y_train)
        print("\n\n++++ Training Complete ++++\n\n")
        # print accuracy on test data
        score = self.model.score(x_test,y_test)
        print("On test data, this model was %f %% accurate.\n\n" %(round(score*100,2)))
        # save model
        self.path = self.path + str(self.model_type)+ '_' + str(self.feature_type) + '_' + str(self.name) + "_" + str(int(score*100)) + ".pkl"
        joblib.dump(self.model, self.path)

        return {'Accuracy': round(score*100,2) , 'Predicitons': [self.model.predict(vec.reshape(1,-1)) for vec in samples], 'Labels': labels}

    def prediction(self, vects, Load_best=True, model_path=None, test=False, labels="None"):
        """
        Input a list of vectors, these vectors will all get a predicted class from the loaded modelself.
        If you want to test the model without using train set test to True and supply labels.
        """
        #load model based on inputs
        self.load_model(self.name, self.model_type, self.feature_type)
        # for each vector in the list append a prediction to results
        results = [self.model.predict(vec.reshape(1,-1)) for vec in vects]
        if(self.model_type == 'svm_model'):
            probs =  [['N/A for SVM''s' for vec in vects]]
        else:
            probs =  [np.argmax(self.model.predict_proba(vec.reshape(1,-1))) for vec in vects]      
        print("\n\n+++++ Results +++++\n\n\n\n prediciton:%s\n\n label:%s"%([x[0] for x in results[0:10]],labels[0:10]))
        # print out the results depending on case
        #printout test results with label
        if(test and bool(labels)):
            return {'Predicitons':results,'labels':labels, 'probabilities': probs}
        #raise error since the labels were not provided with the test
        elif(test and not labels):
            raise Exception('Can not enable test mode without supplying labels, Check arguments')
        #just return the predicted results, this is used for inference/production
        else:
         return list(zip(results, probs))

    def load_model(self, name, model_type, feature_type, Load_best=True, model_path=None):

        #load best model
        if(Load_best):

            best = 0
            best_file = ""

            #find highest accuracy model
            for file in glob("./server/py_files/ML_models/weights/%s_%s_%s*.pkl" %(model_type, feature_type, name) ):
                if(int(file[-6:-4]) > best):
                    best_file = file
                else:
                    next
            try:
                self.model = joblib.load(best_file)
            except:
                print(best_file)
                raise Exception('Must provide a valid path trained model, starting from /server directory.')

        # load the model form the given input path
        else:
            try:
                self.model = joblib.load(model_path)
            except:
                raise Exception('Must provide a valid path trained model, starting from /server directory.')

        print("\n\n+++++ Model successfully loaded +++++\n\n\t%s" %(basename(best_file)))

        return 0

class Log_reg(base_classifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'log_reg'
        self.path = "server/py_files/ML_models/weights/"
        ## create the acutal model
        self.model = LogisticRegression( random_state=42, max_iter=1000)

class Random_forest(base_classifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'random_forest'
        self.path = "server/py_files/ML_models/weights/"
        ## create the acutal model
        self.model = RandomForestClassifier( random_state=42, max_depth=110, n_estimators=150)

class svm(base_classifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'svm'
        self.path = "server/py_files/ML_models/weights/"
        ## create the acutal model
        self.model = LinearSVC( random_state=42, class_weight='balanced', tol=.00001, max_iter=5000)

class naive_bayes(base_classifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'naive_bayes'
        self.path = "server/py_files/ML_models/weights/"
        ## create the acutal model
        self.model = MultinomialNB()
        



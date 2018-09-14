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
from py_files.AccuracyAnalysis import AccuracyAnalysis

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
        # score = self.model.score(x_test,y_test)
        labels_pred = [self.model.predict(vec.reshape(1,-1)) for vec in samples]
        score = AccuracyAnalysis.score(self, labels, labels_pred)
        report = AccuracyAnalysis.report(self, labels, labels_pred)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, labels_pred, samples)
        
        print("On test data, this model was %f %% accurate.\n\n" %(round(score*100,2)))
        # save model
        self.path = self.path + str(self.model_type)+ '_' + str(self.feature_type) + '_' + str(self.name) + "_" + str(int(score*100)) + ".pkl"
        joblib.dump(self.model, self.path)

        # return {'Accuracy': round(score*100,2) , 'Predicitons': [self.model.predict(vec.reshape(1,-1)) for vec in samples], 'Labels': labels}
        return {'score': score, 'report': report, 'misclassifications': misclassifications}

    def prediction(self, vecs, Load_best=True, model_path=None, test=False, labels="None", samples = 'None'):
        """
        Input a list of vectors, these vectors will all get a predicted class from the loaded modelself.
        If you want to test the model without using train set test to True and supply labels.
        """
        #load model based on inputs
        self.load_model(self.name, self.model_type, self.feature_type)
        # for each vector in the list append a prediction to results
        labels_pred = [str(self.model.predict(vec[0]))[2:-2] for vec in vecs]
        # if(self.model_type == 'svm_model'):
        #     probs =  [['N/A for SVM''s' for vec in vecs]]
        # else:
        #     probs =  [np.argmax(self.model.predict_proba(vec.reshape(1,-1))) for vec in vecs]     

        score = AccuracyAnalysis.score(self, labels, labels_pred)
        report = AccuracyAnalysis.report(self, labels, labels_pred)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, labels_pred, samples)
        # todo : it seems like some of the pred_label are empty ==> please check Cc @darwin (we can check with if each['pred_label'] is empty string inside the for loop `for each in misclassifications`)

        print("\n\n+++++ Results +++++\n\n\n\n prediciton:%s\n\n label:%s"%([x for x in labels_pred[0:10]],labels[0:10]))
        # print out the results depending on case
        #printout test results with label
        if(test and bool(labels)):
            return {'score': score, 'report': report, 'misclassifications': misclassifications}
        #raise error since the labels were not provided with the test
        elif(test and not labels):
            raise Exception('Can not enable test mode without supplying labels, Check arguments')
        #just return the predicted results, this is used for inference/production
        else:
         return labels_pred

    def load_model(self, name, model_type, feature_type, Load_best=True, model_path=None):

        #load best model
        print(model_type,feature_type,name)
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

import numpy
from keras.datasets import imdb
from keras.models import Sequential
from keras.layers import Dense, Flatten, Input
from keras.layers import LSTM, TimeDistributed, Dropout
from keras.layers.embeddings import Embedding
from keras.metrics import sparse_categorical_accuracy
from keras.preprocessing import sequence
from keras.preprocessing.text import one_hot
from keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.utils import np_utils
# from scipy.sparse import csr_matrix
# fix random seed for reproducibility
numpy.random.seed(7)


class DL_classifier():
    """
    deep learning class with its own training methods, 
    as they differ from the base class since they are all sk learn models.
    """

    def __init__(self, name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = None
        self.path = "server/py_files/ML_models/weights/"
        ## create the acutal model
        self.model = None

    def train(self,samples,labels):
        self.compile()
        # encoded_docs = [one_hot(d, 1000) for d in samples]

        max_length = 4000
        print(type(samples))
        padded_docs = pad_sequences(np.array(samples.todense()), maxlen=max_length)
        padded_docs = np.array(padded_docs).flatten().reshape((padded_docs.shape[0],16, 250))
        labels = LabelEncoder().fit_transform(labels)
        dummy_labels = np_utils.to_categorical(labels)
        print(dummy_labels.shape)
        # split data into test train split
        x_train, x_test, y_train, y_test = train_test_split(padded_docs, dummy_labels,
                                                            test_size=0.25, random_state=42)

        
        # print(np.array(x_train).flatten().reshape(padded_docs.shape[0],25,2))
        x_train = np.array(x_train)
        y_train = np.array(y_train)
        x_test = np.array(x_test)
        y_test = np.array(y_test)

        # max_review_length = 50
        # x_train = sequence.pad_sequences(x_train, maxlen=max_review_length)
        # x_test = sequence.pad_sequences(x_test, maxlen=max_review_length)

        print("\n++++ Begin Training ++++\n\n")
        self.model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=5000, batch_size=128, verbose = 1)
        print("\n\n++++ Training Complete ++++\n\n")

        score = self.model.evaluate(x_test,y_test)
        print(score)
        print("On test data, this model was %.2f %% accurate.\n\n" %(score[1]*100))

    
class LSTM_model(DL_classifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'LSTM'
        self.path = "server/py_files/ML_models/weights/"
        ## create the acutal model
        self.model = None

    def compile(self):
        model = Sequential()
        model.add(LSTM(100, input_shape = (16,250),return_sequences=True))
        model.add(LSTM(50,return_sequences=True))
        model.add(LSTM(50,return_sequences=True))
        model.add(LSTM(50,return_sequences=True))
        model.add(LSTM(50))
        model.add(Dropout(0.3))
        model.add(Dense(128, activation='relu'))
        model.add(Dense(128, activation='relu'))
        model.add(Dense(128, activation='relu'))
        model.add(Dense(128, activation='relu'))
        model.add(Dropout(0.3))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(5, activation='sigmoid'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        self.model = model

        return model


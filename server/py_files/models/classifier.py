# import relevent modules
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression as log_reg
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib
from glob import glob
from os.path import basename
from py_files.AccuracyAnalysis import AccuracyAnalysis


# General classifier object, call this to instantiate a model.
class BaseClassifier():
    """
    Class used to easily call train, test, prediction, and load on to act on a ml model object.

    """
    def __init__(self, name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = None
        self.path = "server/py_files/models/trained/"
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

        score = AccuracyAnalysis.score(self, labels, labels_pred)
        report = AccuracyAnalysis.report(self, labels, labels_pred)
        misclassifications = AccuracyAnalysis.misclassifications(self, labels, labels_pred, samples)

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
            for file in glob("./server/py_files/models/trained/%s_%s_%s*.pkl" %(model_type, feature_type, name) ):
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

class LogisticRegression(BaseClassifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'LogisticRegression'
        self.path = "server/py_files/models/trained/"
        ## create the acutal model
        self.model = log_reg( random_state=42, max_iter=1000)

class RandomForest(BaseClassifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'RandomForest'
        self.path = "server/py_files/models/trained/"
        ## create the acutal model
        self.model = RandomForestClassifier( random_state=42, max_depth=110, n_estimators=150)

class SVM(BaseClassifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'SVM'
        self.path = "server/py_files/models/trained/"
        ## create the acutal model
        self.model = LinearSVC( random_state=42, class_weight='balanced', tol=.00001, max_iter=5000)

class NaiveBayes(BaseClassifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'NaiveBayes'
        self.path = "server/py_files/models/trained/"
        ## create the acutal model
        self.model = MultinomialNB()

import numpy
from keras.models import Sequential
from keras.layers import Dense, Flatten, Input, Dropout, Conv1D, MaxPool1D, Embedding, AvgPool1D
from keras.layers import LSTM as long_short_term_memory 
from keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.utils import np_utils
from keras.layers import Embedding
from py_files.models.Embeddings import Embeddings
import keras
# from scipy.sparse import csr_matrix
# fix random seed for reproducibility
numpy.random.seed(7)


class DeepClassifier():
    """
    deep learning class with its own training methods,
    as they differ from the base class since they are all sk learn models.
    """

    def __init__(self, name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = None
        self.path = "server/py_files/models/trained/"
        ## create the acutal model
        self.model = None

    def train(self,samples,labels):
        
        if(self.feature_type == 'keras-embeddings'):
            self.compile(samples[1])
            max_length = 100
            samples = pad_sequences(samples[0], maxlen=max_length, padding='post')
        elif(self.feature_type == 'tf-idf'):
            samples = samples.todense()
            self.compile(np.array(samples).shape)
        else:
            self.compile(np.array(samples).shape)

        labels = LabelEncoder().fit_transform(labels)
        dummy_labels = np_utils.to_categorical(labels)
        print(dummy_labels.shape)
        # split data into test train split
        x_train, x_test, y_train, y_test = train_test_split(samples, dummy_labels,
                                                            test_size=0.05, random_state=42)

        x_train = np.array(x_train)
        y_train = np.array(y_train)
        x_test = np.array(x_test)
        y_test = np.array(y_test)

        early_stop = keras.callbacks.EarlyStopping(monitor='val_loss',
                              min_delta=0,
                              patience=4,
                              verbose=0, mode='auto')

        callbacks_list = [early_stop]

        print("\n++++ Begin Training ++++\n\n")
        self.model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=100, batch_size=4, verbose = 1, callbacks=callbacks_list)
        print("\n\n++++ Training Complete ++++\n\n")

        score = self.model.evaluate(x_test,y_test)
        print(score)
        print("On test data, this model was %.2f %% accurate.\n\n" %(score[1]*100))
        
        #save model weights
        self.path = self.path + str(self.model_type)+ '_' + str(self.feature_type) + '_' + str(self.name) + "_" + str(int(score[1]*100)) + ".json"
        model_json = self.model.to_json()
        with open(self.path, "w") as json_file:
            json_file.write(model_json)


class LSTM(DeepClassifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'LSTM'
        self.path = "server/py_files/models/trained/"
        ## create the acutal model
        self.model = None

    def compile(self, vocab_size):
        Embedding_model  = Embeddings.Embeddings(self.name, 100)
        embedding_vecs = Embedding_model.keras_embeddings_layer()
        model = Sequential()
        model.add(embedding_vecs)
        model.add(long_short_term_memory(100,return_sequences=True))
        model.add(long_short_term_memory(50,return_sequences=True))
        model.add(long_short_term_memory(50,return_sequences=False))
        model.add(Dropout(0.3))
        model.add(Dense(128, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.3))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dropout(0.3))
        model.add(Dense(5, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        self.model = model

        return model

class NeuralNet(DeepClassifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'NeuralNet'
        self.path = "server/py_files/models/trained/"
        ## create the acutal model
        self.model = None

    def compile(self, input_shape):
        model = Sequential()
        if(self.feature_type == 'keras-embeddings'):
            Embedding_model  = Embeddings.Embeddings(self.name, 100)
            embedding_vecs = Embedding_model.keras_embeddings_layer()
            model.add(Embedding(input_shape+1,100,input_length = 100, trainable =True))
            model.add(Flatten())
            model.add(Dense(1024, activation='relu'))
        else:
            model.add(Dense(128, activation='relu', input_dim = input_shape[1]))
        model.add(Dropout(0.5))
        model.add(Dense(64, activation='relu'))
        # model.add(Dropout(0.3))     
        # model.add(Dense(512, activation='relu'))
        # model.add(Dropout(0.3))     
        # model.add(Dense(256, activation='relu'))
        # model.add(Dropout(0.3))     
        # model.add(Dense(64, activation='relu')) 
        # model.add(Dropout(0.3))       
        # model.add(Dense(32, activation='relu'))
        # model.add(Dropout(0.3))     
        # model.add(Dense(32, activation='relu'))
        # model.add(Dropout(0.5))     
        model.add(Dense(16, activation='relu'))
        model.add(Dropout(0.4))        
        model.add(Dense(5, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        self.model = model

        return model

class CNN(DeepClassifier):
    def __init__(self,name, feature_type):
        self.name = name
        self.feature_type = feature_type
        self.model_type = 'CNN'
        self.path = "server/py_files/models/trained/"
        ## create the acutal model
        self.model = None

    def compile(self, input_shape):
        Embedding_model  = Embeddings.Embeddings(self.name, 100)
        embedding_vecs = Embedding_model.keras_embeddings_layer()
        model = Sequential()
        model.add(Embedding(input_shape+1,100,input_length = 100, trainable =True))
        model.add(Conv1D(256, 5, activation='relu',data_format='channels_first', padding = 'valid', strides = 4))
        model.add(MaxPool1D(5))
        model.add(Dropout(0.3))  
        model.add(Conv1D(128, 5, activation='relu',data_format='channels_first',padding = 'valid', strides = 2))
        model.add(AvgPool1D(10))
        model.add(Flatten())
        model.add(Dense(256, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dropout(0.2))      
        model.add(Dense(5, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
        print(model.summary())
        self.model = model

        return model


#import relevent models
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib

#Overall class for the logistoc regression model
class Log_reg():
    """ 
    Class used to easily train and logistic regression from SKlearn and then, once trained, 
    the prediciotn mthod can be called to make predcitions from a saved model   
    
    """
    def __init__(self, name):
        self.name = name
        self.path = "./weights/"
        ## create the acutal model
        self.model = LogisticRegression()
        
    #traing the model on the given samples and labels.
    #input the whole data set, this method will split into train and test
    def train(self,samples,labels):
        """
        Given a list of samples and labels this method will do a trai/test split and
        train the modeol on that data.
        """
        #split data into test train split
        x_train, x_test, y_train, y_test = train_test_split(samples, labels, 
                                                            test_size=0.25, random_state=42)
        print("\n++++ Begin Training ++++\n\n")
        #train model
        self.model.fit(x_train, y_train)
        print("\n\n++++ Training Complete ++++\n\n")
        #print accuracy on test data
        score = self.model.score(x_test,y_test)
        print("On test data, this model was %f accurate.\n\n", score )
        #save model
        self.path = "./weights/" + str(self.name) + "_" + str(score) + ".pkl"
        joblib.dump(self.model, self.path) 

    def prediction(self, vects, model_path):
        """
        Input a list of vectors, these vectors will all get a predicted class from the loaded model
        """
        #load the model form the given input path
        loaded_model = joblib.load(model_path)
        print("\n\n+++++ Model successfully loaded +++++\n\n")
        #for each vector in the list append a prediction to results
        results = [loaded_model.predict(vec) for vec in vects]
        print("\n\n+++++ Results +++++\n\n")
        #print out the results
        print(results)

    def productionize(self, model_path, production_path):
        """
        Saves the specified model to production weights file
        """
        #TODO find the best model score and load/save that one
        #load the specified model
        loaded_model = joblib.load(model_path)
        #save the model to specified path
        joblib.dump(loaded_model,production_path)
        print("\n+++++ Model saved to production path. +++++\n\n %s", production_path)
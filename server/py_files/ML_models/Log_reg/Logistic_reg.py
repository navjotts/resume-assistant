# import relevent modules
# import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib
from glob import glob
from os.path import basename

# Overall class for the logistoc regression model
class Log_reg():
    """ 
    Class used to easily train and logistic regression from SKlearn and then, once trained, 
    the prediciotn mthod can be called to make predcitions from a saved model   
    
    """
    def __init__(self, name):
        self.name = name
        self.path = "server/py_files/ML_models/Log_reg/weights/"
        ## create the acutal model
        self.model = LogisticRegression( random_state=42, max_iter=1000)
        
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
        self.path = "server/py_files/ML_models/Log_reg/weights/" + str(self.name) + "_" + str(int(score*100)) + ".pkl"
        joblib.dump(self.model, self.path) 

        return {'Accuracy': round(score*100,2) , 'Predicitons': [self.model.predict([vec]) for vec in samples], 'Labels': labels}

    def prediction(self, vects, Load_best=True, model_path=None, test=False, labels=None):
        """
        Input a list of vectors, these vectors will all get a predicted class from the loaded modelself.
        If you want to test the model without using train set test to True and supply labels.
        """
        #load model based on inputs
        self.load_model(self.name)
        # for each vector in the list append a prediction to results
        results = [self.model.predict(vec.reshape(1,-1)) for vec in vects]
        print("\n\n+++++ Results +++++\n\n\n\n prediciton:%s\n\n label:%s"%([x[0] for x in results[0:10]],labels[0:10]))
        # print out the results depending on case
        #printout test results with label
        if(test and labels):
            return {'results':results,'labels':labels}
        #raise error since the labels were not provided with the test
        elif(test and not labels):
            raise Exception('Can not enable test mode without supplying labels, Check arguments')
        #just return the predicted results, this is used for inference/production
        else:
         return results

    def productionize(self, model_path, production_path):
        """
        Saves the specified model to production weights file
        """
        # TODO find the best model score and load/save that one
        # load the specified model
        loaded_model = joblib.load(model_path)
        # save the model to specified path
        joblib.dump(loaded_model,production_path)
        print("\n+++++ Model saved to production path. +++++\n\n %s", production_path)

    def load_model(self, name, Load_best=True, model_path=None):
        
        #load best model
        if(Load_best):
       
            best = 0
            best_file = ""

            #find highest accuracy model
            for file in glob("./server/py_files/ML_models/Log_reg/weights/%s*.pkl" %(name) ):
                if(int(file[-6:-4]) > best):
                    best_file = file
                else:
                    next

            try:
                self.model = joblib.load(best_file)
            except:
                raise Exception('Must provide a valid path trained model, starting from /server directory.')

        # load the model form the given input path
        else:
            try:
                self.model = joblib.load(model_path)
            except:
                raise Exception('Must provide a valid path trained model, starting from /server directory.')

        print("\n\n+++++ Model successfully loaded +++++\n\n\t%s" %(basename(best_file)))

        return 0
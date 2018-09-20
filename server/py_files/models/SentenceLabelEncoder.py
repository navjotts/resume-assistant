import numpy as np
class LabelEncoder(object):
    def __init__(self):
        self.catigorical_encoder = {'EDUCATION':[1,0,0,0,0],'EXPERIENCE':[0,1,0,0,0],'PROJECT/SKILL':[0,0,1,0,0],'OTHERS':[0,0,0,1,0], '':[0,0,0,0,1]}
        self.num_encoder =  {'EDUCATION':1,'EXPERIENCE':2,'PROJECT/SKILL':3,'OTHERS':4, '':5}
        self.decoder = ['EDUCATION','EXPERIENCE','PROJECT/SKILL','OTHERS', '']


    def encode_catigorical(self, labels):

       return np.array([self.catigorical_encoder[label] for label in labels])

    def encode_numerical(self, labels):

       return np.array([self.num_encoder[label] for label in labels])

    def decode(self, predicitons):

        return np.array([self.decoder[prediciton-1] for prediciton in predicitons])

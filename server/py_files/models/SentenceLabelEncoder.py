import numpy as np

class SentenceLabelEncoder(object):
    def __init__(self):
        self.categorical_encoder = {
            'EDUCATION':[1, 0, 0, 0],
            'EXPERIENCE':[0, 1, 0, 0],
            'PROJECT/SKILL':[0, 0, 1, 0],
            'OTHERS':[0, 0, 0, 1]
            }
        self.num_encoder =  {
            'EDUCATION': 1,
            'EXPERIENCE': 2,
            'PROJECT/SKILL': 3,
            'OTHERS': 4}
        self.decoder = ['EDUCATION', 'EXPERIENCE', 'PROJECT/SKILL', 'OTHERS']


    def encode_categorical(self, labels):
       return np.array([self.categorical_encoder[label] for label in labels])

    def encode_numerical(self, labels):
       return np.array([self.num_encoder[label] for label in labels])

    def decode(self, predicitons):
        return np.array([self.decoder[int(prediciton)] for prediciton in predicitons])

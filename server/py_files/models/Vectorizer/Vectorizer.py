import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import joblib

class Vectorizer(object):
    def __init__(self, name, vec_type):
        # todo bring in ngram_range as well
        self.name = name
        self.vec_type = vec_type
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + '_' + vec_type + '.pkl')
        self.model = None

    def create_vectorizer(self):
        if self.vec_type == 'tf-idf':
            return TfidfVectorizer(max_df=0.5, min_df=1) # todo max_df and min_df should be hyperparams (and hence we need a CV setup)

        if self.vec_type == 'bow':
            return CountVectorizer()

    def train(self, samples):
        vectorizer = self.create_vectorizer()
        trained = vectorizer.fit(samples)
        joblib.dump(trained, self.path)

    # loads the model from local (if needed)
    def load(self):
        if not self.model:
            self.model = joblib.load(self.path)

        if not self.model:
            print('Vectorizer: error: unable to load model')


    def words_to_sents(self, samples):
        return [(' ').join(s) for s in samples]

    def vectors(self, samples, retrain):
        samples = self.words_to_sents(samples)
        if retrain:
            self.train(samples)

        self.load()
        return self.model.transform(samples)




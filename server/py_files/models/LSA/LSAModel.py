import os

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import mglearn

from py_files.models.Vectorizer.Vectorizer import Vectorizer

class LSAModel(object):
    def __init__(self, name):
        self.name = name
        self.model = None # todo should be a dict => so that we can hold more than 1 models in memory together
        self.seed = 12 # fix the random seed for consistency of results
        np.random.seed(self.seed) # todo => doesn't setting this gets rid of the need of the above? CHECK (then we don't need to set `random_state` everywhere)

    def choose_features(self, samples, retrain=False):
        return Vectorizer(self.name, 'tf-idf').vectors(samples, retrain).toarray() # todense()

    def top_topics(self, samples, num_topics, words_per_topic):
        print(self.name, samples)
        features = self.choose_features(samples)

        lda = LatentDirichletAllocation(n_components=num_topics)
        lda_dtf = lda.fit_transform(features)

        sorting=np.argsort(lda.components_)[:,::-1]
        features=np.array(vect.get_feature_names())

        mglearn.tools.print_topics(topics=range(num_topics), feature_names=features, sorting=sorting,topics_per_chunk=num_topics,n_words=words_per_topic)

        dummy_data = {'resumes': ['Javascript', 'Python', 'MySQL', 'React', 'Git', 'SVN', 'C++', 'manage', 'web', 'development', 'MongoDB', 'lead', 'programming', 'components', 'projects', 'Computer'],
                        'jobs': ['development', 'HTML', 'HTML5', 'Java', 'Javascript', 'C++', 'technical', 'Computer', 'management', 'leadership', 'planning', 'degree', 'projects', 'full-stack']}
        return dummy_data[self.name]
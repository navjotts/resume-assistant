import os

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from py_files.models.Vectorizer.Vectorizer import Vectorizer

class LSAModel(object):
    def __init__(self, name):
        self.name = name
        self.model = None # todo should be a dict => so that we can hold more than 1 models in memory together
        self.seed = 12 # fix the random seed for consistency of results
        np.random.seed(self.seed)

    def top_topics(self, samples, num_topics, words_per_topic):
        vectors = Vectorizer(self.name, 'tf-idf').vectors(samples, False).toarray() # todo try todense()

        lda = LatentDirichletAllocation(n_components=num_topics)
        lda_dtf = lda.fit_transform(vectors) # todo do we need this `lda_dtf` (or we just needed the dtf)

        sorting = np.argsort(lda.components_)[:,::-1]
        features = np.array(Vectorizer(self.name, 'tf-idf').feature_names())
        topics = range(num_topics)

        ret = []
        for i in range(0, 5, num_topics): # todo what is the significance of 5
            these_topics = topics[i: i + num_topics]
            for i in range(words_per_topic):
                ret.extend(features[sorting[these_topics, i]])

        print('top_topics for', self.name)
        print(ret)

        dummy_data = {'resumes': ['Javascript', 'Python', 'MySQL', 'React', 'Git', 'SVN', 'C++', 'manage', 'web', 'development', 'MongoDB', 'lead', 'programming', 'components', 'projects', 'Computer'],
                        'jobs': ['development', 'HTML', 'HTML5', 'Java', 'Javascript', 'C++', 'technical', 'Computer', 'management', 'leadership', 'planning', 'degree', 'projects', 'full-stack']}

        return dummy_data[self.name]
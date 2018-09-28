import os
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

class LSAModel(object):
    def __init__(self, name):
        self.name = name
        self.model = None # todo should be a dict => so that we can hold more than 1 models in memory together
        self.seed = 12 # fix the random seed for consistency of results
        np.random.seed(self.seed) # todo => doesn't setting this gets rid of the need of the above? CHECK (then we don't need to set `random_state` everywhere)

    def top_topics(self, text, num_topics, words_per_topic):
        dummy_data = {'resumes': ['Javascript', 'Python', 'MySQL', 'React', 'Git', 'SVN', 'C++', 'manage', 'web', 'development', 'MongoDB', 'lead', 'programming', 'components', 'projects', 'Computer'],
                        'jobs': ['development', 'HTML', 'HTML5', 'Java', 'Javascript', 'C++', 'technical', 'Computer', 'management', 'leadership', 'planning', 'degree', 'projects', 'full-stack']}
        return dummy_data[self.name]

    def train(input):

        vect = CountVectorizer(ngram_range=(1,1), stop_words='english')
        dtm=vect.fit_transform(input)

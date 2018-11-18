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

    def top_topics(self, doc, num_topics, words_per_topic):
        vectors = Vectorizer(self.name, 'tf-idf').vectors(doc, False).toarray() # todo try todense()

        lda = LatentDirichletAllocation(n_components=num_topics)
        lda_dtf = lda.fit_transform(vectors) # todo do we need this `lda_dtf`? (or we just needed the dtf)

        sorting = np.argsort(lda.components_)[:, ::-1]
        features = np.array(Vectorizer(self.name, 'tf-idf').feature_names())
        topics = range(num_topics)

        selected_topics = []
        for i in range(0, 5, num_topics): # todo what is the significance of 5?
            these_topics = topics[i:i+num_topics]
            for i in range(words_per_topic):
                selected_topics.extend(features[sorting[these_topics, i]])

        for sent in doc:
            for word in sent:
                if word.isupper() and word not in selected_topics:
                    selected_topics.append(word)
        selected_topics = list(filter(lambda each: not each.isdigit(), selected_topics))

        return selected_topics
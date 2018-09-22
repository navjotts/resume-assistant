import os
import multiprocessing
import gensim.models.doc2vec as d2v
from scipy import spatial
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import math

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class SentenceEmbeddings(object):
    def __init__(self, name, dimension):
        self.name = name
        self.dimension = dimension
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + str(dimension) + 'd.txt')
        self.model = None

    def train(self, sentences):
        model = d2v.Doc2Vec(min_count=1,
                            window=7,
                            size=self.dimension,
                            seed=42,
                            workers=multiprocessing.cpu_count())

        sents = self.tagged_sentences(sentences)
        model.build_vocab(sents)

        print(model)

        model.train(sents,
                    total_examples=len(sentences),
                    epochs=100)

        print('saving the model at: %s' % self.path)
        model.save(self.path)

        self.model = model

    def tagged_sentences(self, sentences):
        tagged_sents = []
        for i, sent in enumerate(sentences):
            tagged_sents.append(d2v.TaggedDocument(sent, ["sent_{}".format(i)]))

        print('tagged_sents:', len(tagged_sents))
        return tagged_sents

    # loads the model from local (if needed)
    def load(self):
        if not self.model:
            self.model = d2v.Doc2Vec.load(self.path)

        if not self.model:
            print('Embeddings: error: unable to load model')

    # sents is a list of dicts with 2 keys: 'from' and 'to'
    # where 'from' is the base sentence we want to compare,
    # 'to' is a list of sentences we want to compare our from_sentence to
    # and it returns the best similarity_score the from_sentence can find in its respetive to_sentences
    # score b/w 0 and 1
    def similarity_score(self, groups_of_sents):
        scores = []
        for group in groups_of_sents:
            from_sent = group['from']
            to_sents = group['to']
            if len(to_sents) == 0:
                scores.append(1.0) # if nothing to compare to
            else:
                self.model = d2v.Doc2Vec.load(self.path) # todo this should not be here (leaving for now to match last demo results)
                from_sent_dum = self.model.infer_vector(from_sent)
                from_sent_l2 = math.sqrt(np.dot(from_sent_dum, from_sent_dum))
                group_scores = []
                for sent in to_sents:
                    sent_dum = self.model.infer_vector(sent)
                    sent_l2 = math.sqrt(np.dot(sent_dum, sent_dum))
                    score = np.dot(from_sent_dum, sent_dum) / (from_sent_l2 * sent_l2)
                    # score = spatial.distance.cosine(self.model.infer_vector(from_sent), self.model.infer_vector(sent))
                    # score = cosine_similarity(np.array(self.model.infer_vector(from_sent)).reshape(1,-1), np.array(self.model.infer_vector(sent)).reshape(1,-1))
                    # print('similarity:', self.model.docvecs.n_similarity(from_sent, sent))
                    score = 1 if score > 1 else (0 if score < 0 else score)
                    group_scores.append(score)
                scores.append(max(group_scores))

        return scores
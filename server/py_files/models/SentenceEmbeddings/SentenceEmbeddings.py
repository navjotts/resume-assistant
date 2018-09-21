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
        # with open(self.path, 'w') as f:
        #     f.write('')
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

    def similarity(self, sent1, sents2):
        self.load()
        # print('similarity:', self.model.docvecs.n_similarity(sent1,sent2))
        scores = []
        sent1_dum = self.model.infer_vector(sent1)
        l2_sent1 = math.sqrt(np.dot(sent1_dum, sent1_dum))
        for sent in sents2:
            sent_dum = self.model.infer_vector(sent)
            l2_sent = math.sqrt(np.dot(sent_dum, sent_dum))
            score = np.dot(sent1_dum, sent_dum) / (l2_sent1 * l2_sent)
            # score = spatial.distance.cosine(self.model.infer_vector(sent1), self.model.infer_vector(sent))
            # score = cosine_similarity(np.array(self.model.infer_vector(sent1)).reshape(1,-1), np.array(self.model.infer_vector(sent)).reshape(1,-1))
            if score > 1:
                score = 1
            elif score < 0:
                score = 0

            scores.append(score)
        return scores
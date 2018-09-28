import os
import numpy as np
import math
import multiprocessing

import gensim.models.doc2vec as d2v

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class SentenceEmbeddings(object):
    def __init__(self, name, dimension):
        self.name = name
        self.dimension = dimension
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + str(dimension) + 'd.txt')
        self.model = None
        self.seed = 42
        self.epochs = 100

    def train(self, sentences):
        model = d2v.Doc2Vec(min_count=1,
                            window=7,
                            size=self.dimension,
                            seed=self.seed,
                            workers=multiprocessing.cpu_count())

        sents = self.tagged_sentences(sentences)
        model.build_vocab(sents)

        print(model)

        model.train(sents,
                    total_examples=len(sentences),
                    epochs=self.epochs)

        model.save(self.path)
        print('Saved model to disk...')

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

    def vector(self, sent):
        self.load()
        # Note: infer_vector is a separate iterative process in itself, and is affected by randomness if we don't control it
        # (https://github.com/RaRe-Technologies/gensim/issues/447)
        self.model.random.seed(self.seed)
        return self.model.infer_vector(sent, steps=self.epochs)

    def similarity_score(self, fromsent, tosent, method='gensim'):
        self.load()

        if method == 'custom':
            fromsent_vec = self.vector(fromsent)
            tosent_vec = self.vector(tosent)
            fromsent_l2 = math.sqrt(np.dot(fromsent_vec, fromsent_vec))
            tosent_l2 = math.sqrt(np.dot(tosent_vec, tosent_vec))
            score = np.dot(fromsent_vec, tosent_vec) / (fromsent_l2 * tosent_l2)
        elif method == 'gensim':
            self.model.random.seed(self.seed)
            score = self.model.docvecs.similarity_unseen_docs(self.model, fromsent, tosent, steps=self.epochs)
        else:
            raise Exception('Please provide a similarity scoring method!')

        score = 1 if score > 1 else (0 if score < 0 else score)
        return score

    def group_similarity_score(self, groups_of_sents, method='gensim'):
        '''
            sents is a list of dicts with 2 keys: 'from' and 'to'
            where 'from' is the base sentence we want to compare,
            'to' is a list of sentences we want to compare our from_sentence to
            and it returns the best similarity_score the from_sentence can find in its respetive to_sentences
            score b/w 0 and 1
        '''
        self.load()
        scores = []
        for group in groups_of_sents:
            fromsent = group['from']
            tosents = group['to']
            if len(tosents) == 0:
                scores.append(-1.0) # if nothing to compare to
            else:
                group_scores = []

                if method == 'custom':
                    fromsent_vec = self.vector(fromsent)
                    fromsent_l2 = math.sqrt(np.dot(fromsent_vec, fromsent_vec))
                    for sent in tosents:
                        sent_vec = self.vector(sent)
                        sent_l2 = math.sqrt(np.dot(sent_vec, sent_vec))
                        score = np.dot(fromsent_vec, sent_vec) / (fromsent_l2 * sent_l2)
                        assert score <= 1.0
                        # score = (score + 1)/2
                        score = 0.0 if score < 0 else score
                        group_scores.append(score)
                elif method == 'gensim':
                    for sent in tosents:
                        self.model.random.seed(self.seed) # todo check why do we need to set this each time - shouldn't it just be once the model is loaded (https://github.com/RaRe-Technologies/gensim/issues/447)
                        score = self.model.docvecs.similarity_unseen_docs(self.model, fromsent, sent, steps=self.epochs)
                        assert score <= 1.0
                        # score = (score + 1)/2
                        score = 0.0 if score < 0 else score
                        group_scores.append(score)
                else:
                    raise Exception('Please provide a similarity scoring method!')

                scores.append(max(group_scores))

        return scores
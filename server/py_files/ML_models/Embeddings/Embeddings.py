import os
import multiprocessing
import gensim.models.word2vec as w2v

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Embeddings(object):
    def __init__(self, name, dimension):
        self.name = name
        self.dimension = dimension
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', name + str(dimension) + 'd.txt')
        self.model = None

    def train(self, sentences):
        model = w2v.Word2Vec(min_count=3,
                            window=7,
                            size=self.dimension,
                            seed=42,
                            workers=multiprocessing.cpu_count())

        model.build_vocab(sentences)

        model.train(sentences,
                    total_examples=len(sentences),
                    epochs=10)

        print('saving the model at: %s' % self.path)
        model.wv.save_word2vec_format(self.path, binary = False)

        self.model = model

    def most_similar_by_word(self, word):
        if not self.model:
            print('error: please train/load the model before testing')
            return
        return model.wv.similar_by_word(word)
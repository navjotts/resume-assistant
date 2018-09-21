import os
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

    def similarity(self, sent1, sent2):
        self.load()
        print('similarity:', self.model.wv.similarity(sent1, sent2))
        return self.model.wv.similarity(sent1, sent2)
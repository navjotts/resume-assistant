import os
import multiprocessing
import numpy as np
import pandas as pd
import sklearn.manifold
import gensim.models.word2vec as w2v
from gensim.models import KeyedVectors

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Embeddings(object):
    def __init__(self, name, dimension):
        self.name = name
        self.dimension = dimension
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + str(dimension) + 'd.txt')
        self.model = None
        self.seed = 12

    def train(self, sentences):
        model = w2v.Word2Vec(min_count=1,
                            window=7,
                            size=self.dimension,
                            seed=self.seed,
                            workers=multiprocessing.cpu_count())

        model.build_vocab(sentences)

        print(model)

        model.train(sentences,
                    total_examples=len(sentences),
                    epochs=100)

        model.wv.save_word2vec_format(self.path, binary = False)
        print('Saved model to disk...')

        self.model = model

    # loads the model from local (if needed)
    def load(self):
        if not self.model:
            self.model = KeyedVectors.load_word2vec_format(self.path, binary = False)

        if not self.model:
            print('Embeddings: error: unable to load model')

    # for integration into other ML/DL models
    def vectors(self, model_name='resumes_jobs'): # todo this will change to 'resumes_jobs' once we include jobs data also
        self.load()

        dimension = 100 # we are only using 100 dimensional embeddings for now

        if model_name == 'glove':
            embeddings_dict = dict()
            f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', 'glove.6B.' + str(dimension) + 'd.txt'), encoding ='utf-8' )
            print('using glove model')
            for line in f:
                values = line.split()
                word = values[0]
                if self.word_to_index(word):
                    embedding_vec = np.array(values[1:])
                    embeddings_dict[word] = embedding_vec
            f.close()

            pretrained_vectors = np.zeros((len(self.model.wv.vocab), dimension))
            for word, vocab_object in self.model.wv.vocab.items():
                embedding_vec = embeddings_dict.get(word)
                if embedding_vec is not None:
                    pretrained_vectors[vocab_object.index] = embedding_vec
        else:
            print('using custom pretrained vectors')
            pretrained_vectors = self.model.wv.syn0

        vocab_size, emdedding_size = pretrained_vectors.shape
        print('input dimension of the Embeddings layer (vocab size):', vocab_size)
        print('output dimension of the Embeddings layer (embedding dimensions):', emdedding_size)
        return pretrained_vectors

    def vector(self, word):
        self.load()
        vec = self.model.wv.word_vec(word)
        print(word, vec)
        return vec

    def word_to_index(self, word):
        self.load()
        if word not in self.model.wv.vocab:
            return None

        return self.model.wv.vocab[word].index

    def index_to_word(self, index):
        self.load()
        if index not in self.model.wv.index2word:
            return None

        return self.model.wv.index2word[index]

    # samples is expected to be a list of samples, where each sample is further a list of tokens
    def encode_samples(self, samples):
        self.load()
        encoded_samples = []
        for s in samples:
            encoded = []
            for w in s:
                if self.word_to_index(w):
                    encoded.append(self.word_to_index(w))
            encoded_samples.append(encoded)

        return encoded_samples

    # for testing/comparing trained embeddings
    def most_similar(self, word):
        self.load()
        return self.model.wv.similar_by_word(word)

    # for visualization purposes
    def reduce_dimensionality(self, dimension):
        self.load()
        tsne = sklearn.manifold.TSNE(n_components=dimension, random_state=self.seed)
        word_vectors_reduced = tsne.fit_transform(self.model.wv.syn0)
        return word_vectors_reduced

    # for visualization purposes
    def words_coordinates(self, dimension):
        self.load()
        word_vectors_reduced = self.reduce_dimensionality(dimension)
        words_and_coords = []
        for word in self.model.wv.vocab:
            word_info = self.model.wv.vocab[word]
            coords = word_vectors_reduced[word_info.index]
            words_and_coords.append((word,) + tuple(coords))

        print('words_and_coords', len(words_and_coords))
        points = pd.DataFrame(words_and_coords)
        print(points.head(10))

        outout_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', 'embeddings' + str(dimension) + 'd.csv')
        with open(outout_file, 'w') as f:
            f.write('')
        points.to_csv(outout_file)
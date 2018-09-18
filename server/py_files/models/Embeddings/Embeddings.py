import os
import multiprocessing
import gensim.models.word2vec as w2v
from gensim.models import KeyedVectors
import sklearn.manifold
import pandas as pd
import keras

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Embeddings(object):
    def __init__(self, name, dimension):
        self.name = name
        self.dimension = dimension
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', name + str(dimension) + 'd.txt')
        self.model = None

    def train(self, sentences):
        model = w2v.Word2Vec(min_count=3,
                            window=7,
                            size=self.dimension,
                            seed=42,
                            workers=multiprocessing.cpu_count())

        model.build_vocab(sentences)

        print(model)

        model.train(sentences,
                    total_examples=len(sentences),
                    epochs=100)

        print('saving the model at: %s' % self.path)
        model.wv.save_word2vec_format(self.path, binary = False)

        self.model = model

    # loads the model from local (if needed)
    def load(self):
        if not self.model:
            self.model = KeyedVectors.load_word2vec_format(self.path, binary = False)

        if not self.model:
            print('error: unable to load model')

    # for integration into other ML/DL models
    def keras_embeddings_layer(self, trainable = False):
        self.load()
        embeddings = self.model.wv.get_keras_embedding(train_embeddings = trainable)
        print('input dimension of the Embeddings layer (vocab size):', embeddings.input_dim)
        print('output dimension of the Embeddings layer (embedding dimensions):', embeddings.output_dim)
        print('input length of the Embeddings layer (\'None\' if not fixed size input):', embeddings.input_length)
        return embeddings

    def embedding_vector(self, word):
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

    def index_to_word(self, index):
        self.load()
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
            if encoded:
                encoded_samples.append(encoded)

        return encoded_samples

    # for testing/comparing trained embeddings
    def most_similar(self, word):
        self.load()
        return self.model.wv.similar_by_word(word)

    # for visualization purposes
    def reduce_dimensionality(self, dimension):
        self.load()
        tsne = sklearn.manifold.TSNE(n_components=dimension, random_state=42)
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
        points = pd.DataFrame(words_and_coords, columns=["word", "x", "y"])
        print(points.head(10))

        outout_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained', 'embeddings' + str(dimension) + 'd.csv')
        with open(outout_file, 'w') as f:
            f.write('')
        points.to_csv(outout_file)
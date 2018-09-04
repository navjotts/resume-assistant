import gensim

#train a doc2vec model to be used in the process_sent function
def train_d2v(sentences):
    #TODO
    #create a gensim doc2vec model
    #train it on a large corpus
    #save the model for use in process_sent
    pass

#train a word2vec model to be used in the process_words function
def train_w2v(sentences):
    #TODO
    #create a gensim word2vec model
    #train it on a large corpus
    #save the model for use in process_sent
    pass

def process_words(sentences):
    #TODO
    #Tokenize the sentence into words
    #load the most recent word2vec model 
    #create vector of words
    pass

def process_sent(sentences):
    #TODO
    #load the most recent doc2vec model 
    #create vector of of a given sentence
    pass
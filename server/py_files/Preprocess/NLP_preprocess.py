from gensim.models.doc2vec import Doc2Vec
from gensim.parsing.preprocessing import remove_stopwords
from gensim.parsing.preprocessing import strip_multiple_whitespaces
from gensim.parsing.preprocessing import strip_punctuation
from gensim.summarization.textcleaner import clean_text_by_word
from gensim.models.doc2vec import TaggedDocument

#######################
#first time run will require this on the local machine
# import nltk
# nltk.download('punkt')
#######################

from nltk import word_tokenize


#train a doc2vec model to be used in the process_sent function
def train_d2v(sentences):
    #specify file path
    # fname = "./models/doc2vec.bin"
    fname = "server/py_files/Preprocess/models/doc2vec.model"

    #process incoming sentences
    sentences = [process_sentences(text) for text in sentences]
    #tag "documents"
    sentences = form_tags(sentences)
    #create a gensim doc2vec model
    #train it on a large corpus
    # model = Doc2Vec(sentences, vector_size=5, window=2, min_count=1, workers=4)
    print("\n\n+++++ Started Training of the gensim model +++++\n\n\tThis may take a few momemnts...\n\n++++++++++++++++++++++++++++++++++++++++++++++++")
    model = Doc2Vec(size=50, window=10, min_count=3, workers=11,alpha=0.025, min_alpha=0.010)
    model.build_vocab(sentences)
    model.train(sentences,total_examples=len(sentences), epochs=250)

    model.save(fname)
    print("Gensim model trained on %d sentences." % (len(sentences)))

    return 0

def process_sent(sentences, model = None):
    if(not model):
        #load the most recent doc2vec model 
        model = Doc2Vec.load("server/py_files/Preprocess/models/doc2vec.model")
        print("\n\n+++++ Successfully loaded the Doc2vec model +++++\n")
    
    #process incoming sentences. no need to tag here, that is only for training.
    sentences = [process_sentences(text) for text in sentences]
    #create vector of of a given sentence
    results = [model.infer_vector(sentence) for sentence in sentences]
    # print(results)
    return results

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

def process_sentences(sentences):
    
    text = remove_stopwords(sentences)
    text = text.lower()
    text = strip_punctuation(text)
    text = strip_multiple_whitespaces(text)
    # text = list(clean_text_by_word(text, deacc=True))
    text = word_tokenize(text)
    
    return text

def form_tags(text):

    tagged_documents_list = []
    for i, sent in enumerate(text):
        tagged_documents_list.append(TaggedDocument(sent, ["sent_{}".format(i)]))

    return tagged_documents_list

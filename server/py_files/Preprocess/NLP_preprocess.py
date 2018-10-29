from gensim.models.doc2vec import Doc2Vec
from gensim.parsing.preprocessing import remove_stopwords
from gensim.parsing.preprocessing import strip_multiple_whitespaces
from gensim.parsing.preprocessing import strip_punctuation
from gensim.summarization.textcleaner import clean_text_by_word
from gensim.models.doc2vec import TaggedDocument
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.externals import joblib
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

#######################
#first time run will require this on the local machine
# import nltk
# nltk.download('punkt')
#######################

from nltk import word_tokenize


#train a doc2vec model to be used in the process_sent function
def train_d2v(sentences):
    #specify file path
    fname = "server/py_files/Preprocess/models/doc2vec.model"

    #process incoming sentences
    sentences = [process_sentences(text) for text in sentences]
    #tag "documents"
    sentences = form_tags(sentences)
    #create a gensim doc2vec model
    #train it on a large corpus
    # model = Doc2Vec(sentences, vector_size=5, window=2, min_count=1, workers=4)
    print("\n\n+++++ Started Training of the gensim model +++++\n\n\tThis may take a few momemnts...\n\n++++++++++++++++++++++++++++++++++++++++++++++++")
    model = Doc2Vec(size=50, window=5, min_count=5, workers=10,alpha=0.025, min_alpha=0.010)
    model.build_vocab(sentences)
    model.train(sentences,total_examples=len(sentences), epochs=250)

    model.save(fname)
    print("Gensim model trained on %d sentences." % (len(sentences)))

    return 0

#predict on new sentence using doc2vec
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

#preprocess sentence and tockenize into words
def process_sentences(sentences):

    text = remove_stopwords(sentences)
    text = text.lower()
    text = strip_punctuation(text)
    text = strip_multiple_whitespaces(text)
    try:
         text = word_tokenize(text)
    except:
        raise Exception("need to run lines 13 and 14 for first time run, check file /server/py_files/preprocess/NLP_preprocess.py")

    return text

#create tagged ID objects for the DOC2vec model from gensim
def form_tags(text):
    tagged_documents_list = []
    for i, sent in enumerate(text):
        tagged_documents_list.append(TaggedDocument(sent, ["sent_{}".format(i)]))

    return tagged_documents_list

#TFIDF model with scikit learn
def SK_TFIDF_train(sentences):
    """
    Train TFIDF model to encode sentences, check Sklearn documentation for details
    """
    print("\n\n+++++ Starting TFIDF model training +++++\n")
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(sentences)
    joblib.dump(X_train_counts, "server/py_files/Preprocess/models/BOW.pkl")
    tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
    joblib.dump(tf_transformer, "server/py_files/Preprocess/models/TFIDF.pkl")
    X_train_tf = tf_transformer.transform(X_train_counts)
    print("\n\n+++++ Finished TFIDF model training +++++\n")
    return X_train_tf

#use saved bag of words model and TFIDF model to create sentence vectors
def SK_TFIDF_predict(sentences):
    X_train_counts = joblib.load("server/py_files/Preprocess/models/BOW.pkl")
    tf_transformer = joblib.load("server/py_files/Preprocess/models/TFIDF.pkl")
    print("+++++ Loaded TFIDF Models +++++")
    return tf_transformer.transform(X_train_counts)


def integer_sequence(sentences):
    t = Tokenizer()
    t.fit_on_texts(sentences)
    vocab_size = len(t.word_index) + 1

    # integer encode the documents
    encoded_docs = t.texts_to_sequences(sentences)

    return encoded_docs,vocab_size

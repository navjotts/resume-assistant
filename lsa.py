
from nltk.tokenize import word_tokenize
from gensim.test.utils import get_tmpfile
import gensim 
import glob
import warnings

# Turn off deprecation warnings, some people don't condone this.
warnings.filterwarnings("ignore") 


documents = []

path = '/home/antonio/repos/resume-assistant/server/data/resumes-txt/*.txt'
files = glob.glob(path)
for file in files:
    lines = ''
    with open(file) as f:
        lines = f.read()

    documents.append(lines)

# Create a query document and convert it to tf-idf, this function expects a txt file
def create_query_document(file):
    query_document = ''
    with open(file) as f:
        query_document = f.read()
    
    tokenized_query_document = word_tokenize(query_document)
    query_document_bow = dictionary.doc2bow(tokenized_query_document)
    tf_idf_query_document = tf_idf_model[query_document_bow]
    
    return tf_idf_query_document
    

# Turn each document into a list of tokens
tokenized_documents = [[w.lower() for w in word_tokenize(text)]
            for text in documents]


# Create a dictionary, maps tokens to integers( or indeces )
dictionary = gensim.corpora.Dictionary(tokenized_documents)

# Corpus or list of bag-of-words
corpus = [dictionary.doc2bow(gen_doc) for gen_doc in tokenized_documents]

# Create tf_idf_model, Term frequency; how often the word shows up in the document
tf_idf_model = gensim.models.TfidfModel(corpus)

# Print the number of documents in the corpus and the number of tokens
print(tf_idf_model)
s = 0
for i in corpus:
    s+=len(i)
print(s)

# Necessary because similarities expects a tmp working directory for large datasets (something to do with sharding)
index_tmpfile = get_tmpfile("index")
gensim.test.utils.get_tmpfile

# This object can be used to later compare a new document with documents corpus
similarity_object = gensim.similarities.Similarity(index_tmpfile, tf_idf_model[corpus], num_features=len(dictionary))
print(similarity_object)

# Compare a new document to documents in the corpus, in this case test_resume.txt
test_resume = '/home/antonio/repos/resume-assistant/server/data/resumes-txt/test_resume.txt'
document_similarity = similarity_object[create_query_document(test_resume)]
print('Document similarity, closest document percentage', max(document_similarity))

corpus_tfidf = tf_idf_model[corpus]
lsa_model = gensim.models.lsimodel.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)

# To do-- check if tf_idf_model and tf_idf_corpus are the same thing, 
# Applying LSA, to test_resume.txt
lsa_test_result = lsa_model[create_query_document(test_resume)]
#print('Lsa model topics', lsa_model.print_topics(20))
print("Test resume lsa result, closest document percentage \n", max(lsa_test_result))
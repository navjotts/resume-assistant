
from nltk.tokenize import word_tokenize
import gensim 
import glob


documents = []

path = '/home/antonio/repos/resume-assistant/server/data/resumes-txt/*.txt'
files = glob.glob(path)
for file in files:
    lines = ''
    with open(file) as f:
        lines = f.read()

    documents.append(lines)

gen_docs = [[w.lower() for w in word_tokenize(text)]
            for text in documents]


# Create a dictionary
dictionary = gensim.corpora.Dictionary(gen_docs)

corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]

# Create tf_idf model
tf_idf = gensim.models.TfidfModel(corpus)
corpus_tfidf = tf_idf[corpus]

s = 0
for i in corpus:
    s+=len(i)
print(s)

lsa_model = gensim.models.lsimodel.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)
index = gensim.similarities.MatrixSimilarity(lsa_model[corpus])

print(lsa_model.print_topics(10))
print(index)
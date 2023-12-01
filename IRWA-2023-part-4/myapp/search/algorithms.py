from collections import defaultdict
from nltk.stem import PorterStemmer, LancasterStemmer
from nltk.corpus import stopwords
import math
import collections
import re
import string
from numpy import linalg as la
from collections import defaultdict
import numpy as np
import math


def search_in_corpus(corpus, query, index, tf, idf, dictionary):
    # 1. create create_tfidf_index and Search
    query = build_terms(query)
    first_term = query[0]
    try:
        id = dictionary[first_term]
    except:
        return []
    docs = set(posting[0] for posting in index[id])

    for term in query[1:]:
      try:
        id = dictionary[term]
      except:
        return []
      term_docs = set(posting[0] for posting in index[id])
      docs = docs.union(term_docs)

    docs = list(docs)

    # 2. apply ranking
    ranked_docs, ranked_scores = rank_documents(query, docs, index, idf, tf, dictionary)
    result_docs = []
    for id in ranked_docs:
        result_docs.append(corpus.get(id))
    return result_docs


def build_terms(line):
    stemmer = PorterStemmer()
    stemmer1 = LancasterStemmer()
    stop_words = set(stopwords.words("english"))
    punctuations = string.punctuation

    line =  line.lower() ## Transform in lowercase
    line = re.sub(r'http.*', '',line)
    line = re.sub(r'@\w+', '', line)
    line = re.sub(r'\d+','', line)
    line = re.sub(r'#\w+|[^\x00-\x7F]+|['+ re.escape(punctuations) + ']', ' ',line)
    line=  line.split() ## Tokenize the text to get a list of terms
    line=[x for x in line if x not in stop_words]  ##eliminate the stopwords
    line=[stemmer.stem(word) for word in line] ## perform stemming
    line=[stemmer1.stem(word) for word in line] ## perform stemming
    return line


def create_index_tfidf(corpus, batch_size):
    index = defaultdict(list)
    dictionary = {}
    term_id = 0
    tf = defaultdict(list)
    df = defaultdict(int)
    idf = defaultdict(float)

    num_docs = len(corpus)

    # Process the corpus in batches
    for start in range(0, num_docs, batch_size):
        end = min(start + batch_size, num_docs)
        current_batch = list(corpus.values())[start:end]

        for tweet in current_batch:
            line = tweet.get_description()
            doc_number = tweet.get_id()

            terms = build_terms(line)
            current_page_index = {}

            for position, term in enumerate(terms):
                if term not in dictionary:
                    term_id += 1
                    string_id = "term_id_" + str(term_id)
                    dictionary[term] = string_id
                else:
                    string_id = dictionary[term]
                try:
                    current_page_index[string_id][1].append(position)
                except:
                    current_page_index[string_id] = [doc_number, [position]]

            for term_page, posting_page in current_page_index.items():
                index[term_page].append(posting_page)

            norm = 0
            for term, posting in current_page_index.items():
                norm += len(posting[1]) ** 2
            norm = math.sqrt(norm)

            for term, posting in current_page_index.items():
                tf[term].append(np.round(len(posting[1]) / norm, 4))
                df[term] += 1

    for term in df:
        idf[term] = np.round(np.log(float(num_docs / df[term])), 4)

    return index, tf, df, idf, dictionary

def rank_documents(terms, docs, index, idf, tf, dictionary):

    # I'm interested only on the element of the docVector corresponding to the query terms
    # The remaining elements would became 0 when multiplied to the query_vector
    doc_vectors = defaultdict(lambda: [0] * len(terms)) # I call doc_vectors[k] for a nonexistent key k, the key-value pair (k,[0]*len(terms)) will be automatically added to the dictionary
    query_vector = [0] * len(terms)

    # compute the norm for the query tf
    query_terms_count = collections.Counter(terms)  # get the frequency of each term in the query.

    query_norm = la.norm(list(query_terms_count.values()))

    for termIndex, term in enumerate(terms):  #termIndex is the index of the term in the query
        if dictionary[term] not in index:
            continue
        
        term_id = dictionary[term]

        ## Compute tf*idf(normalize TF as done with documents)
        query_vector[termIndex]= query_terms_count[term] / query_norm*idf[term_id]
        # Generate doc_vectors for matching docs

        for doc_index, (doc, postings) in enumerate(index[term_id]):
            if doc in docs:
                doc_vectors[doc][termIndex] = tf[term_id][doc_index] * idf[term_id]

    # Calculate the score of each doc
    doc_scores=[[np.dot(curDocVec, query_vector), doc] for doc, curDocVec in doc_vectors.items() ]
    doc_scores.sort(reverse=True)
    result_docs = [x[1] for x in doc_scores]
    result_scores = [x[0] for x in doc_scores]

    return result_docs, result_scores

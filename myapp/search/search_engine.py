import random
import time
import numpy as np

from myapp.search.objects import ResultItem, Document
from myapp.search.algorithms import search_in_corpus
from myapp.search.algorithms import create_index_tfidf

def build_demo_results(corpus: dict, search_id):
    """
    Helper method, just to demo the app
    :return: a list of demo docs sorted by ranking
    """
    res = []
    size = len(corpus)
    ll = list(corpus.values())
    for index in range(random.randint(0, 40)):
        item: Document = ll[random.randint(0, size-1)]
        res.append(ResultItem(item.id, item.title, item.description, item.doc_date,
                              "doc_details?id={}&search_id={}&param2=2".format(item.id, search_id), random.random()))

    #for index, item in enumerate(corpus['Id']):
    #     # DF columns: 'Id' 'Tweet' 'Username' 'Date' 'Hashtags' 'Likes' 'Retweets' 'Url' 'Language'
    #     res.append(DocumentInfo(item.Id, item.Tweet, item.Tweet, item.Date,
    #                             "doc_details?id={}&search_id={}&param2=2".format(item.Id, search_id), random.random()))

    # simulate sort by ranking
    res.sort(key=lambda doc: doc.ranking, reverse=True)
    return res


class SearchEngine:
    """educational search engine"""

    def __init__(self, corpus):
        start_time = time.time()
        self.index, self.tf, self.df, self.idf, self.dictionary= create_index_tfidf(corpus, len(corpus))
        print("Total time to create the index: {} seconds".format(np.round(time.time() - start_time, 2)))



    def search(self, search_query, search_id, corpus):
        print("Search query:", search_query)
        results = []
        
        if search_query:
            results = search_in_corpus(corpus, search_query,  self.index, self.tf, self.idf, self.dictionary)
            #results = build_demo_results(corpus, search_id)

        return results

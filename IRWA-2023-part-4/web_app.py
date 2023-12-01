import os
from json import JSONEncoder

# pip install httpagentparser
import httpagentparser  # for getting the user agent as json
import nltk
import numpy as np
import time
import requests
from flask import Flask, render_template, session
from flask import request
from datetime import datetime

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document, StatsDocument, StatsUser, StatsQuery
from myapp.search.search_engine import SearchEngine
from myapp.search.algorithms import build_terms
import myapp.analytics.data_storage as data_storage


# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

# end lines ***for using method to_json in objects ***

# instantiate the Flask application
app = Flask(__name__)

# random 'secret_key' is used for persisting data in secure cookie
app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
# open browser dev tool to see the cookies
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'

# instantiate our in memory persistence
analytics_data = AnalyticsData()

full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)

# load documents corpus into memory.
file_path = path + "/Rus_Ukr_war_data.json"

# file_path = "../../tweets-data-who.json"
start_time = time.time()
corpus = load_corpus(file_path)
print("loaded corpus. first elem:", list(corpus.values())[0])
print("Total time to load the corpus: {} seconds".format(np.round(time.time() - start_time, 2)))

# instantiate our search engine
search_engine = SearchEngine(corpus)


# Home URL "/"
@app.route('/')
def index():
    print("starting home url /...")
    analytics_data.fact_time.append(time.time())

    # flask server creates a session by persisting a cookie in the user's browser.
    # the 'session' object keeps data between multiple requests
    session['some_var'] = "IRWA 2023 home"

    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent)

    response = requests.get('https://api64.ipify.org?format=json').json()
    user_ip = response["ip"]
    agent = httpagentparser.detect(user_agent)
   
    
    response = requests.get(f'https://ipapi.co/{user_ip}/json/').json()
    now = datetime.now()
    dtime = now.strftime("%H:%M:%S")
    date = now.strftime("%Y-%m-%d")
    analytics_data.fact_user.append(StatsUser(user_ip, agent['platform']['name'], agent['os']['name'],agent['browser']['name'], 
                                       response.get("city"),response.get("region"),response.get("country_name"), dtime, date))

    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))

    print(session)

    return render_template('index.html', page_title="Welcome")


@app.route('/search', methods=['POST'])
def search_form_post():
    search_query = request.form['search-query']

    session['last_search_query'] = search_query
    session['query_counter'] = session.get('query_counter', 0) + 1

    search_id = analytics_data.save_query_terms(search_query)

    results = search_engine.search(search_query, search_id, corpus)

    found_count = len(results)
    session['last_found_count'] = found_count
    print(session)

    if search_query in analytics_data.fact_query.keys():
        analytics_data.fact_query[search_query][0] += 1
        analytics_data.fact_query[search_query][1] = found_count
    else:
        analytics_data.fact_query[search_query] = [1, found_count]

    return render_template('results.html', results_list=results, searched = search_query,  page_title="Results", found_counter=found_count)


@app.route('/doc_details', methods=['GET'])
def doc_details():
    # getting request parameters:
    #user = request.args.get('user')

    print("doc details session: ")
    print(session)

    res = session["some_var"]

    print("recovered var from session:", res)

    # get the query string parameters from request
    clicked_doc_id = request.args["id"]
    #p1 = int(request.args["search_id"])  # transform to Integer
    #p2 = int(request.args["param2"])  # transform to Integer
    print("click in id={}".format(clicked_doc_id))

    clicked_tweet = corpus.get(int(clicked_doc_id))

    # store data in statistics table 1
    if clicked_doc_id in analytics_data.fact_clicks.keys():
        analytics_data.fact_clicks[clicked_doc_id] += 1
    else:
        analytics_data.fact_clicks[clicked_doc_id] = 1

    print("fact_clicks count for id={} is {}".format(clicked_doc_id, analytics_data.fact_clicks[clicked_doc_id]))

    return render_template('doc_details.html', clicked_tweet=clicked_tweet)


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """

    docs = []
    docs_query = []
    formatted_duration = 0

    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[int(doc_id)]
        count = analytics_data.fact_clicks[doc_id]
        doc = StatsDocument(row.id, row.title, row.description, row.doc_date, row.url, count)
        docs.append(doc)
    docs.sort(key=lambda doc: doc.count, reverse=True)

    if analytics_data.fact_time:
        end = analytics_data.fact_time[0]
        session_duration = round(time.time() - end,2)
        hours, remainder = divmod(session_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_duration = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

    user = analytics_data.fact_user[0]

    for query in analytics_data.fact_query:
        count = analytics_data.fact_query[query][0]
        found = analytics_data.fact_query[query][1]
        doc = StatsQuery(query, count, found)
        docs_query.append(doc)
        analytics_data.fact_querylen[query+str(count)] = len(build_terms(query))
    docs_query.sort(key=lambda doc: doc.count, reverse=True)

    mean_len = sum(analytics_data.fact_querylen.values())/len(analytics_data.fact_querylen)

    data_storage.save_info(user=user, query_info=docs_query, clicked_docs=docs)

    return render_template('stats.html', clicks_data=docs, user = user, duration = formatted_duration, 
                           query_counter=len(analytics_data.fact_query), query = docs_query, mean_query = mean_len)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    visited_docs = []
    for doc_id in analytics_data.fact_clicks.keys():
        d: Document = corpus[int(doc_id)]
        doc = ClickedDoc(doc_id, d.description, analytics_data.fact_clicks[doc_id])
        visited_docs.append(doc)

    visited_docs.sort(key=lambda doc: doc.counter, reverse=True)
    visited_dash = []
    for doc in visited_docs: 
        visited_dash.append(doc.to_json())

    docs_in_dataset = data_storage.get_ids_from_csv()
    visited_docs = []
    for doc_id in docs_in_dataset:
        d: Document = corpus[int(doc_id)]
        doc = ClickedDoc(doc_id, d.description, docs_in_dataset[doc_id])
        visited_docs.append(doc)

    visited_docs.sort(key=lambda doc: doc.counter, reverse=True)
    visited_dash2 = []
    for doc in visited_docs: 
        visited_dash2.append(doc.to_json())

    return render_template('dashboard.html', visited_docs=visited_dash, visited_docs2=visited_dash2)


@app.route('/sentiment')
def sentiment_form():
    return render_template('sentiment.html')


@app.route('/sentiment', methods=['POST'])
def sentiment_form_post():
    text = request.form['text']
    nltk.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    score = ((sid.polarity_scores(str(text)))['compound'])
    return render_template('sentiment.html', score=score)


if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)

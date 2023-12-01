import pandas as pd

def save_info(user, query_info, clicked_docs):
    
    dataset_path = 'dataset.csv'

    try:
        df_original = pd.read_csv(dataset_path)
    except FileNotFoundError:
        df_original = pd.DataFrame()

    df = pd.DataFrame(columns = ['ip', 'platform', 'browser', 'os', 'city', 'region', 'country', 'time', 'date',
                                'query', 'found',
                                'id','title','description','doc_date', 'url'])

    
    for query in query_info:
        for doc in clicked_docs:
            row = {'ip': user.ip, 'platform':user.platform, 'browser':user.browser, 'os':user.os, 'city': user.city, 
                    'region': user.region, 'country':user.country, 'time':user.time, 'date':user.date,
                    'query': query.query, 'found':query.found,
                    'id':doc.id, 'title': doc.title, 'description':doc.description ,'doc_date':doc.doc_date, 
                    'url':doc.url}
                    
            new_row = pd.DataFrame([row])
            df = pd.concat([df, new_row], ignore_index=True)

    df_updated = pd.concat([df_original,df], ignore_index=True)
    df_updated.to_csv(dataset_path, index=False)

def get_ids_from_csv():
    dataset_path = 'dataset.csv'
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print('Error')

    visited_docs = {}
    for id in df['id']:
        if id in visited_docs:
            visited_docs[id] += 1 
        else:
             visited_docs[id] = 1 

    return visited_docs

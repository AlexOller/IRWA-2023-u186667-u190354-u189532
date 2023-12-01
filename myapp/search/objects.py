import json


class Document:
    """
    Original corpus data as an object
    """

    def __init__(self, id, title, description, doc_date, likes, retweets, url, hashtags):
        self.id = id
        self.title = title
        self.description = description
        self.doc_date = doc_date
        self.likes = likes
        self.retweets = retweets
        self.url = url
        self.hashtags = hashtags

    def get(self, id):
        if self.id == id:
            return self
    def get_description(self):
        return self.description
    
    def get_id(self):
        return self.id
    
    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)


class StatsDocument:
    """
    Original corpus data as an object
    """

    def __init__(self, id, title, description, doc_date, url, count):
        self.id = id
        self.title = title
        self.description = description
        self.doc_date = doc_date
        self.url = url
        self.count = count

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)

class StatsUser:
    def __init__(self, ip, platform, os, browser, city, region, country, time, date):
        self.ip = ip
        self.platform = platform
        self.browser = browser
        self.os = os
        self.city = city
        self.region = region
        self.country = country
        self.time = time
        self.date = date


    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)
    
class StatsQuery:
    def __init__(self, query, count, found):
        self.query = query
        self.found = found
        self.count = count
        
        
    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)
    
    def to_json(self):
        return self.__dict__

class ResultItem:
    def __init__(self, id, title, description, doc_date, url, ranking):
        self.id = id
        self.title = title
        self.description = description
        self.doc_date = doc_date
        self.url = url
        self.ranking = ranking

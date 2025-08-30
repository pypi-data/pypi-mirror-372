from collections import defaultdict
import json

class Request:

    def __init__(self,environ):
        self.queries = defaultdict()
        self.body = {}
        for key , val in  environ.items():
            setattr(self, key.replace(".","_").lower(),val )
    
        if self.query_string:
            req_queries = self.query_string.split("&")

            for query in req_queries:
                query_key , query_val = query.split("=")

                self.queries[query_key] = query_val

        if self.wsgi_input and hasattr(self,'content_length'):
            content_length = int(self.content_length)
            body = self.wsgi_input.read(content_length).decode()
            # print(body)
            self.body = json.loads(body)

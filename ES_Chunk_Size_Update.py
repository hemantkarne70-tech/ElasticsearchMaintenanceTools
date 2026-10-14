import time
import traceback
from elasticsearch import Elasticsearch, helpers

ES_URI = "xxx.xxx.xxx.xxx:9200"

ES_CONFIG = {
    "timeout": 20,
    "max_retries": 5,
    "retry_on_timeout": True,
}

ES_CHUNK_SIZE = 10000

index = "index"


class UpdateHash:

    def __init__(self):
        self.es = Elasticsearch(ES_URI, **ES_CONFIG)

    def processUpdateHash(self):
        lst = []
        try:
            query = {"query":{"bool":{"must":[{"match":{"Weekday":"00"}}],"must_not":[],"should":[]}},"from":0,"size":1000,"sort":[],"aggs":{}}
            records = self.es.search(body=query, index=index)
            print(records['hits']['total'])
            if records['hits']['hits'] == []:
                return
            for counter, record in enumerate(records['hits']['hits']):
                # print(record['_id'])
                es_query = {
                    "_op_type": "update",
                    "_index": index,
                    "_id": record['_id'],
                    "doc":{
                    "Weekday": "Sunday",
                    "Flag": "1"}
                }
                lst.append(es_query)
            helpers.bulk(self.es, actions=lst, chunk_size=ES_CHUNK_SIZE)
            print(len(lst),'record updated')
            time.sleep(2)

        except Exception as e:
            traceback.print_exc()
            print(e, '###########')


if __name__ == '__main__':
    while True:
        obj = UpdateHash()
        obj.processUpdateHash()
        time.sleep(5)
        # break

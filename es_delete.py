import time
import traceback
from elasticsearch import helpers,Elasticsearch

ES_URI = "xxx.xxx.xxx.xxx:9200"
ES_CONFIG = {
    "timeout": 20,
    "max_retries": 5,
    "retry_on_timeout": True,
}
ES_CHUNK_SIZE = 1000
index = "index"

class RECORDS:
    def deleteRecords(self):
        _from = 0
        _size = 100
        try:
            qry = {"query":{"bool":{"must":[{"match":{"Doc_id":"4B40FRF9TX07CBF1B5EBCF2"}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}

            es = Elasticsearch(ES_URI, **ES_CONFIG)
            records = es.search(body=qry, index=index)
            # print(records['hits']['hits'])
            lst = []
            if records['hits']['hits'] == []:
                return
            for record in records['hits']['hits']:
                # print(record,"::::::::::::::",type(record))

                es_query = {
                    "_op_type": "delete",
                    "_index": index,
                    "_id": record['_id'],
                    "doc": record
                }
                lst.append(es_query)
            # print(lst)
            helpers.bulk(es, actions=lst, chunk_size=ES_CHUNK_SIZE)
            print(len(lst),'record deleted')
            time.sleep(2)
            # break

        except Exception as e:
            traceback.print_exc()

if __name__ == '__main__':
    obj = RECORDS()
    obj.deleteRecords()
from elasticsearch import helpers,Elasticsearch

ES_URI = "xxx.xxx.xxx.xxx:9200"
ES_CONFIG = {
		"timeout": 20,
		"max_retries": 5,
		"retry_on_timeout": True,
}

ES_LOAD_BUFFER = 500
ES_CHUNK_SIZE = 10000
ES_MAX_RETRY = 5
ES_INDEX_NAME = "index"

es = Elasticsearch(ES_URI, **ES_CONFIG)
count=0

def update_field():
	_from = 0
	_size = 10000
	while True:
		try:
			body = {"query":{"bool":{"must":[{"exists": {"field": "Doc_Field"}}],"must_not":[]}},"from":_from,"size":_size,"sort":[],"aggs":{}}
			res= es.search(index=ES_INDEX_NAME, body=body)
			if res['hits']['hits'] == []:
				return 0
			lst = []
			for data in res['hits']['hits']:
				es_query = {
								"_op_type": "update",
								"_index": ES_INDEX_NAME,
								"_id": data['_id'],
								"doc": {"Doc_Field": "Updated"}
						}
				lst.append(es_query)
			helpers.bulk(es, raise_on_error=True, actions=lst, chunk_size=ES_CHUNK_SIZE)
			_from += _size
			print("updation done........",_size)
		except Exception as e:
			print(f"Something is wrong {e}")
update_field()

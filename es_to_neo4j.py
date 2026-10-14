import json
from neo4j import GraphDatabase
from elasticsearch import Elasticsearch

NEO_IP = "xxx.xxx.xxx.xxx"
NEO_PORT = "7687"

ES_URI = "xxx.xxx.xxx.xxx:9200"
ES_CONFIG = {
    "timeout": 200,
    "max_retries": 5,
    "retry_on_timeout": True,
}

INDEX_NAME = "index"

es = Elasticsearch(ES_URI, **ES_CONFIG)

driver = GraphDatabase.driver(f"bolt://{NEO_IP}:{NEO_PORT}", encrypted=False)

# Function to ingest data into Neo4j
def ingest_batch_data_to_neo4j(tx, batch_data):
    # Cypher query using UNWIND for batch processing
    query = """
    UNWIND $batchData AS data
    CREATE (n:node)
    SET n = data
    """
    tx.run(query, batchData=batch_data)

# Fetch data from Elasticsearch
def fetch_data_from_es_scroll():
    page = es.search(
        index=INDEX_NAME,
        scroll='2m',  # Keep the search context alive for 2 minutes
        size=1000,  # Number of results per "page"
        body={"query": {"match_all": {}}}
    )
    scroll_id = page['_scroll_id']
    hits = page['hits']['hits']
    while len(hits):
        yield hits
        page = es.scroll(scroll_id=scroll_id, scroll='2m')
        scroll_id = page['_scroll_id']
        hits = page['hits']['hits']
    es.clear_scroll(scroll_id=scroll_id)

# Adjusted process function for batch processing with Scroll API
def process_and_ingest_scroll():
    for hits in fetch_data_from_es_scroll():
        batch_data = []
        for hit in hits:
            data = hit["_source"]
            # Ensure all data properties are primitive types or arrays of primitive types
            # For example, serialize complex objects to JSON strings
            for key, value in data.items():
                if isinstance(value, dict) or isinstance(value, list):  # Adjust based on your data structure
                    data[key] = json.dumps(value)  # Serialize complex types
            batch_data.append(data)
        with driver.session() as session:
            session.write_transaction(ingest_batch_data_to_neo4j, batch_data)

if __name__ == "__main__":
    process_and_ingest_scroll()
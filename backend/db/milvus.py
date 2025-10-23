# db/milvus.py
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from config import COLLECTION_NAME, EMBEDDING_DIM


def connect_milvus():
    connections.connect(alias="default", host="localhost", port="19530")


def create_new_collection():
    if utility.has_collection(COLLECTION_NAME):
        utility.drop_collection(COLLECTION_NAME)
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=10000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
        FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=1000),
    ]
    schema = CollectionSchema(fields=fields, description="Website HTML content chunks")
    collection = Collection(name=COLLECTION_NAME, schema=schema)
    return collection

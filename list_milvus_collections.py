#!/usr/bin/env python3

import os
from pymilvus import MilvusClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_all_collections():
    """List all collections in Milvus"""
    try:
        # Get connection details from environment
        host = os.getenv("MILVUS_HOST", "localhost")
        port = os.getenv("MILVUS_PORT", "19530")
        token = os.getenv("MILVUS_TOKEN")
        
        uri = f"http://{host}:{port}"
        logger.info(f"Connecting to Milvus at: {uri}")
        
        # Try to connect to Milvus
        client = MilvusClient(uri=uri, token=token)
        
        # List all collections
        collections = client.list_collections()
        logger.info(f"Found {len(collections)} collections: {collections}")
        
        # For each collection, get basic info
        for collection_name in collections:
            try:
                logger.info(f"\n--- Collection: {collection_name} ---")
                
                # Get collection description
                desc = client.describe_collection(collection_name)
                logger.info(f"Description: {desc}")
                
                # Try to get count
                try:
                    count = client.query(
                        collection_name=collection_name,
                        filter="id >= 0",
                        output_fields=["count(*)"]
                    )
                    logger.info(f"Entity count: {count}")
                except Exception as e:
                    logger.warning(f"Could not count entities: {e}")
                    
            except Exception as e:
                logger.error(f"Error getting info for collection {collection_name}: {e}")
                
    except Exception as e:
        logger.error(f"Failed to connect to Milvus: {e}")
        logger.info("Milvus might not be running or accessible")

if __name__ == "__main__":
    list_all_collections()

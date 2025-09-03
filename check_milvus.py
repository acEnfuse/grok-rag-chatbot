#!/usr/bin/env python3

import os
from pymilvus import MilvusClient, connections
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_milvus_collections():
    """Check what collections exist in Milvus and their contents"""
    try:
        # Try to connect to Milvus
        client = MilvusClient(uri="http://localhost:19530")
        
        # List all collections
        collections = client.list_collections()
        logger.info(f"Found collections: {collections}")
        
        # Check the HRSD collection specifically
        hrsd_collection = "hrsd"
        if hrsd_collection in collections:
            logger.info(f"Collection '{hrsd_collection}' exists!")
            
            # Get collection info
            collection_info = client.describe_collection(hrsd_collection)
            logger.info(f"Collection info: {collection_info}")
            
            # Count entities
            try:
                count = client.query(
                    collection_name=hrsd_collection,
                    filter="id >= 0",
                    output_fields=["count(*)"]
                )
                logger.info(f"Entity count: {count}")
            except Exception as e:
                logger.warning(f"Could not count entities: {e}")
            
            # Try to get some sample data
            try:
                sample_data = client.query(
                    collection_name=hrsd_collection,
                    filter="id >= 0",
                    limit=5,
                    output_fields=["id", "title", "company", "location"]
                )
                logger.info(f"Sample data: {sample_data}")
            except Exception as e:
                logger.warning(f"Could not get sample data: {e}")
                
        else:
            logger.info(f"Collection '{hrsd_collection}' does not exist")
            
    except Exception as e:
        logger.error(f"Failed to connect to Milvus: {e}")
        logger.info("Milvus might not be running or accessible")

if __name__ == "__main__":
    check_milvus_collections()

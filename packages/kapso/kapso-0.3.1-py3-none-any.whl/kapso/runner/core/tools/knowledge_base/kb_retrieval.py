"""
Implementation of knowledge base retrieval tool.
"""

import logging
from typing import Any, Dict, List, Annotated
from langgraph.prebuilt import InjectedState
from kapso.runner.core.flow_state import State

from langchain.tools import tool
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from kapso.runner.core.persistence import (
    check_collection_exists,
    create_pgvector,
    create_pgvector_from_documents,
)
from kapso.runner.core.tools.knowledge_base.kb_utils import extract_knowledge_base_text

# Create a logger for this module
logger = logging.getLogger(__name__)


@tool
async def kb_retrieval(queries: List[str], knowledge_base_key: str, state: Annotated[State, InjectedState]) -> Dict[str, Any]:
    """
    Retrieve relevant information from a knowledge base based on queries.

    Args:
        queries: List of search queries to find relevant information
        knowledge_base_key: Key to identify which knowledge base to search in
        state: Current state object
        config: Runnable configuration

    Returns:
        Dictionary with results or error message
    """
    try:
        # Ensure we have at least one query
        if not queries:
            return {"error": "No queries provided"}

        # Extract configuration
        node_config = state.get("current_node", {})

        # Extract knowledge base text directly from config
        kb_text = extract_knowledge_base_text(node_config, knowledge_base_key)

        if not kb_text:
            return {"error": f"Knowledge base '{knowledge_base_key}' not found"}

        # Using knowledge_base_key as collection name
        collection_name = knowledge_base_key

        # Create embeddings instance
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

        # Check if collection exists using shared connection
        collection_exists = await check_collection_exists(collection_name)

        # If collection doesn't exist, create it
        if not collection_exists:
            # Create the collection with knowledge base text
            logger.info(f"Creating new vector collection: {collection_name}")

            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter()
            chunks = text_splitter.split_text(kb_text)
            documents = [Document(page_content=chunk) for chunk in chunks]

            # Create vector store from documents using our helper function
            vector_store = await create_pgvector_from_documents(
                documents=documents, embedding=embeddings, collection_name=collection_name
            )
            logger.info(f"Created new vector collection with {len(documents)} documents")
        else:
            # Collection exists, use shared engine to create PGVector
            logger.info(f"Using existing vector collection: {collection_name}")
            vector_store = await create_pgvector(collection_name, embeddings)

        # Now perform the queries
        results = []
        for query in queries:
            logger.info(f"Searching for query: {query}")
            retrieved_docs = await vector_store.asimilarity_search(query, k=3)
            results.extend([doc.page_content for doc in retrieved_docs])

        # Return unique results
        unique_results = list(set(results))
        logger.info(f"Found {len(unique_results)} unique results")
        return {"results": unique_results}

    except Exception as e:
        # Handle errors
        error_message = f"Error during knowledge base retrieval: {str(e)}"
        logger.error(error_message)
        return {"error": error_message}


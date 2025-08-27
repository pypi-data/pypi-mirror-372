import logging
import os
from typing import Tuple, Optional
from dotenv import load_dotenv
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

# Create a logger for this module
logger = logging.getLogger(__name__)

# Cached SQLAlchemy async engine
_async_engine = None


async def check_postgres_connection() -> Tuple[bool, Optional[str]]:
    """
    Check if PostgreSQL is available and properly configured.
    
    Returns:
        Tuple[bool, Optional[str]]: (is_available, error_message)
    """
    postgres_url = os.getenv("POSTGRES_URL")
    
    if not postgres_url:
        return False, "POSTGRES_URL environment variable not set"
    
    try:
        # Try to create a minimal connection pool
        pool = AsyncConnectionPool(
            postgres_url,
            min_size=1,
            max_size=1,
            open=False,
            kwargs={
                "connect_timeout": 5,  # Short timeout for testing
            }
        )
        
        # Try to open the pool
        await pool.open()
        
        # Try to get a connection
        async with pool.connection() as conn:
            # Execute a simple query
            await conn.execute("SELECT 1")
        
        # Clean up
        await pool.close()
        
        return True, None
        
    except ImportError:
        return False, "PostgreSQL driver (psycopg) not installed"
    except Exception as e:
        error_msg = str(e)
        if "could not connect to server" in error_msg:
            return False, "Cannot connect to PostgreSQL server. Is it running?"
        elif "password authentication failed" in error_msg:
            return False, "PostgreSQL authentication failed. Check your credentials."
        elif "database" in error_msg and "does not exist" in error_msg:
            return False, "PostgreSQL database does not exist"
        else:
            return False, f"PostgreSQL connection error: {error_msg}"


async def create_checkpointer():
    """Create an async PostgreSQL checkpointer with connection pool."""
    # Determine if running in multiple workers
    workers = int(os.getenv("WEB_CONCURRENCY", "1"))

    # Create the pool without opening it in the constructor
    # Adjust pool size based on number of workers
    min_size = max(1, int(1 / workers))
    max_size = 2

    pool = AsyncConnectionPool(
        os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/postgres"),
        min_size=min_size,
        max_size=max_size,
        open=False,
        kwargs={
            "autocommit": True,
            "prepare_threshold": 0,
            # Add connection timeout and keepalives to prevent SSL connection closure
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
            # Add application name for logging
            "application_name": os.getenv("APPLICATION_NAME", "kapso_checkpointer"),
        },
    )

    # Open the pool properly using await
    await pool.open()

    # Create the checkpointer with the opened pool
    checkpointer = AsyncPostgresSaver(pool)

    # Initialize the database tables
    await checkpointer.setup()

    # Expose the pool for cleanup purposes
    checkpointer.pool = pool

    return checkpointer


async def get_async_engine():
    """
    Get a cached async SQLAlchemy engine with connection pooling.
    This provides a shared engine for database operations.
    """
    global _async_engine
    if _async_engine is None:
        logger.info("Creating new SQLAlchemy async engine")
        _async_engine = create_async_engine(
            os.getenv("PGVECTOR_CONNECTION_STRING", "postgresql://postgres:postgres@localhost:5432/postgres"),
            pool_size=3,
            max_overflow=5,
            pool_timeout=30,
            pool_recycle=1800,
            echo=False,
            # Add application name for logging
            connect_args={"application_name": os.getenv("APPLICATION_NAME", "kapso_sqlalchemy")},
        )
    return _async_engine


async def check_collection_exists(collection_name: str) -> bool:
    """
    Check if a PGVector collection exists in the database by checking the langchain_pg_collection table.

    Args:
        collection_name: Name of the collection to check

    Returns:
        True if collection exists, False otherwise
    """
    try:
        engine = await get_async_engine()
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT EXISTS (SELECT 1 FROM langchain_pg_collection WHERE name = :name)"),
                {"name": collection_name},
            )
            exists = result.scalar()
            logger.info(f"Collection '{collection_name}' exists: {exists}")
            return exists
    except Exception as e:
        logger.error(f"Error checking if collection exists: {str(e)}")
        return False


async def create_pgvector(collection_name, embeddings, use_jsonb=True):
    """
    Create a PGVector instance with a shared engine.

    Args:
        collection_name: Name of the collection
        embeddings: Embeddings function
        use_jsonb: Whether to use JSONB for metadata

    Returns:
        PGVector instance
    """
    try:
        from langchain_postgres import PGVector

        engine = await get_async_engine()
        logger.info(f"Creating PGVector for collection: {collection_name}")

        return PGVector(
            collection_name=collection_name,
            connection=engine,
            embeddings=embeddings,
            use_jsonb=use_jsonb,
            async_mode=True,
        )
    except Exception as e:
        logger.error(f"Error creating PGVector: {str(e)}")
        raise


async def create_pgvector_from_documents(documents, embedding, collection_name, use_jsonb=True):
    """
    Create a PGVector collection from documents using the shared engine.

    Args:
        documents: List of Document objects
        embedding: Embeddings function
        collection_name: Name of the collection
        use_jsonb: Whether to use JSONB for metadata

    Returns:
        PGVector instance with documents loaded
    """
    try:
        from langchain_postgres import PGVector

        engine = await get_async_engine()

        logger.info(
            f"Creating PGVector collection '{collection_name}' with {len(documents)} documents"
        )

        # Create vector store from documents with our shared engine connection
        return await PGVector.afrom_documents(
            documents=documents,
            embedding=embedding,
            collection_name=collection_name,
            connection=engine,
            use_jsonb=use_jsonb,
        )
    except Exception as e:
        logger.error(f"Error creating PGVector from documents: {str(e)}")
        raise

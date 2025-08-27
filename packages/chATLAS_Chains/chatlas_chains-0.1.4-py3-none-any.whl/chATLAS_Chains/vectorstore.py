import os
import socket
from typing import Optional

from pydantic import SecretStr

from chATLAS_Chains.log import logger
from chATLAS_Embed.EmbeddingModels import SentenceTransformerEmbedding
from chATLAS_Embed.VectorStores import PostgresParentChildVectorStore

# Keeps track of which db is stored where
db_config = {
    "cds_v1": {"hostname": "dbod-chatlas-cds.cern.ch", "port": 6606},  # N.B. different hostname
    "twiki_prod": {"hostname": "dbod-chatlas.cern.ch", "port": 6624},
    "indico_prod_v1": {"hostname": "dbod-chatlas.cern.ch", "port": 6624},
    "atlas_talk_prod": {"hostname": "dbod-chatlas.cern.ch", "port": 6624},
    "mkdocs_prod_v1": {"hostname": "dbod-chatlas.cern.ch", "port": 6624},
}


def check_port_forwarding(host="localhost.cern.ch", port=6624):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex((host, port))  # Returns 0 if connection succeeds
        if result == 0:
            logger.debug(f"Port {port} is forwarded and accessible.")
            return True
        else:
            logger.error(f"Port {port} is NOT accessible.")
            return False


def initialize_vector_store(
    model_path: str, postgres_password: str, db_name: str, port_forwarding: bool = False, use_hf_token: bool = False
) -> PostgresParentChildVectorStore:
    """
    Initialises the connecton to the vector store

    :param model_path: Path to the embedding model
    :param postgres_password: Password for the Postgres database
    :param db_name: Name of the database
    :param port_forwarding: Whether to use port forwarding (use if not on the CERN network)

    :return: Instance of PostgresParentChildVectorStore
    """
    logger.info(f"Instantiating vector store {db_name}")

    # Define the embedding model
    embedding_model = SentenceTransformerEmbedding(model_name=model_path, use_hf_token=use_hf_token)

    if port_forwarding:
        logger.debug("Checking port forwarding")
        server_name = "localhost.cern.ch"

        # check the port is setup properly
        port = db_config[db_name]["port"]
        if not check_port_forwarding(host=server_name, port=port):
            raise ValueError(f"Port forwarding not set up for db {db_name}, port {port}")
    else:
        server_name = db_config[db_name]["hostname"]
        port = db_config[db_name]["port"]
        logger.debug(f"Port forwarding off, connecting to DB from {server_name}")

    connection_string = f"postgresql://admin:{postgres_password}@{server_name}:{port}/{db_name}"

    # Connect to the vector store
    vectorstore = PostgresParentChildVectorStore(connection_string=connection_string, embedding_model=embedding_model)
    # Manually set search hyperparams
    vectorstore.search_hyperparams = """
            SET plan_cache_mode = force_generic_plan;
            """

    # vectorstore.explain_analyse = True
    logger.info("Vector store initialised")

    return vectorstore


class VectorStoreManager:
    """
    Manages vectorstore instances with lazy initialization and caching.
    """

    def __init__(self, model_path: str | None = None, port_forwarding: bool = False, use_hf_token: bool = False):
        self._cache: dict[str, PostgresParentChildVectorStore] = {}

        password = os.getenv("CHATLAS_DB_PASSWORD")
        if password is None:
            raise ValueError("CHATLAS_DB_PASSWORD not set in environment")
        self.postgres_password = SecretStr(password)

        if model_path:
            self.model_path = model_path
        elif os.getenv("CHATLAS_EMBEDDING_MODEL_PATH"):
            self.model_path = os.getenv("CHATLAS_EMBEDDING_MODEL_PATH")
        else:
            raise ValueError(
                "CHATLAS_EMBEDDING_MODEL_PATH not set in environment. Set it or use the model_path argument."
            )

        self.port_forwarding = port_forwarding
        self.use_hf_token = use_hf_token

    def get_vectorstore(self, db_name: str) -> PostgresParentChildVectorStore:
        """
        Get a vectorstore instance for the specified database.
        Uses caching to avoid duplicate initialization.

        Args:
            db_name: Name of the database ('twiki_prod', 'cds_prod_v1', 'indico_prod_v1')

        Returns:
            PostgresParentChildVectorStore instance
        """
        if db_name not in db_config:
            raise ValueError(f"Unknown database: {db_name}. Available: {list(db_config.keys())}")

        # Return cached instance if available
        if db_name in self._cache:
            logger.debug(f"Returning cached vectorstore for {db_name}")
            return self._cache[db_name]

        vectorstore = initialize_vector_store(
            model_path=self.model_path,
            postgres_password=self.postgres_password.get_secret_value(),
            db_name=db_name,
            port_forwarding=self.port_forwarding,
            use_hf_token=self.use_hf_token,
        )

        # Cache the instance
        self._cache[db_name] = vectorstore
        return vectorstore

    def get_all_vectorstores(self) -> list[PostgresParentChildVectorStore]:
        """
        Get all available vectorstores.

        Returns:
            List of all vectorstore instances
        """
        return [self.get_vectorstore(db_name) for db_name in db_config]

    def clear_cache(self):
        """Close and clear all cached vectorstore instances."""
        for db_name, store in list(self._cache.items()):
            if hasattr(store, "close"):
                try:
                    store.close()
                    logger.info(f"Closed vectorstore for {db_name}")
                except Exception as e:
                    logger.warning(f"Error closing vectorstore for {db_name}: {e}")
        self._cache.clear()
        logger.info("Vectorstore cache cleared")


# only initialise on first use
_manager: VectorStoreManager | None = None


def _get_manager() -> VectorStoreManager:
    """
    Initialises the VectorStoreManager with default parameters. For use with the helper functions below.
    """
    global _manager
    if _manager is None:
        _manager = VectorStoreManager()
    return _manager


def get_vectorstore(db_name: str) -> PostgresParentChildVectorStore:
    """Retrieve a single vectorstore using the default instance of VectorStoreManager."""
    return _get_manager().get_vectorstore(db_name)


def get_all_vectorstores() -> list[PostgresParentChildVectorStore]:
    """Retrieve all vectorstores using the default instance of VectorStoreManager."""
    return _get_manager().get_all_vectorstores()


if __name__ == "__main__":
    # Example usage
    try:
        vectorstore = get_vectorstore("cds_v1")
        print(f"Successfully connected to vectorstore: {vectorstore}")
    except ValueError as e:
        print(f"Error: {e}")

    result = vectorstore.search("What is the Drell-Yan dilepton cross section?", k=5)

    print(f"Found {len(result)} documents")

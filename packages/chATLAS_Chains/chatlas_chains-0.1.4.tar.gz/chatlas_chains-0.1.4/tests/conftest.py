"""
vectorstore fixtures for CI/CD
"""

import os

import pytest

from chATLAS_Chains.vectorstore import VectorStoreManager

# gitlab CI, load embedding model from HuggingFace
if os.getenv("GITLAB_PAT"):
    model_path = "joegan/multi-qa-mpnet-base-dot-v1-ATLAS-TALK"
    port_forwarding = False

# local dev, load using environment variables
else:
    model_path = None  # uses CHATLAS_EMBEDDING_MODEL_PATH
    port_forwarding = bool(os.getenv("CHATLAS_PORT_FORWARDING"))

manager = VectorStoreManager(model_path=model_path, port_forwarding=port_forwarding)


@pytest.fixture(scope="session")
def twiki_vectorstore():
    """
    Create a twiki vectorstore fixture for the CI/CD
    """

    vectorstore = manager.get_vectorstore("twiki_prod")

    yield vectorstore

    vectorstore.close()


@pytest.fixture(scope="session")
def mkdocs_vectorstore():
    """
    Create a mkdocs vectorstore fixture for the CI/CD
    """

    vectorstore = manager.get_vectorstore("mkdocs_prod_v1")

    yield vectorstore

    vectorstore.close()


@pytest.fixture(scope="session")
def cds_vectorstore():
    """
    Create a cds vectorstore fixture for the CI/CD
    """

    vectorstore = manager.get_vectorstore("cds_v1")

    yield vectorstore

    vectorstore.close()


@pytest.fixture(scope="session")
def three_vectorstores(twiki_vectorstore, mkdocs_vectorstore, cds_vectorstore):
    """
    Fixture that returns the twiki, mkdocs and CDS vectorstores as a list
    """
    return [twiki_vectorstore, mkdocs_vectorstore, cds_vectorstore]

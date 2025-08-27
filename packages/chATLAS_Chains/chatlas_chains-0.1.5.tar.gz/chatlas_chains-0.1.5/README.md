
# chATLAS_Chains

This package implements and benchmarks various Retrieval Augmented Generation (RAG) chains for use in the [chATLAS](https://chatlas-flask-chatlas.app.cern.ch) project.

## Installation

### From PyPI

```bash
pip install chATLAS-Chains
```

### From source

We recommend using [`uv`](https://docs.astral.sh/uv/)
```bash
cd chATLAS_Chains
uv sync
```

## Environment variables

These are required for the following use cases

1. Using an OpenAI LLM
```bash
export CHATLAS_OPENAI_KEY="your api key"
```

2. Using LLMs via the Groq API
```bash
export CHATLAS_GROQ_BASE_URL="http://cs-513-ml003:3000"
export CHATLAS_GROQ_KEY="your groq api key"
```

**note** The API address is local to the CERN network. If not at CERN, you can forward it like so:
```bash
ssh -L 3000:cs-513-ml003:3000 <LXPLUS_USERNAME>@lxplus.cern.ch
export CHATLAS_GROQ_BASE_URL="http://localhost:3000"
```

## Available Chains
- chains.basic.basic_retrieval_chain
- chains.basic_graph.basic_retrieval_graph
- chains.advanced.advanced_rag

## Postgres

If you want to create a local postgres server, you need to install `psql`. Some instructions to do this on macOS using [homebrew](https://brew.sh) are here:

Software install
```bash
brew install postgresql
brew services start postgresql
brew install pgvector
brew unlink pgvector && brew link pgvector
```

Create a user
```bash
psql -h localhost -U postgres
ALTER USER postgres WITH PASSWORD 'Set_your_password_here';
CREATE EXTENSION IF NOT EXISTS vector;
```
## CHANGELOG

#### 0.1.5

Fix missing `retry_config` argument in `advanced_rag` caused by early PyPI upload

#### 0.1.4

Support for Groq-hosted models

Some new functions that go beyond the "basic RAG" workflow:
- Reciprocal Rerank Fusion `chATLAS_Chains.documents.rrf.reciprocal_rank_fusion`
- Document reranking via the Pinecone API `chATLAS_Chains.documents.rerank.rerank_documents`
- Query rewriting step `chATLAS_Chains.query.query_rewriting.rewrite_query`

These are all usable via the new chain `chATLAS_Chains.chains.advanced.advanced_rag`

Added unit tests to gitlab CI/CD pipeline

#### 0.1.3

Fixing imports

Changed output format of `basic_retrieval_chain` (`docs` key is now a list of `Document` objects, rather than a dict)

Unit tests for `basic_retrieval_chain`

#### 0.1.2

Unit tests

First Langgraph chain

#### 0.1.1

Initial Release

---
## 📄 License

chATLAS_Benchmark is released under Apache v2.0 license.

---

<div align="center">

**Made with ❤️ by the ATLAS Collaboration**

*For questions and support, please [contact](mailto:joseph.caimin.egan@cern.ch)*

</div>
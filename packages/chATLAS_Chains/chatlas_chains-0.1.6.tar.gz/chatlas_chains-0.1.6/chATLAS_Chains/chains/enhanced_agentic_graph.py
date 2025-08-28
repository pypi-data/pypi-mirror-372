"""
Enhanced RAG graph with agentic query planning, document quality assessment, and self-correction


This is sort of a just throw everything at it sort of graph.

You have params in the construction to use (all on by default):

Query Planning, -- Break down complex ATLAS physics questions into sub-questions for better retrieval.
Document Assessment, -- Assess the quality and relevance of retrieved documents
Query Rewriting, -- Rewrite the current query to improve retrieval based on current retrieved sources
Answer Assessment, -- Assess the quality of the generated answer for ATLAS physics questions.
Self Correction -- Refine the answer to improve quality


All of these extra validation steps use the Groq API proxy as these are much faster (and cheaper) than using OpenAI
for these smaller agentic tasks.


The answer rewriting here would break the frontend with the model giving used sources in right response format!
(Note that the prompt in Chains is currently broken for this anyway)


Also doesn't handle things like rate limits on Groq API if it fails
"""

import json
import os
from typing import TypedDict

import requests
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from chATLAS_Chains.llm.model_selection import get_chat_model
from chATLAS_Chains.utils.doc_utils import combine_documents
from chATLAS_Embed import LangChainVectorStore


# Enhanced state definition
class EnhancedGraphState(TypedDict, total=False):
    # Core question fields
    question: str
    original_question: str
    search_kwargs: dict

    # Enhanced query planning fields
    sub_questions: list[str]
    query_keywords: list[str]  # NEW: Key technical terms extracted for exact matching
    atlas_domain: str  # NEW: ATLAS domain category (detector, physics, computing, operations, general)
    current_question_index: int  # Kept for compatibility but may not be used in new implementation

    # Document retrieval and management fields
    retrieved_docs: dict[str, list[Document]]
    merged_docs: list[Document]
    original_k_limit: int  # NEW: Original k parameter to respect document count limits
    context: str

    # Answer generation fields
    answer: str
    final_answer: str

    # Document quality assessment fields
    document_quality_score: float
    needs_query_rewrite: bool
    rewrite_attempt: int
    max_rewrite_attempts: int
    quality_threshold: float

    # Answer quality assessment fields
    answer_quality_score: float
    needs_refinement: bool
    refinement_attempt: int
    max_refinement_attempts: int


def enhanced_retrieval_graph(
    prompt: str,
    vectorstore,
    model_name: str,
    agent_model_name: str = "meta-llama/llama-4-maverick-17b-128e-instruct",
    enable_query_planning: bool = True,
    enable_document_assessment: bool = True,
    enable_answer_assessment: bool = True,
    enable_self_correction: bool = True,
    max_retries: int = 2,
) -> CompiledStateGraph:
    """
    Enhanced RAG retrieval graph with configurable agentic features for ATLAS at CERN.

    Args:
        prompt: str, the prompt to use for the final generation model
        vectorstore: the vectorstore(s) to search
        model_name: str, the name of the model to use for the final response generation
        agent_model_name: str, the name of the model to use for agent operations
        enable_query_planning: bool, whether to enable query decomposition
        enable_document_assessment: bool, whether to enable document quality assessment
        enable_answer_assessment: bool, whether to enable answer quality assessment
        enable_self_correction: bool, whether to enable answer refinement
        max_retries: int, maximum number of retry attempts for query rewriting and answer refinement

    Returns:
        A LangGraph graph that can be executed for enhanced RAG
    """
    # Initialize the models and prompt template
    model = get_chat_model(model_name)
    prompt_template = ChatPromptTemplate.from_template(prompt)

    # Create a list of retrievers from the vectorstore(s)
    if isinstance(vectorstore, list):
        retrievers = [LangChainVectorStore(vector_store=vs) for vs in vectorstore]
    else:
        retrievers = [LangChainVectorStore(vector_store=vectorstore)]

    # Groq API helper function with context window management
    def call_groq_api(messages: list[dict], max_tokens: int = 150, temperature: float = 0.1) -> str:
        """Helper function to call the Groq API through the proxy with context window management."""
        hostname = "localhost" if os.environ.get("CHATLAS_PORT_FORWARDING") else "cs-513-ml003"
        base_url = f"http://{hostname}:3000"
        api_key = os.environ["CHATLAS_GROQ_API_KEY"]

        # Truncate messages if they're too long (keep under ~6000 tokens for safety)
        processed_messages = []
        total_length = 0
        max_content_length = 6000  # Conservative limit for context window

        for message in messages:
            content = message.get("content", "")
            if total_length + len(content) > max_content_length:
                # Truncate the content to fit
                remaining_space = max_content_length - total_length
                if remaining_space > 100:  # Only truncate if we have reasonable space left
                    truncated_content = content[: remaining_space - 50] + "...[truncated]"
                    processed_messages.append({**message, "content": truncated_content})
                break
            else:
                processed_messages.append(message)
                total_length += len(content)

        chat_payload = {
            "messages": processed_messages,
            "max_tokens": max_tokens,
            "model": agent_model_name,
            "temperature": temperature,
            "n": 1,
        }

        try:
            response = requests.post(f"{base_url}/chat", json=chat_payload, headers={"X-API-Key": api_key})
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return ""

    # 1. Enhanced ATLAS Query Planning
    def enhanced_atlas_query_planning(state: EnhancedGraphState) -> EnhancedGraphState:
        """
        ATLAS-specific query planning that understands the domain and creates strategic sub-queries
        while maintaining semantic coherence with the original question.
        """
        question = state["question"]

        if not enable_query_planning:
            return {
                **state,
                "original_question": question,
                "sub_questions": [question],
                "query_keywords": [],
                "atlas_domain": "general",
                "rewrite_attempt": 0,
                "max_rewrite_attempts": max_retries,
                "quality_threshold": 0.4,  # Lowered threshold
                "refinement_attempt": 0,
                "max_refinement_attempts": max_retries,
            }

        # Truncate question if too long for planning
        truncated_question = question[:800] + "..." if len(question) > 800 else question

        planning_prompt = f"""You are an ATLAS experiment query strategist at CERN. Analyze this physics question and create a comprehensive search strategy.

    Original Question: {truncated_question}

    Your task is to:
    1. Identify the ATLAS domain/category
    2. Extract key technical terms that should be searched with quotes for exact matching
    3. Create 2-4 strategic sub-queries that complement (not replace) the original question
    4. Ensure sub-queries cover different aspects needed to fully answer the original question

    ATLAS Domain Categories:
    - detector: Inner Detector, Calorimeters, Muon Spectrometer, Trigger/DAQ
    - physics: Analysis, reconstruction, particles, processes, measurements
    - computing: Software, algorithms, data processing, simulation
    - operations: Running conditions, calibration, monitoring, performance
    - general: Broad ATLAS concepts, overview topics

    Key Technical Terms Guidelines:
    - Put exact technical terms, acronyms, or specific phrases in quotes
    - Examples: "Inner Detector", "Level-1 trigger", "jet reconstruction", "track parameters"
    - Use quotes for detector component names, algorithm names, specific physics objects
    - Don't quote common words like "ATLAS", "physics", "data"

    Sub-query Strategy:
    - Each sub-query should address a different aspect needed for a complete answer
    - Maintain connection to original question's intent
    - Use ATLAS terminology and be specific to subsystems/processes
    - Include complementary perspectives (theory + implementation, calibration + performance, etc.)

    IMPORTANT: Respond with ONLY the JSON object, no additional text before or after.

    {{
        "atlas_domain": "detector|physics|computing|operations|general",
        "key_terms": ["term1", "term2", "term3"],
        "sub_queries": [
            "sub-query 1 with \\"quoted terms\\" where appropriate",
            "sub-query 2 with \\"quoted terms\\" where appropriate", 
            "sub-query 3 with \\"quoted terms\\" where appropriate"
        ],
        "reasoning": "Brief explanation of strategy"
    }}"""

        messages = [{"role": "user", "content": planning_prompt}]
        response = call_groq_api(messages, max_tokens=400, temperature=0.1)

        def extract_json_from_response(response_text: str) -> dict:
            """Extract JSON from response that might have extra text."""
            try:
                # First try direct parsing
                return json.loads(response_text.strip())
            except json.JSONDecodeError:
                # Try to find JSON within the response
                text = response_text.strip()

                # Remove markdown code blocks if present
                if text.startswith("```"):
                    # Find the first newline after ``` to skip the language identifier
                    first_newline = text.find("\n")
                    if first_newline != -1:
                        text = text[first_newline + 1 :]

                # Remove trailing markdown code blocks
                text = text.removesuffix("```")

                text = text.strip()

                # Look for JSON object boundaries
                start_idx = text.find("{")
                if start_idx == -1:
                    raise ValueError("No JSON object found")

                # Find the matching closing brace
                brace_count = 0
                end_idx = -1

                for i in range(start_idx, len(text)):
                    if text[i] == "{":
                        brace_count += 1
                    elif text[i] == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break

                if end_idx == -1:
                    raise ValueError("No complete JSON object found")

                json_text = text[start_idx:end_idx]
                return json.loads(json_text)

        try:
            parsed_response = extract_json_from_response(response)

            atlas_domain = parsed_response.get("atlas_domain", "general")
            key_terms = parsed_response.get("key_terms", [])
            sub_queries = parsed_response.get("sub_queries", [question])

            # Validate sub-queries are reasonable
            if len(sub_queries) > 4:
                sub_queries = sub_queries[:4]
            if len(sub_queries) == 0:
                sub_queries = [question]

            # Validate atlas_domain is one of the expected values
            valid_domains = ["detector", "physics", "computing", "operations", "general"]
            if atlas_domain not in valid_domains:
                atlas_domain = "general"

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Query planning JSON parsing failed: {e}")
            print(f"Raw response: {response[:200]}...")  # Debug info
            # Fallback to original question
            atlas_domain = "general"
            key_terms = []
            sub_queries = [question]

        return {
            **state,
            "original_question": question,
            "sub_questions": sub_queries,
            "query_keywords": key_terms,
            "atlas_domain": atlas_domain,
            "rewrite_attempt": 0,
            "max_rewrite_attempts": max_retries,
            "quality_threshold": 0.4,  # More permissive threshold
            "refinement_attempt": 0,
            "max_refinement_attempts": max_retries,
        }

    # 2. Strategic ATLAS Retrieval
    def strategic_atlas_retrieval(state: EnhancedGraphState) -> EnhancedGraphState:
        """
        Retrieve documents using original question + all sub-queries, then intelligently merge and rank.
        """
        original_question = state["original_question"]
        sub_questions = state.get("sub_questions", [original_question])
        search_kwargs = state.get("search_kwargs", {})

        # Get original k parameter to maintain document count limits
        original_k = search_kwargs.get("k", 10) + search_kwargs.get("k_text", 3)

        # Collect all questions to search
        all_search_queries = [original_question] + [q for q in sub_questions if q != original_question]

        docs_dict = {}
        for i, retriever in enumerate(retrievers):
            all_retrieved_docs = []

            # Search with each query
            for j, query in enumerate(all_search_queries):
                try:
                    docs = retriever.invoke(
                        query,
                        config={"metadata": {"search_kwargs": search_kwargs}},
                    )

                    # Tag docs with their source query and weight
                    for doc in docs:
                        doc.metadata["source_query_index"] = j
                        doc.metadata["source_query"] = query
                        doc.metadata["is_original_query"] = j == 0
                        all_retrieved_docs.append(doc)

                except Exception as e:
                    print(f"Error retrieving for query {j}: {e}")
                    continue

            docs_dict[f"docs_{i}"] = all_retrieved_docs

        return {
            **state,
            "question": original_question,  # Always keep original as main question
            "search_kwargs": search_kwargs,
            "retrieved_docs": docs_dict,
            "original_k_limit": original_k,
        }

    # 3. Intelligent Document Merging and Assessment
    def intelligent_atlas_document_merge_and_assessment(state: EnhancedGraphState) -> EnhancedGraphState:
        """
        Merge documents from all retrievers, remove duplicates, assess quality, and select top-k
        most relevant documents while respecting original k limit.
        """
        docs_dict = state["retrieved_docs"]
        original_question = state["original_question"]
        atlas_domain = state.get("atlas_domain", "general")
        key_terms = state.get("query_keywords", [])
        original_k = state.get("original_k_limit", 10)

        # Collect all documents from all retrievers
        all_docs = []
        for i in range(len(retrievers)):
            if f"docs_{i}" in docs_dict:
                all_docs.extend(docs_dict[f"docs_{i}"])

        if not all_docs:
            return {
                **state,
                "merged_docs": [],
                "document_quality_score": 0.0,
                "needs_query_rewrite": True,
            }

        # Remove exact duplicates based on content
        unique_docs = []
        seen_content = set()

        for doc in all_docs:
            # Create a hash of the content (first 200 chars to handle minor formatting differences)
            content_hash = hash(doc.page_content[:200].strip().lower())
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs.append(doc)

        # If we don't need assessment, just return top-k documents prioritizing original query
        if not enable_document_assessment:
            # Sort to prioritize documents from original query
            unique_docs.sort(
                key=lambda x: (
                    not x.metadata.get("is_original_query", False),
                    x.metadata.get("source_query_index", 999),
                )
            )
            final_docs = unique_docs[:original_k]

            return {
                **state,
                "merged_docs": final_docs,
                "document_quality_score": 1.0,
                "needs_query_rewrite": False,
            }

        # Assess document quality for ATLAS domain
        doc_scores = assess_atlas_document_relevance(unique_docs, original_question, atlas_domain, key_terms)

        # Sort documents by relevance score and original query preference
        scored_docs = list(zip(unique_docs, doc_scores, strict=False))
        scored_docs.sort(
            key=lambda x: (
                -x[1],  # Higher relevance score first
                not x[0].metadata.get("is_original_query", False),  # Original query docs preferred
                x[0].metadata.get("source_query_index", 999),  # Earlier queries preferred
            )
        )

        # Select top documents up to original k limit
        final_docs = [doc for doc, score in scored_docs[:original_k]]

        # Calculate overall quality
        if doc_scores:
            avg_quality = sum(score for _, score in scored_docs[:original_k]) / min(len(scored_docs), original_k)
        else:
            avg_quality = 0.0

        quality_threshold = state.get("quality_threshold", 0.4)
        needs_rewrite = avg_quality < quality_threshold

        return {
            **state,
            "merged_docs": final_docs,
            "document_quality_score": avg_quality,
            "needs_query_rewrite": needs_rewrite,
        }

    # Helper function for document assessment
    def assess_atlas_document_relevance(
        docs: list[Document], question: str, atlas_domain: str, key_terms: list[str]
    ) -> list[float]:
        """
        Assess relevance of documents to ATLAS question using domain-specific criteria.
        Returns a list of relevance scores (0.0 to 1.0) for each document.
        """
        if not docs:
            return []

        # Batch assess documents to reduce API calls
        batch_size = 5
        all_scores = []

        # Truncate question and key terms for API call
        truncated_question = question[:300] + "..." if len(question) > 300 else question
        key_terms_str = ", ".join(f'"{term}"' for term in key_terms[:5])  # Limit for prompt size

        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i : i + batch_size]
            batch_content = ""

            for j, doc in enumerate(batch_docs):
                # Truncate document content to manage context window
                doc_content = doc.page_content[:600] + ("..." if len(doc.page_content) > 600 else "")
                batch_content += f"\n--- Document {j + 1} ---\n{doc_content}"

            assessment_prompt = f"""You are an ATLAS experiment document relevance specialist at CERN. Rate how well each document can help answer this ATLAS {atlas_domain} question.

Question: {truncated_question}
ATLAS Domain: {atlas_domain}
Key Technical Terms: {key_terms_str}

Documents to assess:
{batch_content}

For each document, consider:
- Relevance to the specific ATLAS {atlas_domain} question
- Presence of key technical terms and ATLAS-specific information
- Quality and depth of technical content
- Authority (official ATLAS docs, papers, technical notes vs general content)

Rate each document from 0.0 to 1.0:
- 0.9-1.0: Highly relevant, directly answers question with authoritative ATLAS content
- 0.7-0.8: Very relevant, contains substantial useful ATLAS information
- 0.5-0.6: Moderately relevant, some useful ATLAS content but incomplete
- 0.3-0.4: Somewhat relevant, limited useful information
- 0.0-0.2: Not relevant or no useful ATLAS information

Respond with only the scores as a JSON array: [score1, score2, score3, ...]"""

            messages = [{"role": "user", "content": assessment_prompt}]
            response = call_groq_api(messages, max_tokens=100, temperature=0.1)

            try:
                batch_scores = json.loads(response.strip())
                if isinstance(batch_scores, list) and len(batch_scores) == len(batch_docs):
                    all_scores.extend([float(score) for score in batch_scores])
                else:
                    # Fallback to neutral scores
                    all_scores.extend([0.6] * len(batch_docs))
            except (json.JSONDecodeError, ValueError):
                # Fallback to neutral scores if parsing fails
                all_scores.extend([0.6] * len(batch_docs))

        return all_scores

    # 4. ATLAS Query Rewriting
    def atlas_query_rewriting(state: EnhancedGraphState) -> EnhancedGraphState:
        """
        Rewrite queries with ATLAS domain awareness and better preservation of original intent.
        """
        if not state.get("needs_query_rewrite", False):
            return state

        original_question = state["original_question"]
        current_subqueries = state["sub_questions"]
        atlas_domain = state.get("atlas_domain", "general")
        key_terms = state.get("query_keywords", [])
        rewrite_attempt = state.get("rewrite_attempt", 0)

        # Truncate inputs for API call
        truncated_question = original_question[:300] + "..." if len(original_question) > 300 else original_question
        truncated_subqueries = [q[:200] + "..." if len(q) > 200 else q for q in current_subqueries[:3]]

        rewrite_prompt = f"""You are an ATLAS experiment query optimization specialist. The current search queries didn't retrieve high-quality ATLAS {atlas_domain} documents. 

    Original Question: {truncated_question}
    ATLAS Domain: {atlas_domain}
    Current Sub-queries: {json.dumps(truncated_subqueries)}
    Key Terms: {json.dumps(key_terms[:5])}
    Rewrite Attempt: {rewrite_attempt + 1}

    Improve the search strategy by:
    1. Making queries more specific to ATLAS {atlas_domain} systems/concepts
    2. Adding relevant ATLAS technical terminology in quotes for exact matching
    3. Ensuring queries capture different aspects needed to answer the original question
    4. Staying true to the original question's physics intent

    Create 2-4 improved sub-queries that are more likely to find relevant ATLAS documentation.
    Use quotes around specific technical terms, detector components, algorithm names, etc.

    IMPORTANT: Respond with ONLY the JSON object, no additional text before or after.

    {{
        "improved_subqueries": [
            "improved query 1 with \\"quoted technical terms\\"",
            "improved query 2 with \\"quoted technical terms\\""
        ]
    }}"""

        messages = [{"role": "user", "content": rewrite_prompt}]
        response = call_groq_api(messages, max_tokens=300, temperature=0.1)

        def extract_json_from_response(response_text: str) -> dict:
            """Extract JSON from response that might have extra text."""
            try:
                # First try direct parsing
                return json.loads(response_text.strip())
            except json.JSONDecodeError:
                # Try to find JSON within the response
                text = response_text.strip()

                # Remove markdown code blocks if present
                if text.startswith("```"):
                    # Find the first newline after ``` to skip the language identifier
                    first_newline = text.find("\n")
                    if first_newline != -1:
                        text = text[first_newline + 1 :]

                # Remove trailing markdown code blocks
                text = text.removesuffix("```")

                text = text.strip()

                # Look for JSON object boundaries
                start_idx = text.find("{")
                if start_idx == -1:
                    raise ValueError("No JSON object found")

                # Find the matching closing brace
                brace_count = 0
                end_idx = -1

                for i in range(start_idx, len(text)):
                    if text[i] == "{":
                        brace_count += 1
                    elif text[i] == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break

                if end_idx == -1:
                    raise ValueError("No complete JSON object found")

                json_text = text[start_idx:end_idx]
                return json.loads(json_text)

        try:
            parsed_response = extract_json_from_response(response)
            improved_queries = parsed_response.get("improved_subqueries", current_subqueries)

            # Validate and limit
            if len(improved_queries) > 4:
                improved_queries = improved_queries[:4]
            if len(improved_queries) == 0:
                improved_queries = current_subqueries

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Query rewriting JSON parsing failed: {e}")
            print(f"Raw response: {response[:200]}...")  # Debug info
            # Fallback to current queries if parsing fails
            improved_queries = current_subqueries

        return {
            **state,
            "sub_questions": improved_queries,
            "rewrite_attempt": rewrite_attempt + 1,
            "needs_query_rewrite": False,
        }

    # 5. Process documents (maintains original functionality)
    def process_docs(state: EnhancedGraphState) -> EnhancedGraphState:
        """Process the merged documents into a context string."""
        docs = state["merged_docs"]
        context = combine_documents(docs)
        return {
            **state,
            "context": context,
        }

    # 6. Generate answer
    def generate_answer(state: EnhancedGraphState) -> EnhancedGraphState:
        """Generate an answer using the LLM."""
        original_question = state["original_question"]  # Always use original question
        context = state["context"]

        prompt_input = {"context": context, "question": original_question}

        chain = prompt_template | model
        response = chain.invoke(prompt_input)
        answer = response.content

        return {
            **state,
            "answer": answer,
        }

    # 7. Answer Quality Assessment - ATLAS-specific
    def assess_answer_quality(state: EnhancedGraphState) -> EnhancedGraphState:
        """Assess the quality of the generated answer for ATLAS physics questions."""
        if not enable_answer_assessment:
            return {
                **state,
                "answer_quality_score": 1.0,  # Skip assessment
                "needs_refinement": False,
            }

        answer = state["answer"]
        original_question = state["original_question"]
        context = state["context"]

        # Truncate inputs for API call
        truncated_question = original_question[:300] + "..." if len(original_question) > 300 else original_question
        truncated_answer = answer[:800] + "..." if len(answer) > 800 else answer
        truncated_context = context[:1000] + "..." if len(context) > 1000 else context

        evaluation_prompt = f"""You are an ATLAS experiment answer quality evaluator at CERN. Assess how well this answer addresses the given ATLAS physics question based on the provided ATLAS documentation context.

Original ATLAS Question: {truncated_question}
Answer: {truncated_answer}
Context: {truncated_context}

Rate the answer quality for the ATLAS physics question on a scale of 0.0 to 1.0:
- 1.0: Complete, accurate ATLAS answer, directly addresses the physics question with proper technical details
- 0.7-0.9: Good ATLAS answer, mostly complete with appropriate physics content and minor gaps
- 0.4-0.6: Partial ATLAS answer, some relevant physics information but incomplete or unclear
- 0.0-0.3: Poor answer, doesn't adequately address the ATLAS physics question or contains errors

Consider:
- Does the answer directly address the original ATLAS physics question?
- Is the physics content accurate and appropriately technical?
- Are ATLAS-specific details and terminology used correctly?
- Is the answer complete enough for a physicist working on ATLAS?

Respond with just a number between 0.0 and 1.0."""

        messages = [{"role": "user", "content": evaluation_prompt}]
        response = call_groq_api(messages, max_tokens=50)

        try:
            quality_score = float(response.strip())
        except Exception:
            quality_score = 0.7  # Default good score if parsing fails

        needs_refinement = quality_score < 0.7 and enable_self_correction

        return {
            **state,
            "answer_quality_score": quality_score,
            "needs_refinement": needs_refinement,
        }

    # 8. Answer Refinement - ATLAS-specific
    def refine_answer(state: EnhancedGraphState) -> EnhancedGraphState:
        """Refine the answer to improve quality for ATLAS physics questions."""
        if not state.get("needs_refinement", False) or not enable_self_correction:
            return {**state, "final_answer": state["answer"]}

        original_question = state["original_question"]
        current_answer = state["answer"]
        context = state["context"]

        # Truncate inputs for API call
        truncated_question = original_question[:300] + "..." if len(original_question) > 300 else original_question
        truncated_answer = current_answer[:600] + "..." if len(current_answer) > 600 else current_answer
        truncated_context = context[:1200] + "..." if len(context) > 1200 else context

        refinement_prompt = f"""You are an ATLAS experiment answer refinement specialist at CERN. Improve this answer to better address the ATLAS physics question using the available context from ATLAS documentation.

Original ATLAS Question: {truncated_question}
Current Answer: {truncated_answer}
ATLAS Context: {truncated_context}

Guidelines:
- Make the answer more complete and accurate for ATLAS physics
- Address any gaps in the current answer about ATLAS systems or physics
- Use ATLAS-specific terminology and technical details more effectively
- Ensure the answer directly addresses the original question
- Maintain scientific rigor appropriate for ATLAS physicists
- Include relevant technical details, parameters, or methods when available

Provide the refined answer for the ATLAS physics question:"""

        messages = [{"role": "user", "content": refinement_prompt}]
        refined_answer = call_groq_api(messages, max_tokens=500)

        return {
            **state,
            "answer": refined_answer.strip(),
            "refinement_attempt": state.get("refinement_attempt", 0) + 1,
            "needs_refinement": False,
            "final_answer": refined_answer.strip(),
        }

    # Decision functions for conditional edges
    def should_rewrite_query(state: EnhancedGraphState) -> str:
        """Determine if query should be rewritten based on document quality."""
        if not enable_document_assessment:
            return "process"

        needs_rewrite = state.get("needs_query_rewrite", False)
        rewrite_attempt = state.get("rewrite_attempt", 0)
        max_attempts = state.get("max_rewrite_attempts", max_retries)

        if needs_rewrite and rewrite_attempt < max_attempts:
            return "rewrite"
        else:
            return "process"

    def should_refine_answer(state: EnhancedGraphState) -> str:
        """Determine if answer should be refined."""
        if not enable_answer_assessment or not enable_self_correction:
            return "end"

        needs_refinement = state.get("needs_refinement", False)
        refinement_attempt = state.get("refinement_attempt", 0)
        max_attempts = state.get("max_refinement_attempts", max_retries)

        if needs_refinement and refinement_attempt < max_attempts:
            return "refine"
        else:
            return "end"

    # Build the enhanced graph
    graph = StateGraph(EnhancedGraphState)

    # Add nodes with new function names
    graph.add_node("plan", enhanced_atlas_query_planning)
    graph.add_node("retrieve", strategic_atlas_retrieval)
    graph.add_node("merge_assess", intelligent_atlas_document_merge_and_assessment)

    if enable_document_assessment:
        graph.add_node("rewrite", atlas_query_rewriting)

    graph.add_node("process", process_docs)
    graph.add_node("generate", generate_answer)

    if enable_answer_assessment:
        graph.add_node("assess_answer", assess_answer_quality)

    if enable_self_correction:
        graph.add_node("refine", refine_answer)

    # Define the edges based on enabled features
    graph.add_edge("plan", "retrieve")
    graph.add_edge("retrieve", "merge_assess")

    if enable_document_assessment:
        # Conditional edge: rewrite query if documents are poor quality
        graph.add_conditional_edges("merge_assess", should_rewrite_query, {"rewrite": "rewrite", "process": "process"})

        graph.add_edge("rewrite", "retrieve")  # Loop back to retrieval after rewrite
        graph.add_edge("process", "generate")
    else:
        graph.add_edge("merge_assess", "process")
        graph.add_edge("process", "generate")

    if enable_answer_assessment:
        graph.add_edge("generate", "assess_answer")

        if enable_self_correction:
            # Conditional edge: refine answer if quality is low
            graph.add_conditional_edges("assess_answer", should_refine_answer, {"refine": "refine", "end": END})

            graph.add_edge("refine", "assess_answer")  # Loop back to assessment after refinement
        else:
            graph.add_edge("assess_answer", END)
    else:
        graph.add_edge("generate", END)

    # Set the entry point
    graph.set_entry_point("plan")

    # Compile the graph
    return graph.compile()


if __name__ == "__main__":
    # Example of how to run the enhanced graph
    import os

    os.environ["CHATLAS_EMBEDDING_MODEL_PATH"] = "<PATH TO YOUR EMBEDDING MODEL>"
    os.environ["CHATLAS_OPENAI_KEY"] = "YOUR OPENAI API KEY"
    os.environ["CHATLAS_GROQ_API_KEY"] = "API KEY TO GROQ"
    os.environ["CHATLAS_DB_PASSWORD"] = "<>"

    os.environ["CHATLAS_PORT_FORWARDING"] = "True"

    from chATLAS_Chains.prompt.starters import CHAT_PROMPT_TEMPLATE
    from chATLAS_Chains.vectorstore import get_vectorstore

    graph = enhanced_retrieval_graph(
        prompt=CHAT_PROMPT_TEMPLATE,
        vectorstore=get_vectorstore("twiki_prod"),
        model_name="gpt-4o-mini",
        agent_model_name="meta-llama/llama-4-maverick-17b-128e-instruct",
    )

    ans = graph.invoke(
        {
            "question": "What is the crack veto?",
            "search_kwargs": {
                "k_text": 3,
                "k": 10,
                "date_filter": "01-01-2010",
                "type": ["CDS", "twiki", "Indico"],
            },
        }
    )

    print("Final Answer:", ans.get("final_answer", ans.get("answer")))
    print("Document Quality Score:", ans.get("document_quality_score"))
    print("Answer Quality Score:", ans.get("answer_quality_score"))
    print("Merged Docs Count:", len(ans.get("merged_docs", [])))

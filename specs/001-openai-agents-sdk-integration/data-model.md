# Data Model: OpenAI Agents SDK Integration for RAG System

## Entities

### OpenAIAgent
An OpenAI-compliant agent that follows the official SDK patterns and integrates with RAG tools.

**Attributes:**
- name: String (default: "RAG Assistant")
- instructions: String (system instructions for content-boundary enforcement)
- tools: List[FunctionTool] (including RAGTool)
- model: String (configurable model name)
- model_settings: ModelSettings (configuration for the LLM)

**Relationships:**
- Uses RAGTool for content retrieval
- Interacts with LLMConfiguration for provider selection

### RAGTool
A function tool that wraps the existing retrieval pipeline and provides document chunks to the agent.

**Attributes:**
- name: String ("retrieve_content")
- description: String ("Retrieve relevant content from the textbook based on the user's query")
- parameters: Dict (query: str, context_ids: List[str], mode: str)
- function: Callable (wraps RetrievalService methods)

**Relationships:**
- Wraps RetrievalService for actual retrieval
- Returns RetrievedChunk objects to the agent

### LLMConfiguration
Environment-driven configuration that determines which LLM provider to use (OpenAI or OpenRouter).

**Attributes:**
- provider: String ("openai" | "openrouter")
- openai_api_key: Optional[String]
- openrouter_api_key: Optional[String]
- model_name: String (default model to use)
- temperature: Float (default: 0.7)
- max_tokens: Int (default: 1000)

**Relationships:**
- Configures the OpenAIAgent's model settings
- Determines which API endpoint to use

### RetrievedChunk
Document segments retrieved from the RAG system that serve as the agent's knowledge base.

**Attributes:**
- id: String (unique identifier)
- content: String (the actual content text)
- source_file: String (originating document)
- score: Float (raw semantic similarity score)
- metadata: Dict[String, Any] (additional information)
- relevance_score: Float (comprehensive relevance score)
- context_similarity: Float (similarity to query context)
- is_relevant: Boolean (whether it meets relevance threshold)

**Relationships:**
- Returned by RAGTool to OpenAIAgent
- Used by agent to generate grounded responses

### QueryRequest
Input model for the query endpoint.

**Attributes:**
- query: String (user's question)
- context_ids: List[String] (optional IDs for selected-text mode)
- mode: String ("full_book" | "selected_text")

**Relationships:**
- Processed by OpenAIAgent
- Passed to RAGTool for retrieval

### QueryResponse
Output model for the query endpoint.

**Attributes:**
- answer: String (the agent's response)
- citations: List[String] (source citations)
- confidence: Float (confidence in the response)
- is_confident: Boolean (whether confidence is above threshold)
- sources: List[String] (source documents used)
- boundary_compliance: Float (score for content boundary adherence)
- needs_fact_check: Boolean (whether response needs verification)

**Relationships:**
- Returned by OpenAIAgent processing
- Maintains compatibility with existing API clients

## Validation Rules

### OpenAIAgent Validation
- Must have valid instructions that enforce content boundaries
- Tools must be properly configured with required parameters
- Model name must be supported by the selected provider

### RAGTool Validation
- Query parameter must be non-empty
- Context IDs in selected-text mode must exist in the vector store
- Mode must be either "full_book" or "selected_text"

### LLMConfiguration Validation
- Provider must be either "openai" or "openrouter"
- Required API key must be present for the selected provider
- Model name must be valid for the selected provider

### RetrievedChunk Validation
- Content must not exceed token limits (4096 tokens as per spec)
- Relevance score must be between 0.0 and 1.0
- Source file must be a valid reference

## State Transitions

### Agent Processing Flow
1. QueryRequest received → Agent initialized with tools
2. Agent calls RAGTool → Content retrieved from vector store
3. Agent processes retrieved content → Response generated
4. Response validated for content boundaries → QueryResponse returned

### Tool Execution Flow
1. RAGTool called with parameters → RetrievalService invoked
2. RetrievalService processes query → RetrievedChunk objects created
3. Chunks filtered by relevance → Valid chunks returned to agent
4. Agent uses chunks to generate response → Response validated
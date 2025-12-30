# Data Model: Professional Textbook-Style RAG Chatbot

## Entities

### ConversationSession
- **sessionId**: string (UUID) - Unique identifier for the conversation session
- **createdAt**: datetime - Timestamp when session was created
- **lastAccessed**: datetime - Timestamp of last interaction
- **expiresAt**: datetime - Expiration time for automatic cleanup
- **userId**: string (optional) - Associated user ID if authenticated
- **history**: ConversationTurn[] - Array of conversation exchanges

### ConversationTurn
- **turnId**: string (UUID) - Unique identifier for this turn
- **timestamp**: datetime - When this turn occurred
- **role**: "user" | "assistant" - The participant in this turn
- **content**: string - The actual message content
- **context**: string (optional) - Additional context used for this turn
- **references**: Reference[] (optional) - References provided in this response

### AcademicQuery
- **queryId**: string (UUID) - Unique identifier for the query
- **sessionId**: string - Associated session ID
- **content**: string - The user's query text
- **timestamp**: datetime - When the query was made
- **processedContent**: string (optional) - Cleaned/rephrased query content
- **intent**: string (optional) - Detected user intent from ambiguous input

### TextbookResponse
- **responseId**: string (UUID) - Unique identifier for the response
- **queryId**: string - Associated query ID
- **sessionId**: string - Associated session ID
- **content**: string - The formatted response content
- **structuredContent**: StructuredContent - Parsed structured elements
- **references**: Reference[] - List of references provided
- **timestamp**: datetime - When the response was generated
- **confidence**: number - Confidence score for the response
- **isContextual**: boolean - Whether this response used conversation context

### StructuredContent
- **headings**: string[] - List of headings in the response
- **bulletPoints**: string[] - List of bullet points
- **definitions**: Definition[] - List of definitions provided
- **examples**: Example[] - List of examples provided
- **stepByStep**: StepByStep[] (optional) - Step-by-step explanations if applicable

### Definition
- **term**: string - The term being defined
- **definition**: string - The definition text
- **context**: string (optional) - Context where this definition is relevant

### Example
- **title**: string - Title of the example
- **description**: string - Description of the example
- **code**: string (optional) - Code example if applicable

### StepByStep
- **title**: string - Title of the process being explained
- **steps**: Step[] - Ordered list of steps

### Step
- **stepNumber**: number - The sequence number
- **description**: string - Description of this step
- **example**: string (optional) - Example for this step

### Reference
- **type**: "internal" | "external" - Type of reference
- **title**: string - Title of the reference
- **url**: string - URL to the reference
- **description**: string - Brief description of the reference content
- **relevance**: number (0-1) - How relevant this reference is to the query

### KnowledgeBaseChunk
- **chunkId**: string - Unique identifier for this chunk
- **sourceFile**: string - Source document for this chunk
- **content**: string - The actual content of the chunk
- **metadata**: object - Additional metadata about the chunk
- **sectionTitle**: string (optional) - Title of the section this chunk belongs to
- **references**: Reference[] - References associated with this chunk

## Relationships

```
ConversationSession (1) <---> (0..n) ConversationTurn
ConversationTurn (1) --> (0..1) AcademicQuery (when role="user")
ConversationTurn (1) --> (0..1) TextbookResponse (when role="assistant")
AcademicQuery (1) --> (1) TextbookResponse
TextbookResponse (0..n) --> (0..n) Reference
KnowledgeBaseChunk (0..n) --> (0..n) Reference
```

## Validation Rules

### ConversationSession
- sessionId must be a valid UUID
- createdAt must be before lastAccessed
- expiresAt must be in the future
- history length must not exceed 50 turns (configurable)

### AcademicQuery
- content must not be empty
- timestamp must be set
- processedContent must be set if original content was ambiguous

### TextbookResponse
- content must follow structured format (contain headings, bullet points, or definitions)
- confidence must be between 0 and 1
- references must be provided for concept-based queries
- structuredContent must have at least one element type

### Reference
- url must be a valid URL format
- type must be either "internal" or "external"
- title must not be empty
- relevance must be between 0 and 1

## State Transitions

### ConversationSession
- `active` → `inactive` (when no activity for TTL period)
- `inactive` → `expired` (when expiresAt reached)
- `expired` → `cleaned_up` (when automatic cleanup occurs)

### TextbookResponse
- `generating` → `structured` (when formatting applied)
- `structured` → `validated` (when validation passed)
- `validated` → `delivered` (when sent to user)
# Data Model: RAG Website Ingestion Pipeline

## ContentChunk Entity

**Description**: Represents a piece of text content extracted from a web page, processed, and prepared for embedding generation.

**Attributes**:
- `id`: String (unique identifier, generated as hash of source + content + sequence)
- `content`: String (clean, extracted text content)
- `source_url`: String (original URL where content was found)
- `section_title`: String (title or heading associated with the content)
- `chunk_index`: Integer (sequence number within the source document)
- `embedding`: List[float] (vector representation of the content, optional until generated)
- `metadata`: Dict (additional information like creation timestamp, source file hash)
- `created_at`: DateTime (timestamp when chunk was created)
- `processed_at`: DateTime (timestamp when embedding was generated)

**Validation Rules**:
- `id` must be unique across all chunks
- `content` must not be empty
- `source_url` must be a valid URL format
- `chunk_index` must be non-negative
- `embedding` length must match the Cohere model's output dimension (typically 1024 or 4096)

## IngestionJob Entity

**Description**: Represents a complete ingestion process for a single book or website.

**Attributes**:
- `id`: String (unique identifier for the job)
- `source_url`: String (root URL being ingested)
- `status`: Enum (PENDING, IN_PROGRESS, COMPLETED, FAILED)
- `start_time`: DateTime (when job started)
- `end_time`: DateTime (when job completed/failed)
- `total_pages`: Integer (total number of pages discovered)
- `processed_pages`: Integer (number of pages successfully processed)
- `total_chunks`: Integer (total number of content chunks created)
- `failed_pages`: List[String] (URLs that failed during processing)
- `error_log`: String (summary of errors encountered)

**Validation Rules**:
- `status` must be one of the defined enum values
- `start_time` must be before `end_time` when job is completed
- `processed_pages` must not exceed `total_pages`

## EmbeddingVector Entity

**Description**: Represents a vectorized content chunk stored in Qdrant Cloud with associated metadata.

**Attributes**:
- `id`: String (Qdrant-specific ID, matches ContentChunk.id)
- `vector`: List[float] (the embedding vector values)
- `payload`: Dict (metadata stored with the vector in Qdrant)
  - `content`: String (the original text content)
  - `source_url`: String (original URL of the content)
  - `section_title`: String (title of the section)
  - `chunk_index`: Integer (position in original document)
  - `created_at`: DateTime (when the chunk was created)
- `collection_name`: String (Qdrant collection where vector is stored)

**Validation Rules**:
- `vector` length must match the Cohere model's output dimension
- `payload` must contain required metadata fields
- `id` must match the corresponding ContentChunk.id

## Relationships

- One `IngestionJob` → Many `ContentChunk` instances (one job processes many chunks)
- One `ContentChunk` → One `EmbeddingVector` (each chunk becomes one vector after embedding)

## State Transitions

### IngestionJob Status Transitions:
```
PENDING → IN_PROGRESS → COMPLETED
                    ↘ FAILED
```

- PENDING: Job created, ready to start
- IN_PROGRESS: Pages are being crawled and processed
- COMPLETED: All pages processed successfully
- FAILED: One or more critical errors prevented completion
# Quickstart: RAG Website Ingestion Pipeline

## Prerequisites

- Python 3.11+
- Pip package manager
- Git (for cloning dependencies)

## Setup

### 1. Clone and Navigate to Project

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install requests beautifulsoup4 langchain cohere qdrant-client python-dotenv pytest
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the following:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_HOST=your_qdrant_cluster_url
QDRANT_PORT=6333
BOOK_URL=https://your-docusaurus-book-url.com
CHUNK_SIZE=800
CHUNK_OVERLAP=100
```

## Usage

### Run the Ingestion Pipeline

```bash
python src/main.py --url https://your-book-url.com
```

### Run with Custom Parameters

```bash
python src/main.py --url https://your-book-url.com --chunk-size 1000 --chunk-overlap 200
```

### Run Tests

```bash
pytest tests/
```

## Example

```bash
# Ingest a Docusaurus book
python src/main.py --url https://docs.example-book.com

# The pipeline will:
# 1. Crawl all pages under the provided URL
# 2. Extract clean content from each page
# 3. Chunk content according to specified parameters
# 4. Generate embeddings using Cohere
# 5. Store vectors in Qdrant Cloud with metadata
```

## Troubleshooting

### Common Issues

**API Key Errors**: Verify your Cohere and Qdrant API keys are correct in the `.env` file.

**Crawling Issues**: Check that the provided URL is accessible and follows Docusaurus structure.

**Memory Issues**: For large books, consider reducing chunk size or processing in batches.

### Verify Installation

```bash
python -c "import cohere, qdrant_client; print('Dependencies OK')"
```

## Next Steps

- Check the logs in the console for progress updates
- Verify vectors are stored in your Qdrant Cloud collection
- Use the stored vectors for downstream RAG applications
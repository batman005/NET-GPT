# Net-GPT: AI-Powered NLP-to-SQL Engine for Network Data Analytics using LLMs and RAG

Transform natural language questions into optimized SQL queries for network device data.

## Features

- Natural Language Processing - Ask questions in English
- SQL Generation - Automatic SQL query generation  
- RAG System - Retrieval-Augmented Generation for accuracy
- FAISS Vector Search - Fast semantic search
- Batch Queries - Run multiple queries concurrently
- Component Logging - Detailed logs for each module
- Performance Monitoring - Track query execution times
- Error Tracking - Comprehensive error logs


## DEMO Video
[Screencast from 29-03-26 06:36:34 PM IST.webm](https://github.com/user-attachments/assets/6902f48f-232e-4fc7-97b0-849de375e4a6)




## Architecture

Query Processing Pipeline (9 Steps):

1. Load Database Schema
2. Retrieve RAG Context (FAISS semantic search)
3. Detect Intent (Query type classification)
4. Select Tables (with RAG hints)
5. Select Columns (with validation)
6. Generate SQL (optimized)
7. Validate SQL syntax
8. Explain Query (English explanation)
9. Execute Query & Return Results

## Quick Start

### Prerequisites

- Python 3.10+
- MySQL 5.7+
- Ollama with qwen2.5 and nomic-embed-text models

### Installation

```bash
# Clone or navigate to project
cd Net-GPT-Backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt


```

### Environment Setup

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Update with your configuration:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=network_db
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5
LOG_LEVEL=INFO
```

### Start Ollama

```bash
# Pull required models (one-time setup)
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text

# Start Ollama server
ollama serve
```

### Run Application

```bash
# Start FastAPI server
uvicorn app.main:app --reload
```

API available at:
- Application: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Usage

### Single Query

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/query' \
  -H 'accept: application/json' \
  -H 'x-user-id: Hrithik' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "List all down interfaces grouped by device and location in Ukraine and Congo Country and neighbours ip"
}'
```

### Batch Queries

```bash
curl -X POST "http://localhost:8000/query/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [
      "Show critical alerts",
      "List down interfaces",
      "BGP neighbor status"
    ]
  }'
```

### Response Format

```json
{
  "success": true,
  "question": "List all down interfaces grouped by device and location in Ukraine and Congo Country and neighbours ip",
  "intent": "topology_query",
  "tables": "devices, interfaces, isis_adjacencies, isis_instances, locations, bgp_neighbors",
  "columns": "devices.hostname, devices.device_id, interfaces.interface_name, interfaces.status, locations.country, bgp_neighbors.neighbor_ip",
  "sql": "SELECT \n    d.device_id, \n    d.hostname, \n    d.location_id, \n    l.country, \n    i.interface_name, \n    i.status, \n    ia.neighbor_ip\nFROM \n    devices d\nJOIN \n    interfaces i ON d.device_id = i.device_id\nJOIN \n    isis_adjacencies ia ON i.interface_id = ia.interface_id\nJOIN \n    isis_instances ii ON ia.instance_id = ii.instance_id\nJOIN \n    locations l ON d.location_id = l.location_id\nWHERE \n    (l.country = 'Ukraine' OR l.country = 'Congo') \n    AND i.status = 'down';",
  "explanation": "This query fetches details of network devices in Ukraine or Congo with down interfaces by joining multiple tables that link devices to their locations and interface statuses.\nBased on 1 similar example queries in the knowledge base.",
  "result": {
    "status": "success",
    "data": [
      {
        "device_id": 31,
        "hostname": "router-port jacob-29",
        "location_id": 3,
        "country": "Congo",
        "interface_name": "Gig0/3",
        "status": "DOWN",
        "neighbor_ip": "26.62.225.193"
      },
      {
        "device_id": 42,
        "hostname": "router-new emilyhaven-40",
        "location_id": 4,
        "country": "Ukraine",
        "interface_name": "Gig0/2",
        "status": "DOWN",
        "neighbor_ip": "65.66.167.54"
      },
    ],
    "count": 2
  },
  "error": null,
  "request_id": "REQ-20260329-44GPNU",
  "user_id": "Hrithik"
}
```

## Project Structure

```
Net-GPT-Backend/
├── app/
│   ├── agents/
│   │   ├── intent_agent.py      # Detect query intent
│   │   ├── table_agent.py       # Select tables
│   │   ├── column_agent.py      # Select columns (with validation)
│   │   ├── sql_agent.py         # Generate SQL
│   │   └── explain_agent.py     # Explain queries
│   ├── db/
│   │   ├── mysql_client.py      # MySQL connection pool
│   │   └── schema_loader.py     # Dynamic schema loading
│   ├── llm/
│   │   └── ollama_client.py     # Ollama integration
│   ├── rag/
│   │   ├── schema_config.py     # Schema knowledge base
│   │   ├── embedding_config.py  # Embedding model
│   │   ├── faiss_retriever.py   # FAISS vector store
│   │   └── rag_service.py       # RAG orchestrator
│   ├── routers/
│   │   └── query.py             # API endpoints
│   ├── services/
│   │   ├── pipeline_impl.py     # 9-step pipeline
│   │   └── sql_validator.py     # SQL validation
│   ├── schemas/
│   │   └── query_schemas.py     # Pydantic models
│   ├── utils/
│   │   ├── logger.py            # Component logging
│   │   ├── decorators.py        # Utilities
│   │   ├── prompt_loader.py     # Prompt management
│   │   └── sql_extractor.py     # SQL utilities
│   ├── prompts/                 # LLM prompt templates
│   ├── main.py                  # FastAPI application
│   └── dependencies.py          # Dependency injection
├── logs/
│   ├── pipeline.log             # Query pipeline
│   ├── agents.log               # LLM agents
│   ├── rag.log                  # RAG system
│   ├── db.log                   # Database operations
│   ├── llm.log                  # LLM calls
│   ├── api.log                  # API requests
│   ├── query.log                # Query routes
│   └── error.log                # Errors only

├── requirements.txt
├── .env
├── .env.example
└── pyproject.toml
```

## Logging System

Component-specific logs are created in the `logs/` directory:

### Log Files

- pipeline.log - Query pipeline execution (all 9 steps)
- agents.log - LLM agent operations
- rag.log - RAG system and FAISS search
- db.log - Database operations and schema loading
- llm.log - LLM interactions with Ollama
- api.log - API requests and responses
- query.log - Query router operations
- error.log - Errors only (for quick reference)

### View Logs

```bash
# Watch logs in real-time
tail -f logs/pipeline.log

# Check for errors
grep ERROR logs/error.log

# Search pipeline logs
grep "Selected columns" logs/agents.log
```

## RAG System

Retrieval-Augmented Generation for improved accuracy:

- Embedding Model: nomic-embed-text (768-dimensional vectors)
- Vector Database: FAISS (in-memory, CPU-based)
- Knowledge Base: 11 tables + 9 join patterns + 7 example queries
- Semantic search for table and join pattern retrieval

## Performance Metrics

| Metric | Value |
|--------|-------|
| Single Query | 5-7 seconds |
| Batch Queries (3) | 7-10 seconds (concurrent) |
| Embedding Time | 15-50ms per query |
| FAISS Vector Search | <10ms |
| Error Recovery | Auto-retry with exponential backoff |

## Configuration

### Environment Variables

```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=network_db
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
LOG_LEVEL=INFO
SCHEMA_CACHE_TTL=3600  # Cache database schema for 1 hour
```

### Log Configuration

Edit `app/utils/logger.py`:
```python
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB per file
BACKUP_COUNT = 3                 # Keep 3 rotated files
```

## Testing

### Manual Test Query

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Show all critical alerts"}'
```

### Monitor Execution

```bash
# Watch pipeline logs
tail -f logs/pipeline.log

# Check agent selection
grep "Tables selected" logs/agents.log

# View errors
grep ERROR logs/error.log
```

## Supported Query Types

Alert Queries: "Show critical alerts", "List device warnings"
Device Queries: "Devices with high CPU", "Device inventory"
Interface Queries: "Down interfaces", "Interface traffic"
Topology Queries: "Network topology", "BGP neighbors"
Metrics Queries: "Performance metrics", "Health status"

## Debugging

### Check RAG System

```bash
# Monitor RAG retrieval
grep "Retrieving RAG context" logs/pipeline.log
grep "retrieved" logs/rag.log
```

### Monitor Agent Selection

```bash
# Check column selection
grep "Selected columns" logs/agents.log

# Check SQL generation
grep "Generated SQL" logs/agents.log
```

### Find Issues

```bash
# View all errors
cat logs/error.log

# Check database connection
grep "Database error" logs/db.log
```

## Deployment

### Docker Setup

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

```bash
docker build -t net-gpt .
docker run -p 8000:8000 --env-file .env net-gpt
```

### Production Checklist

- Set LOG_LEVEL=INFO (not DEBUG)
- Configure database credentials in .env
- Setup log rotation and archival
- Use production ASGI server (Gunicorn)
- Monitor logs directory disk usage
- Implement query rate limiting
- Setup error alerting

## Documentation

- API Docs: http://localhost:8000/docs (Swagger UI)
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Contributing

- Follow the existing code structure
- Use get_logger(__name__, component="...") for logging
- Include docstrings for all functions
- Test with LOG_LEVEL=DEBUG enabled
- Clean up logs before committing

## License

MIT License - See LICENSE file

## Tips

- Enable LOG_LEVEL=DEBUG during development
- Check logs/error.log first when queries fail
- Use batch queries endpoint for multiple questions
- Monitor log file sizes to prevent disk issues
- Clear old logs regularly (keep last 7 days)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Query timeout | Set LOG_LEVEL=DEBUG and check logs/agents.log |
| RAG not working | Check logs/rag.log for embedding errors |
| Database connection error | Verify .env credentials and check logs/db.log |
| No logs created | Verify logs/ directory exists and is writable |
| LLM returns invalid columns | Columns are auto-filtered, check logs/agents.log |
| Out of memory | Reduce batch size or restart service |

## Support

For debugging:
1. Check logs/error.log first
2. Enable LOG_LEVEL=DEBUG in .env
3. Reproduce the issue with debug logging
4. Check relevant component log (pipeline, agents, rag, db)
5. Search logs: grep -r "error text" logs/

---

## Remaining (WIP)
1. Frontend for the application.
2. Implementing Caching Mechanism for embedding

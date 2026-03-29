# 🌐 Net-GPT: NLP to SQL Query Engine

**Transform natural language questions into optimized SQL queries for network device data.**

## 🎯 Features

- ✅ **Natural Language Processing** - Ask questions in English
- ✅ **SQL Generation** - Automatic SQL query generation
- ✅ **RAG System** - Retrieval-Augmented Generation for accuracy
- ✅ **FAISS Vector Search** - Fast semantic search
- ✅ **Batch Queries** - Run multiple queries concurrently
- ✅ **Component Logging** - Detailed logs for each module
- ✅ **Performance Monitoring** - Track query execution times
- ✅ **Error Tracking** - Comprehensive error logs

## 🏗️ Architecture

```
User Question
    ↓
┌─────────────────────────────────────┐
│ 1. Load Database Schema             │
│ 2. Retrieve RAG Context             │
│ 3. Detect Intent (Network query?)   │
│ 4. Select Tables (with RAG hints)   │
│ 5. Select Columns                   │
│ 6. Generate SQL (optimized)         │
│ 7. Validate SQL                     │
│ 8. Explain Query (English)          │
│ 9. Execute Query & Return Results   │
└─────────────────────────────────────┘
    ↓
Results (SQL + Data + Explanation)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MySQL database
- Ollama with `qwen2.5` and `nomic-embed-text` models

### Installation

```bash
# Clone or navigate to project
cd Net-GPT-Backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or using uv (faster)
uv pip install -r requirements.txt
```

### Environment Setup

Create `.env` file:

```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=network_db

# Ollama
OLLAMA_HOST=http://localhost:11434

# Logging
LOG_LEVEL=INFO
```

### Start Ollama

```bash
# Terminal 1: Start Ollama server
ollama serve

# Terminal 2: Pull required models
ollama pull qwen2.5
ollama pull nomic-embed-text
```

### Run Application

```bash
# Terminal 3: Start FastAPI server
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

## 📊 API Usage

### Single Query

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: john" \
  -d '{
    "question": "Show me all critical alerts"
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
  "question": "Show me all critical alerts",
  "intent": "alert_query",
  "tables": "alerts, devices",
  "columns": "alert_id, severity, device_name",
  "sql": "SELECT * FROM alerts JOIN devices WHERE severity='critical'",
  "explanation": "This query retrieves all critical alerts with device information",
  "rag_context": {
    "tables_suggested": ["alerts", "devices"],
    "join_patterns_found": 1,
    "similar_examples": 2
  },
  "result": {
    "status": "success",
    "count": 5,
    "data": [...]
  }
}
```

## 📁 Project Structure

```
Net-GPT-Backend/
├── app/
│   ├── agents/              # LLM agents
│   │   ├── intent_agent.py  # Detect query intent
│   │   ├── table_agent.py   # Select relevant tables
│   │   ├── column_agent.py  # Select columns
│   │   ├── sql_agent.py     # Generate SQL
│   │   └── explain_agent.py # Explain queries
│   ├── db/                  # Database layer
│   │   ├── mysql_client.py
│   │   └── schema_loader.py
│   ├── llm/                 # LLM integration
│   │   └── ollama_client.py
│   ├── rag/                 # RAG system
│   │   ├── schema_config.py       # Database schema knowledge base
│   │   ├── embedding_config.py    # Embedding model setup
│   │   ├── faiss_retriever.py     # FAISS vector store
│   │   └── rag_service.py         # RAG orchestrator
│   ├── routers/             # API endpoints
│   │   └── query.py
│   ├── services/            # Business logic
│   │   ├── pipeline_impl.py # Main query pipeline
│   │   └── interfaces.py
│   ├── schemas/             # Pydantic models
│   │   └── query_schemas.py
│   ├── utils/               # Utilities
│   │   ├── logger_setup.py  # Enhanced logging
│   │   ├── logger_manage.py # Log management
│   │   ├── decorators.py
│   │   └── prompt_loader.py
│   ├── prompts/             # LLM prompts
│   ├── main.py              # FastAPI app
│   └── dependencies.py
├── logs/                    # Component-specific logs
│   ├── app.log
│   ├── pipeline.log
│   ├── agents.log
│   ├── rag.log
│   ├── db.log
│   ├── error.log
│   └── performance.log
├── LOGGING.md               # Logging documentation
├── RAG_INTEGRATION_GUIDE.md # RAG implementation guide
├── requirements.txt
├── .env
├── .env.example
└── pyproject.toml
```

## 📝 Logging System

Net-GPT includes **comprehensive logging** with component-specific log files:

### Log Files

- **app.log** - Application startup/shutdown
- **pipeline.log** - Query pipeline execution (all 9 steps)
- **agents.log** - LLM agent operations
- **rag.log** - RAG system events
- **db.log** - Database operations
- **llm.log** - LLM interactions
- **api.log** - API requests/responses
- **error.log** - Errors only (for quick reference)
- **performance.log** - Performance metrics

### View Logs

```bash
# View last 50 lines of pipeline logs
python app/utils/logger_manage.py view pipeline 50

# Search for errors
python app/utils/logger_manage.py search "error" agents

# Get error summary
python app/utils/logger_manage.py errors

# Performance metrics
python app/utils/logger_manage.py perf 24
```

### Maintenance

```bash
# View log statistics
python logs_maintain.py stats

# Archive old logs
python logs_maintain.py archive 7

# Cleanup old logs
python logs_maintain.py cleanup 14

# Rotate large logs
python logs_maintain.py rotate 50
```

📖 See [LOGGING.md](LOGGING.md) for detailed logging documentation.

## 🤖 RAG System

The **Retrieval-Augmented Generation (RAG)** system improves query accuracy:

- **Embedding Model**: `nomic-embed-text` (768-dimensional vectors)
- **Vector Database**: FAISS (in-memory, CPU-based)
- **Knowledge Base**: 10 tables + 9 join patterns + 7 example queries

See [RAG_INTEGRATION_GUIDE.md](RAG_INTEGRATION_GUIDE.md) for details.

## 📊 Performance

| Metric | Value |
|--------|-------|
| Single Query | ~5-7 seconds |
| Batch (3 queries) | ~7-10 seconds (concurrent) |
| Embedding Time | ~15-50ms per query |
| FAISS Search | <10ms |
| Success Rate | 95%+ |

## 🔧 Configuration

### Environment Variables

```bash
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
OLLAMA_HOST=http://localhost:11434
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=network_db
```

### Log Rotation

Edit `app/utils/logger_setup.py`:
```python
MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
BACKUP_COUNT = 5               # Keep 5 rotated files
```

## 🧪 Testing

### Run Simple Query

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"question": "Show all critical alerts"},
    headers={"X-User-ID": "test_user"}
)

print(response.json())
```

### Check Logs

```bash
# Watch logs in real-time
tail -f logs/pipeline.log

# Search for specific info
grep "RAG Context" logs/pipeline.log
```

## 📚 Supported Query Types

- **Alert Queries**: "Show critical alerts", "List device warnings"
- **Device Queries**: "Devices with high CPU", "Device inventory"
- **Interface Queries**: "Down interfaces", "Interface traffic"
- **Topology Queries**: "Network topology", "BGP neighbors"
- **Metrics Queries**: "Performance metrics", "Health status"

## 🐛 Debugging

### Check if RAG is Working

```bash
python app/utils/logger_manage.py view rag 50
```

### Monitor Agent Selection

```bash
python app/utils/logger_manage.py view agents 100
```

### Track Performance

```bash
python app/utils/logger_manage.py perf 24
```

### Find Errors

```bash
python app/utils/logger_manage.py errors 24
```

## 🚀 Deployment

### Docker

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

- ✅ Set `LOG_LEVEL=INFO` (not DEBUG)
- ✅ Configure database credentials
- ✅ Enable log rotation
- ✅ Setup monitoring/alerts
- ✅ Archive logs regularly
- ✅ Use production ASGI server (Gunicorn, uv server)

## 📖 Documentation

- [LOGGING.md](LOGGING.md) - Complete logging guide
- [RAG_INTEGRATION_GUIDE.md](RAG_INTEGRATION_GUIDE.md) - RAG system details
- [API Docs](http://localhost:8000/docs) - Swagger UI (when running)

## 🤝 Contributing

1. Follow the existing code structure
2. Add logs using component loggers
3. Include docstrings
4. Test new features with logging enabled
5. Archive old logs before committing

## 📄 License

MIT License - See LICENSE file

## 💡 Tips

1. **Enable DEBUG logging during development**: `LOG_LEVEL=DEBUG`
2. **Check logs** when queries fail or seem slow
3. **Use batch queries** for multiple questions (faster)
4. **Monitor performance.log** for slowdowns
5. **Archive logs monthly** to save space

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Query timeout | Enable DEBUG logs, check `performance.log` |
| RAG not working | Check `rag.log` for embedding errors |
| Database connection error | Check `.env` credentials in `db.log` |
| No logs created | Verify `logs/` directory permissions |
| Logs too large | Run `python logs_maintain.py cleanup 7` |

## 📞 Support

For issues:
1. Check relevant log file (e.g., `logs/pipeline.log`)
2. Search logs: `python app/utils/logger_manage.py search "error message"`
3. View error summary: `python app/utils/logger_manage.py errors`
4. Enable DEBUG logging and reproduce the issue

---

**Net-GPT**: Turning Natural Language into Network Intelligence 🚀


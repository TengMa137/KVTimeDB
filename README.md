
# KVTimeDB 🗄️

**KVTimeDB** is a Python-based key-value **time-series database** designed for **high-performance storage and retrieval** of sequential data. Ideal for backend applications, analytics pipelines, and AI projects needing fast data access. 
API service for storing and retrieving key-value pairs with timestamp-based queries.


## Features
- Optimized for **time-series data**
- Fast **read/write operations**
- Simple and intuitive Python API
- Easily integrable into **backend systems** and **AI pipelines**

## Technologies
- **Languages**: Python
- **Database Concepts**: Key-Value, Time-Series, ETL
- **Tools**: Git, PyTest
- Can integrate with **AI/ML pipelines** or backend services


## Setup and Run

First clone this repo.
### Using uv

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

#### Run the application
```bash
uv sync
uv run python app/main.py
```

### Using pip/conda

#### Prerequisites
- Python 3.13 (tested)
- pip or conda

#### Setup
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -e .

python app/main.py
```

#### Alternative with conda
```bash
# Create conda environment
conda create -n your-project-name python=3.13
conda activate your-project-name

# Install dependencies
pip install -e .

# Run the application
python app/main.py
```

### Using docker
```bash
docker-compose up --build
```

The server will start on `http://localhost:8080`

## API Usage

### Store a value (PUT)
```bash
curl -X PUT http://localhost:8080 \
  -H 'Content-Type: application/json' \
  -d '{"key": "{key}", "value": "{value}", "timestamp": {timestamp}}'
```

**Example:**
```bash
curl -X PUT http://localhost:8080 \
  -H 'Content-Type: application/json' \
  -d '{"key": "user0", "value": "John Doe", "timestamp": 1673524092123456}'
```

### Retrieve a value (GET)
```bash
curl -X GET http://localhost:8080 \
  -H 'Content-Type: application/json' \
  -d '{"key": "{key}", "timestamp": {timestamp}}'
```

**Example:**
```bash
curl -X GET http://localhost:8080 \
  -H 'Content-Type: application/json' \
  -d '{"key": "user0", "timestamp": 1673524092123456}'
```

## Timestamp-Based Queries

The system supports temporal queries where:
- A request returns the most recent value at or before the given timestamp
- If no value exists at or before the timestamp, `null` is returned

Example sequence:
```json
[
  {"key": "item1", "timestamp": 100, "value": "iPhone 16"},
  {"key": "item1", "timestamp": 101, "value": "iPhone 17"}
]
```

Query results for `item1`:
- `timestamp: 99` → returns `null`
- `timestamp: 100` → returns `"iPhone 16"`
- `timestamp: 101` → returns `"iPhone 17"`
- `timestamp: 102` → returns `"iPhone 17"`

## Considerations for Concurrency

- **ACID Transactions**: SQLite's built-in transaction system ensures consistency
- **WAL Mode**: Enables multiple concurrent readers with single writer
- **Connection Timeout**: 10-second timeout prevents indefinite blocking
- **Thread-local connections**: Each thread gets its own database connection
- **Graceful busy handling**: Returns 503 status for temporary unavailability

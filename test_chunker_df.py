import pandas as pd
from markdown_chunker import MarkdownChunker
import json
from pathlib import Path

def create_sample_dataframe():
    """Create a sample DataFrame with various markdown content."""
    data = {
        'filename': [
            'api_docs.md',
            'user_guide.md',
            'tutorial.md',
            'architecture.md',
            'deployment.md'
        ],
        'filepath': [
            '/docs/api/api_docs.md',
            '/docs/guides/user_guide.md',
            '/docs/tutorials/tutorial.md',
            '/docs/architecture/architecture.md',
            '/docs/deployment/deployment.md'
        ],
        'filecontent': [
            """# API Documentation

## Authentication
To authenticate with our API, you need to include your API key in the request header:

```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}

response = requests.get('https://api.example.com/v1/users', headers=headers)
```

## Endpoints

### Users API
| Endpoint | Method | Description |
|----------|--------|-------------|
| /users | GET | List all users |
| /users/{id} | GET | Get user details |
| /users | POST | Create new user |

### Products API
| Endpoint | Method | Description |
|----------|--------|-------------|
| /products | GET | List all products |
| /products/{id} | GET | Get product details |

## Rate Limiting
Our API implements rate limiting to ensure fair usage. Each client is limited to:
- 100 requests per minute
- 1000 requests per hour

## Error Handling
Common error codes and their meanings:

| Code | Description | Resolution |
|------|-------------|------------|
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Verify resource exists |
| 429 | Too Many Requests | Respect rate limits |
""",
            """# User Guide

## Getting Started
Welcome to our platform! This guide will help you get started.

### Installation
1. Download the package
2. Install dependencies
3. Configure your settings

### Configuration
```yaml
# config.yaml
api_key: YOUR_API_KEY
endpoint: https://api.example.com
timeout: 30
```

## Features

### Feature 1: Data Analysis
- Import your data
- Run analysis
- Export results

### Feature 2: Reporting
- Generate reports
- Schedule exports
- Share with team

## Troubleshooting
Common issues and their solutions:

1. **Connection Issues**
   - Check your internet connection
   - Verify API endpoint
   - Confirm API key

2. **Data Issues**
   - Validate input format
   - Check file permissions
   - Review error logs
""",
            """# Tutorial: Building Your First App

## Prerequisites
Before you begin, make sure you have:
- Python 3.8+
- pip installed
- Basic programming knowledge

## Step 1: Setup
First, let's set up our development environment:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Create Project Structure
```
myapp/
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
└── requirements.txt
```

## Step 3: Write Code
Let's create a simple application:

```python
# src/main.py
def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
```

## Step 4: Testing
Write tests for your code:

```python
# tests/test_main.py
import unittest
from src.main import greet

class TestGreet(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("Alice"), "Hello, Alice!")
```

## Next Steps
- Add more features
- Improve error handling
- Deploy your application
""",
            """# System Architecture

## Overview
Our system follows a microservices architecture with the following components:

### Frontend Service
- React-based SPA
- Material-UI components
- Redux state management

### Backend Services
1. **API Gateway**
   - Request routing
   - Authentication
   - Rate limiting

2. **User Service**
   - User management
   - Authentication
   - Profile handling

3. **Data Service**
   - Data processing
   - Analytics
   - Storage management

## Data Flow
```mermaid
graph LR
    A[Client] --> B[API Gateway]
    B --> C[User Service]
    B --> D[Data Service]
    C --> E[(Database)]
    D --> E
```

## Security
- JWT authentication
- Role-based access control
- Data encryption at rest
- TLS for data in transit

## Scalability
- Horizontal scaling
- Load balancing
- Caching strategy
- Database sharding
""",
            """# Deployment Guide

## Infrastructure Requirements
- Kubernetes cluster
- Load balancer
- Database servers
- Cache servers

## Deployment Steps

### 1. Prepare Environment
```bash
# Set up Kubernetes cluster
kubectl create namespace production
kubectl config set-context --current --namespace=production

# Create secrets
kubectl create secret generic db-credentials \
    --from-literal=username=admin \
    --from-literal=password=secret
```

### 2. Deploy Services
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: api-gateway:latest
        ports:
        - containerPort: 8080
```

### 3. Configure Monitoring
- Prometheus metrics
- Grafana dashboards
- Alert rules

### 4. Backup Strategy
- Daily full backups
- Hourly incremental backups
- Retention policy: 30 days

## Maintenance
- Regular security updates
- Performance monitoring
- Capacity planning
- Disaster recovery testing
"""
        ]
    }
    return pd.DataFrame(data)

def analyze_chunks(result_df):
    """Analyze and print statistics about the chunks."""
    print("\nChunk Analysis:")
    print("="*80)
    
    # Basic statistics
    print(f"Total number of chunks: {len(result_df)}")
    print(f"Number of unique files: {result_df['filename'].nunique()}")
    
    # Chunks per file
    print("\nChunks per file:")
    print("-"*40)
    chunks_per_file = result_df.groupby('filename').size()
    for filename, count in chunks_per_file.items():
        print(f"{filename}: {count} chunks")
    
    # Average chunk size
    result_df['chunk_size'] = result_df['chunk_text'].str.len()
    avg_chunk_size = result_df['chunk_size'].mean()
    print(f"\nAverage chunk size: {avg_chunk_size:.2f} characters")
    
    # Chunk size distribution
    print("\nChunk size distribution:")
    print("-"*40)
    size_bins = [0, 100, 500, 1000, float('inf')]
    size_labels = ['0-100', '101-500', '501-1000', '1000+']
    result_df['size_category'] = pd.cut(result_df['chunk_size'], 
                                      bins=size_bins, 
                                      labels=size_labels)
    size_dist = result_df['size_category'].value_counts().sort_index()
    for category, count in size_dist.items():
        print(f"{category}: {count} chunks")

def main():
    # Create sample DataFrame
    df = create_sample_dataframe()
    
    # Initialize chunker
    chunker = MarkdownChunker(
        min_chunk_size=100,
        max_chunk_size=1000,
        overlap_size=50
    )
    
    # Process DataFrame
    result_df = chunker.process_dataframe(df)
    
    # Print original DataFrame info
    print("\nOriginal DataFrame:")
    print("="*80)
    print(f"Number of files: {len(df)}")
    print("\nFiles:")
    for _, row in df.iterrows():
        print(f"- {row['filename']} ({len(row['filecontent'])} characters)")
    
    # Print processed DataFrame info
    print("\nProcessed DataFrame:")
    print("="*80)
    print(f"Number of chunks: {len(result_df)}")
    
    # Analyze chunks
    analyze_chunks(result_df)
    
    # Save results to JSON for inspection
    output_dir = Path("chunking_results")
    output_dir.mkdir(exist_ok=True)
    
    # Save chunk details
    chunks_data = []
    for _, row in result_df.iterrows():
        chunk_info = {
            'filename': row['filename'],
            'filepath': row['filepath'],
            'chunkid': row['chunkid'],
            'chunk_text': row['chunk_text'],
            'chunk_size': len(row['chunk_text'])
        }
        chunks_data.append(chunk_info)
    
    with open(output_dir / "chunks.json", "w") as f:
        json.dump(chunks_data, f, indent=2)
    
    print(f"\nResults have been saved to {output_dir}/chunks.json")

if __name__ == "__main__":
    main() 
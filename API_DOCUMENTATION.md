# 📚 API Documentation

## Overview

This document provides comprehensive API documentation for the Enhanced Document AI Multi-Agent Assistant. The system provides both REST API endpoints and Python API for programmatic access.

## Base URL
```
http://localhost:7860/api
```

## Authentication
Currently, the API uses API key authentication through environment variables. No additional authentication headers are required for local development.

## Error Handling

All API responses follow this error format:
```json
{
  "error": "Error description",
  "status": "error|blocked|failed",
  "code": 400,
  "details": "Additional error details"
}
```

## Rate Limiting
- Default: 100 requests per hour per user
- Document uploads: 10 per hour per user  
- Questions: 50 per hour per user

Rate limit headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets

---

## 🔗 REST API Endpoints

### Health & Status

#### GET `/api/health`
Get system health status.

**Response:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "uptime_seconds": 3600,
  "requests_total": 150,
  "success_rate": 98.67,
  "avg_response_time": 1.234,
  "recent_errors": [],
  "alerts": [],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET `/api/metrics`
Get detailed system metrics.

**Response:**
```json
{
  "health": { /* health status object */ },
  "circuit_breakers": {
    "summarization": {
      "state": "CLOSED",
      "failure_count": 0,
      "last_failure": null
    }
  },
  "state_info": {
    "sessions_count": 5,
    "cache_size": 10,
    "last_saved": 1640995200
  }
}
```

### Document Processing

#### POST `/api/documents/process`
Process a document with AI agents.

**Request:**
```bash
curl -X POST \
  -F "file=@document.pdf" \
  -F "options={\"include_metadata\": true, \"include_summary\": true}" \
  http://localhost:7860/api/documents/process
```

**Form Data:**
- `file`: Document file (PDF, DOCX, TXT)
- `options`: JSON object with processing options

**Processing Options:**
```json
{
  "include_summary": true,
  "include_metadata": true,
  "include_analysis": false,
  "max_summary_length": 500,
  "extract_keywords": true,
  "language": "en"
}
```

**Response:**
```json
{
  "session_id": "1640995200_abc123"
}
```

#### GET `/api/documents/{session_id}/questions`
Get question history for a document session.

**Response:**
```json
{
  "session_id": "1640995200_abc123",
  "questions": [
    {
      "id": 1,
      "question": "What is the main topic?",
      "answer": "The document discusses...",
      "timestamp": "2024-01-01T12:05:00Z",
      "confidence": 0.88
    }
  ],
  "total_questions": 1
}
```

### Safety & Validation

#### POST `/api/safety/validate-content`
Validate content for safety issues.

**Request:**
```json
{
  "content": "Text content to validate",
  "validation_type": "text|file",
  "strict_mode": false
}
```

**Response:**
```json
{
  "is_safe": true,
  "message": "Content is safe",
  "filters_triggered": [],
  "confidence": 0.95,
  "suggestions": []
}
```

#### POST `/api/safety/validate-file`
Validate uploaded file for safety.

**Request:**
```bash
curl -X POST \
  -F "file=@document.pdf" \
  http://localhost:7860/api/safety/validate-file
```

**Response:**
```json
{
  "is_safe": true,
  "message": "File is safe",
  "file_info": {
    "size": 2048000,
    "type": "application/pdf",
    "extension": ".pdf"
  },
  "security_checks": {
    "size_check": "passed",
    "extension_check": "passed",
    "content_scan": "passed"
  }
}
```

---

## 🐍 Python API

### Core Classes

#### Document Processor
```python
from enhanced_ui import EnhancedDocumentUI
from safety_module import safety_validator

# Initialize processor
processor = EnhancedDocumentUI()

# Process document
result = processor.process_document_enhanced(file_object)

# Validate content
is_safe, message = safety_validator.validate_text_content("text content")
```

#### Safety Validator
```python
from safety_module import SafetyValidator

validator = SafetyValidator()

# File validation
with open('document.pdf', 'rb') as f:
    content = f.read()
    is_safe, message = validator.validate_file_safety('document.pdf', content)

# Text validation
is_safe, message = validator.validate_text_content("Some text content")

# User input validation
is_safe, message = validator.validate_user_input("User question", "question")

# Rate limiting
can_proceed = validator.check_rate_limit("user123", "document_upload")
```

#### Resilience Manager
```python
from resilience_module import ResilienceManager, with_resilience

manager = ResilienceManager()

# Use as decorator
@with_resilience('api_call')
def call_external_api():
    # Your API call here
    pass

# Manual execution
try:
    result = manager.fallback_manager.execute_with_fallback(
        'summarization', 
        primary_function, 
        fallback_args
    )
except Exception as e:
    # Handle complete failure
    pass
```

### Decorators

#### @with_resilience
Adds retry logic and circuit breaker protection.

```python
@with_resilience('api_call')  # operation_type: 'api_call', 'file_processing', 'database'
def my_function():
    # Function with automatic retry and circuit breaker
    pass
```

#### @validate_request
Adds input validation and output sanitization.

```python
@validate_request
def secure_function(data):
    # Function with automatic safety validation
    return processed_data
```

#### @with_fallback
Provides fallback execution strategy.

```python
@with_fallback('my_service')
def primary_function():
    # Primary implementation
    pass

# Register fallback
manager.fallback_manager.register_fallback(
    'my_service',
    primary_function,
    fallback_function
)
```

---

## 🔧 Configuration API

### Environment Configuration
```python
import os
from dotenv import load_dotenv

# Load configuration
load_dotenv()

config = {
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
    'GUARDRAILS_API_KEY': os.getenv('GUARDRAILS_API_KEY'),
    'MAX_FILE_SIZE': int(os.getenv('MAX_FILE_SIZE', 52428800)),
    'RATE_LIMIT_REQUESTS': int(os.getenv('RATE_LIMIT_REQUESTS', 100))
}
```

### Runtime Configuration
```python
from resilience_module import resilience_manager

# Update retry configuration
resilience_manager.retry_manager.retry_configs['api_call'] = {
    'max_retries': 5,
    'base_delay': 2,
    'max_delay': 120
}

# Update circuit breaker settings
cb = resilience_manager.fallback_manager.circuit_breakers['summarization']
cb.failure_threshold = 10
cb.recovery_timeout = 300
```

---

## 📊 Monitoring API

### Health Monitoring
```python
from resilience_module import get_health_status, get_system_metrics

# Get current health
health = get_health_status()
print(f"System status: {health['status']}")
print(f"Success rate: {health['success_rate']}%")

# Get detailed metrics
metrics = get_system_metrics()
```

### Custom Metrics
```python
from resilience_module import resilience_manager

# Record custom metrics
resilience_manager.health_monitor.record_request(
    response_time=1.5,
    success=True
)

# Record custom errors
resilience_manager.health_monitor.record_error(
    Exception("Custom error"),
    {"context": "custom_operation"}
)
```

---

## 🧪 Testing API

### Test Utilities
```python
from test_agents import TestSummarizerAgent
import unittest

# Run specific tests
class MyTestCase(TestSummarizerAgent):
    def test_custom_scenario(self):
        # Your custom test
        pass

# Run tests programmatically
if __name__ == "__main__":
    unittest.main()
```

### Mock Services
```python
from unittest.mock import Mock, patch

# Mock external services for testing
with patch('agents.summarizer_agent.SummarizerAgent') as MockAgent:
    mock_agent = MockAgent.return_value
    mock_agent.generate_summary.return_value = "Test summary"
    
    # Your test code here
    result = mock_agent.generate_summary("test input")
    assert result == "Test summary"
```

---

## 🔒 Security API

### Content Filtering
```python
from safety_module import ContentFilter

filter = ContentFilter()

# Filter document content
is_safe, message, filtered_content = filter.filter_document_content(
    "Raw document content"
)

if is_safe:
    # Proceed with filtered content
    process_content(filtered_content)
else:
    # Handle unsafe content
    handle_security_violation(message)
```

### Security Events
```python
from safety_module import safety_validator

# Log security events
safety_validator.log_security_event("unauthorized_access", {
    "user_id": "user123",
    "attempted_action": "admin_access",
    "timestamp": "2024-01-01T12:00:00Z"
})
```

---

## 📈 Performance Optimization

### Caching
```python
from resilience_module import resilience_manager

# Access state manager for caching
state = resilience_manager.state_manager

# Store in cache
state.set('cache_key', expensive_computation_result)

# Retrieve from cache
cached_result = state.get('cache_key')
if cached_result:
    return cached_result
```

### Batch Processing
```python
def batch_process_documents(file_list):
    """Process multiple documents efficiently"""
    results = []
    
    for file in file_list:
        try:
            # Use resilient processing
            result = processor.process_document_enhanced(file)
            results.append(result)
        except Exception as e:
            # Handle individual failures
            results.append({"error": str(e), "file": file.name})
    
    return results
```

---

## 🚀 Deployment API

### Docker Integration
```python
# health_check.py - For Docker health checks
from resilience_module import get_health_status
import sys

def docker_health_check():
    try:
        health = get_health_status()
        if health['status'] in ['healthy', 'degraded']:
            sys.exit(0)  # Healthy
        else:
            sys.exit(1)  # Unhealthy
    except Exception:
        sys.exit(1)  # Error

if __name__ == "__main__":
    docker_health_check()
```

### Cloud Deployment
```python
# cloud_config.py - Cloud-specific configuration
import os

def get_cloud_config():
    return {
        'is_cloud': os.getenv('CLOUD_PROVIDER') is not None,
        'provider': os.getenv('CLOUD_PROVIDER'),  # 'aws', 'gcp', 'azure'
        'instance_id': os.getenv('INSTANCE_ID'),
        'region': os.getenv('REGION'),
        'log_group': os.getenv('LOG_GROUP'),
        'metrics_endpoint': os.getenv('METRICS_ENDPOINT')
    }
```

---

## 🔍 Debugging API

### Debug Information
```python
from resilience_module import resilience_manager
import json

def get_debug_info():
    """Get comprehensive debug information"""
    return {
        'health_status': resilience_manager.health_monitor.get_health_status(),
        'circuit_breakers': {
            name: {
                'state': cb.state,
                'failures': cb.failure_count
            }
            for name, cb in resilience_manager.fallback_manager.circuit_breakers.items()
        },
        'active_sessions': len(resilience_manager.state_manager.get('sessions', {})),
        'cache_size': len(resilience_manager.state_manager.get('cache', {}))
    }

# Usage
debug_info = get_debug_info()
print(json.dumps(debug_info, indent=2))
```

### Logging Configuration
```python
import logging

# Configure detailed logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Enable debug logging for specific modules
logging.getLogger('safety_module').setLevel(logging.DEBUG)
logging.getLogger('resilience_module').setLevel(logging.DEBUG)
```

---

## ❓ FAQ

### Q: How do I increase rate limits?
A: Modify the environment variable `RATE_LIMIT_REQUESTS` or update the configuration programmatically:
```python
safety_validator.rate_limits_config = {
    "document_upload": 20,
    "question": 100,
    "default": 200
}
```

### Q: How do I add custom safety filters?
A: Extend the SafetyValidator class:
```python
class CustomSafetyValidator(SafetyValidator):
    def __init__(self):
        super().__init__()
        self.custom_patterns = [r'custom_pattern_here']
    
    def validate_text_content(self, text):
        # Add your custom validation logic
        is_safe, message = super().validate_text_content(text)
        
        if is_safe:
            # Additional custom checks
            for pattern in self.custom_patterns:
                if re.search(pattern, text):
                    return False, "Custom filter triggered"
        
        return is_safe, message
```

### Q: How do I customize the retry behavior?
A: Update the retry configuration:
```python
resilience_manager.retry_manager.retry_configs['my_operation'] = {
    'max_retries': 5,
    'base_delay': 2,
    'max_delay': 300
}

@with_resilience('my_operation')
def my_function():
    pass
```

---

## 📞 Support

For additional API support:
- **GitHub Issues**: [Report bugs or request features](https://github.com/your-repo/issues)
- **Documentation**: [Full documentation](https://your-docs-site.com)
- **Email**: api-support@your-domain.com

---

*Last updated: January 2024*",
  "status": "success",
  "summary": {
    "content": "Document summary...",
    "length": 450,
    "confidence": 0.95
  },
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "creation_date": "2024-01-01",
    "pages": 10,
    "file_size": "2.3 MB",
    "keywords": ["keyword1", "keyword2"]
  },
  "processing_time": 2.5,
  "agents_used": ["summarizer", "metadata_extractor"]
}
```

#### GET `/api/documents/{session_id}`
Retrieve processed document information.

**Response:**
```json
{
  "session_id": "1640995200_abc123",
  "filename": "document.pdf",
  "status": "completed",
  "results": { /* processing results */ },
  "created_at": "2024-01-01T12:00:00Z",
  "expires_at": "2024-01-02T12:00:00Z"
}
```

### Question Answering

#### POST `/api/documents/{session_id}/questions`
Ask questions about a processed document.

**Request:**
```json
{
  "question": "What is the main topic of this document?",
  "context_length": 1000,
  "response_format": "detailed"
}
```

**Response:**
```json
{
  "question": "What is the main topic of this document?",
  "answer": "The document primarily discusses...",
  "confidence": 0.88,
  "sources": ["page 1", "page 3"],
  "response_time": 1.2,
  "session_id": "1640995200_abc123
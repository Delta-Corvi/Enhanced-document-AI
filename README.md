# Document AI Multi-Agent Assistant Plus
![Uploading Gemini_Generated_Image_ho6kwiho6kwiho6k.png…]()


[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ReadyTensor](https://img.shields.io/badge/ReadyTensor-AAIDC2025-green.svg)](https://readytensor.ai)

> **Module 3 Project for Ready Tensor Agentic AI Developer Certification 2025 (AAIDC2025)**

A revolutionary document intelligence platform that transforms static PDF documents into interactive, conversational resources through advanced multi-agent AI systems. This sophisticated solution enables users to upload documents, process them with state-of-the-art embeddings, and engage in natural language conversations with their content using collaborative AI agents.

## 🚀 Key Features

**Multi-Agent Intelligence**
- Collaborative AI agents specialized in document parsing, analysis, and synthesis
- Intelligent agent coordination for complex reasoning and cross-document analysis
- Dynamic agent selection based on query complexity and requirements

**Advanced Document Processing**
- Intelligent PDF text extraction and chunking with contextual overlap
- Multi-format support with OCR capabilities for scanned documents
- Semantic understanding and structural recognition

**Conversational Interface**
- Natural language querying with Google Gemini integration
- Context-aware conversations across multiple documents
- Progressive query refinement and iterative analysis

**Privacy-First Architecture**
- Complete local data storage and processing
- No cloud dependency for document content
- Offline accessibility for processed materials

**Enterprise-Ready Performance**
- FAISS-powered vector search for efficient similarity matching
- Persistent storage with JSONL and optimized indices
- Real-time processing feedback and status monitoring

## 🏗️ Architecture Overview

The system employs a sophisticated multi-agent architecture where specialized AI agents collaborate to deliver comprehensive document intelligence:

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                       │
│                   (Gradio Web App)                      │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                Multi-Agent Coordinator                  │
├─────────────────────────────────────────────────────────┤
│  Document Parser  │  Analysis Agent  │  Retrieval Agent │
│     Agent         │                  │                  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                 Processing Layer                        │
├─────────────────────────────────────────────────────────┤
│  PDF Processor  │  Embedding Gen  │  Vector Store      │
│  (PyMuPDF)      │  (Google AI)    │  (FAISS)           │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                 Persistence Layer                       │
├─────────────────────────────────────────────────────────┤
│  Document DB    │  Vector Indices │  Conversation      │
│  (JSONL)        │  (FAISS Index)  │  History           │
└─────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- **Python 3.8 or higher**
- **Google AI API key** (for Gemini integration)
- **Minimum 4GB RAM** (8GB recommended for large documents)
- **Internet connection** (for AI model access during processing)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Delta-Corvi/-Document-AI-Multi-Agent-Assistant-Plus.git
   cd -Document-AI-Multi-Agent-Assistant-Plus
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_ai_api_key_here
   ```

5. **Launch the application**
   ```bash
   python main.py
   ```

6. **Access the interface**
   
   Open your browser and navigate to `http://localhost:7860`

## 💡 Usage Guide

### Getting Started

1. **Upload Documents**: Use the drag-and-drop interface or file browser to upload PDF documents
2. **Processing**: Monitor real-time processing feedback as documents are analyzed and embedded
3. **Query**: Ask natural language questions about your document content
4. **Collaborate**: Engage in extended conversations with follow-up questions and refinements

### Example Queries

**Simple Information Retrieval**
- "What are the main findings in this research paper?"
- "Summarize the executive summary from the business plan"

**Complex Analysis**
- "Compare the methodologies across these three studies and identify common limitations"
- "Analyze the financial trends in these quarterly reports and highlight potential risks"

**Cross-Document Synthesis**
- "What common themes emerge across all uploaded documents?"
- "Identify contradictions between the findings in documents A and B"

### Best Practices

**Document Preparation**
- Ensure PDFs have clear, readable text (avoid heavily stylized fonts)
- Organize documents with descriptive filenames
- For scanned documents, verify OCR quality before upload

**Query Optimization**
- Be specific about the type of information you're seeking
- Use progressive refinement for complex topics
- Leverage the conversational nature for iterative analysis

## 📁 Project Structure

```
Document-AI-Multi-Agent-Assistant-Plus/
├── main.py                    # Application entry point and server management
├── requirements.txt           # Python dependencies and version specifications
├── .env                      # Environment configuration (API keys)
├── README.md                 # Project documentation
├── LICENSE                   # MIT License file
│
├── agents/                   # Multi-agent system components
│   ├── __init__.py          
│   ├── coordinator.py        # Agent coordination and task distribution
│   ├── document_parser.py    # Document analysis specialist agent
│   ├── retrieval_agent.py    # Information retrieval specialist
│   └── synthesis_agent.py    # Response synthesis and validation
│
├── core/                     # Core processing modules
│   ├── __init__.py
│   ├── document_processor.py # PDF processing and text extraction
│   ├── embedding_manager.py  # Embedding generation and management
│   ├── vector_store.py       # FAISS vector database operations
│   └── conversation_manager.py # Multi-agent conversation handling
│
├── ui/                       # User interface components
│   ├── __init__.py
│   ├── gradio_interface.py   # Main web interface implementation
│   └── components.py         # UI component definitions
│
├── utils/                    # Utility functions and helpers
│   ├── __init__.py
│   ├── file_handlers.py      # File I/O operations
│   ├── config_manager.py     # Configuration management
│   └── logging_setup.py      # Logging configuration
│
├── data/                     # Local storage directory
│   ├── documents/            # Uploaded document storage
│   ├── indices/              # FAISS vector indices
│   ├── metadata/             # Document metadata (JSONL)
│   └── conversations/        # Conversation history storage
│
└── tests/                    # Test suite
    ├── __init__.py
    ├── test_agents.py        # Multi-agent system tests
    ├── test_processing.py    # Document processing tests
    └── test_integration.py   # End-to-end integration tests
```

## 🔧 Configuration Options

### Environment Variables

```env
# Required
GOOGLE_API_KEY=your_google_ai_api_key

# Optional
MAX_DOCUMENT_SIZE=50MB          # Maximum document size
CHUNK_SIZE=1000                 # Text chunking size
CHUNK_OVERLAP=200               # Chunk overlap for context preservation
MAX_CONVERSATION_HISTORY=100    # Conversation history limit
VECTOR_DIMENSIONS=768           # Embedding vector dimensions
```

### Advanced Configuration

The system supports advanced configuration through `config/settings.yaml`:

```yaml
agents:
  max_concurrent_agents: 5
  coordination_timeout: 30
  retry_attempts: 3

processing:
  embedding_batch_size: 32
  similarity_threshold: 0.7
  max_retrieved_chunks: 10

ui:
  theme: "default"
  auto_scroll: true
  show_agent_reasoning: false
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_agents.py -v
python -m pytest tests/test_processing.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## 🚀 Performance Optimization

### Memory Management
- The system uses lazy loading for large document collections
- Vector indices are optimized for memory-efficient operations
- Automatic garbage collection prevents memory leaks during extended use

### Scalability Considerations
- FAISS indices support efficient scaling to thousands of documents
- Multi-agent processing can be distributed across available CPU cores
- Configurable batch sizes optimize processing for available resources

### Query Performance
- Semantic caching reduces redundant processing
- Intelligent agent selection minimizes unnecessary computations
- Optimized embedding retrieval ensures sub-second response times

## 📊 Monitoring and Analytics

The system provides comprehensive monitoring capabilities:

- **Agent Performance Metrics**: Track individual agent performance and collaboration patterns
- **Processing Analytics**: Monitor document processing times and success rates  
- **Query Analysis**: Understand user interaction patterns and system utilization
- **Resource Monitoring**: Track memory usage, processing load, and system health

## 🔒 Security and Privacy

**Data Protection**
- All documents remain on local storage - no cloud uploads
- Encryption at rest for sensitive document collections
- Secure API key management with environment variable isolation

**Privacy Compliance**
- GDPR-compliant data handling with complete user control
- No telemetry or usage data transmission
- Configurable data retention policies

## 🤝 Contributing

We welcome contributions to enhance the Document AI Multi-Agent Assistant Plus! Here's how you can contribute:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines for Python code
- Add comprehensive tests for new features
- Update documentation for significant changes
- Ensure backward compatibility when possible

## 🐛 Troubleshooting

### Common Issues

**Installation Problems**
```bash
# Update pip and try again
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**API Key Issues**
- Verify your Google AI API key is correctly set in `.env`
- Ensure the API key has appropriate permissions
- Check for any API quota limitations

**Performance Issues**
- Increase system memory allocation for large document collections
- Adjust chunk size and overlap parameters for optimal processing
- Monitor CPU usage during multi-agent processing

**Document Processing Errors**
- Verify PDF files are not corrupted or password-protected
- Ensure sufficient disk space for processing large documents
- Check file permissions for uploaded documents

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Ready Tensor Certification

This project is part of the **Ready Tensor Agentic AI Developer Certification 2025 (AAIDC2025)** program, specifically designed as a Module 3 implementation demonstrating advanced multi-agent systems and document intelligence capabilities.

### Learning Objectives Achieved
- Multi-agent system design and implementation
- Advanced RAG (Retrieval-Augmented Generation) architecture
- Production-ready AI application development
- Privacy-focused AI system deployment
- Conversational AI interface design


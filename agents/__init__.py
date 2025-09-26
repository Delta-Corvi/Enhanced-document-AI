# ==============================================================================
# agents/__init__.py
# ==============================================================================

"""
AI Agents Package for Document Processing

This package contains specialized AI agents for different document processing tasks:
- SummarizerAgent: Generates intelligent document summaries
- QuestionAgent: Handles question-answering about document content
- MetadataAgent: Extracts structured metadata from documents

Usage:
    from agents import SummarizerAgent, QuestionAgent, MetadataAgent
    
    # Initialize agents
    summarizer = SummarizerAgent()
    qa_agent = QuestionAgent()
    metadata_agent = MetadataAgent()
"""

__version__ = "1.0.0"
__description__ = "AI agents for document processing tasks"

# Import agent functions directly
try:
    from .summarizer_agent import summarize
    from .question_agent import answer
    from .metadata_agent import extract_metadata
    
    AGENTS_LOADED = True
    
except ImportError as e:
    import logging
    logging.warning(f"Some agents could not be imported: {e}")
    AGENTS_LOADED = False
    
    # Provide fallback implementations
    def summarize(text: str) -> str:
        """Fallback summarize function"""
        return f"Summary not available - agent import failed. Text length: {len(text)} characters."
    
    def answer(context: str, question: str) -> str:
        """Fallback answer function"""
        return f"Answer not available - agent import failed. Question: {question}"
    
    def extract_metadata(text: str) -> dict:
        """Fallback metadata extraction function"""
        return {
            "title": "Metadata extraction failed",
            "author": "Unknown",
            "date": "Unknown",
            "keywords": ["extraction", "failed"],
            "error": "Agent import failed"
        }

# Create basic agent classes for backwards compatibility
class BaseAgent:
    def __init__(self):
        self.name = "BaseAgent"
    
    def process(self, *args, **kwargs):
        return {"error": "Agent not available", "fallback": True}

class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "SummarizerAgent"
    
    def summarize(self, text: str) -> str:
        return summarize(text)

class QuestionAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "QuestionAgent"
    
    def answer(self, context: str, question: str) -> str:
        return answer(context, question)

class MetadataAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "MetadataAgent"
    
    def extract_metadata(self, text: str) -> dict:
        return extract_metadata(text)

# Agent registry for dynamic access
AGENT_REGISTRY = {
    "summarizer": SummarizerAgent,
    "question": QuestionAgent,
    "metadata": MetadataAgent
}

def get_agent(agent_type: str):
    """Get an agent instance by type"""
    if agent_type.lower() in AGENT_REGISTRY:
        return AGENT_REGISTRY[agent_type.lower()]()
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

def list_available_agents():
    """List all available agent types"""
    return list(AGENT_REGISTRY.keys())

# Agent factory for creating configured agents
class AgentFactory:
    """Factory for creating and configuring AI agents"""
    
    @staticmethod
    def create_summarizer(**config):
        """Create a configured summarizer agent"""
        agent = SummarizerAgent()
        # Apply configuration if the agent supports it
        if hasattr(agent, 'configure'):
            agent.configure(**config)
        return agent
    
    @staticmethod
    def create_question_agent(**config):
        """Create a configured question-answering agent"""
        agent = QuestionAgent()
        if hasattr(agent, 'configure'):
            agent.configure(**config)
        return agent
    
    @staticmethod
    def create_metadata_agent(**config):
        """Create a configured metadata extraction agent"""
        agent = MetadataAgent()
        if hasattr(agent, 'configure'):
            agent.configure(**config)
        return agent
    
    @staticmethod
    def create_all_agents(**config):
        """Create all agents with shared configuration"""
        return {
            "summarizer": AgentFactory.create_summarizer(**config),
            "question": AgentFactory.create_question_agent(**config),
            "metadata": AgentFactory.create_metadata_agent(**config)
        }

# Public API
__all__ = [
    "SummarizerAgent",
    "QuestionAgent", 
    "MetadataAgent",
    "AgentFactory",
    "get_agent",
    "list_available_agents",
    "summarize",
    "answer",
    "extract_metadata",
    "AGENTS_LOADED"
]
"""
Test Package for Enhanced Document AI Assistant

This package contains comprehensive test suites:
- Unit tests for individual components
- Integration tests for end-to-end workflows  
- Security tests for safety validation
- Performance tests and benchmarks
- Mock objects and test utilities

Usage:
    # Run all tests
    python -m pytest tests/
    
    # Run specific test categories
    python -m pytest tests/ -m unit
    python -m pytest tests/ -m integration
    python -m pytest tests/ -m security
    
    # Import test utilities
    from tests import TestUtilities, MockGeminiClient
"""

__version__ = "1.0.0"
__description__ = "Comprehensive test suite for Enhanced Document AI"

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, MagicMock, patch

# Test configuration
TEST_CONFIG = {
    "test_data_dir": os.path.join(os.path.dirname(__file__), "test_data"),
    "mock_responses_dir": os.path.join(os.path.dirname(__file__), "mock_responses"),
    "temp_dir": os.path.join(os.path.dirname(__file__), "temp"),
    "coverage_threshold": 80,
    "performance_threshold_ms": 5000,
    "memory_threshold_mb": 100
}

# Test categories and markers
TEST_MARKERS = {
    "unit": "Unit tests for individual components",
    "integration": "Integration tests for complete workflows",
    "security": "Security and safety validation tests", 
    "performance": "Performance and load tests",
    "slow": "Tests that take longer to run",
    "api": "Tests that require external API access",
    "mock": "Tests using mocked dependencies"
}

# Test utilities class
class TestUtilities:
    """Common utilities for testing"""
    
    @staticmethod
    def create_test_file(content: str, filename: str = "test.txt") -> str:
        """Create a temporary test file with given content"""
        import tempfile
        
        temp_dir = TEST_CONFIG["temp_dir"]
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    @staticmethod
    def create_test_pdf(content: str = "Test PDF content") -> str:
        """Create a simple test PDF file"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            import tempfile
            
            temp_dir = TEST_CONFIG["temp_dir"]
            os.makedirs(temp_dir, exist_ok=True)
            
            file_path = os.path.join(temp_dir, "test.pdf")
            c = canvas.Canvas(file_path, pagesize=letter)
            c.drawString(100, 750, content)
            c.save()
            
            return file_path
            
        except ImportError:
            # Fallback: create a dummy PDF-like file
            return TestUtilities.create_test_file(
                f"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n{content}",
                "test.pdf"
            )
    
    @staticmethod
    def cleanup_test_files():
        """Clean up temporary test files"""
        import shutil
        
        temp_dir = TEST_CONFIG["temp_dir"]
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)
    
    @staticmethod
    def get_sample_text(size: str = "medium") -> str:
        """Get sample text of different sizes for testing"""
        samples = {
            "small": "This is a small test document with basic content.",
            "medium": """This is a medium-sized test document. It contains multiple sentences 
                        and paragraphs to test document processing capabilities. The content 
                        includes various topics and demonstrates typical document structure.
                        
                        This second paragraph adds more content for comprehensive testing of 
                        summarization and metadata extraction features.""",
            "large": """This is a large test document designed for comprehensive testing.
                      """ + "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100,
            "toxic": "This content contains inappropriate and harmful language for testing safety filters.",
            "pii": "Contact John Doe at john.doe@email.com or call 555-123-4567. SSN: 123-45-6789.",
            "multilingual": "Hello world. Bonjour le monde. Hola mundo. 你好世界. مرحبا بالعالم."
        }
        
        return samples.get(size, samples["medium"])

# Mock classes for testing
class MockGeminiClient:
    """Mock Gemini API client for testing"""
    
    def __init__(self, response_type: str = "success"):
        self.response_type = response_type
        self.call_count = 0
        self.last_prompt = None
    
    def generate_content(self, prompt: str) -> str:
        """Mock content generation"""
        self.call_count += 1
        self.last_prompt = prompt
        
        if self.response_type == "success":
            return f"Mock response for: {prompt[:50]}..."
        elif self.response_type == "error":
            raise Exception("Mock API error")
        elif self.response_type == "timeout":
            import time
            time.sleep(10)  # Simulate timeout
            return "Delayed response"
        else:
            return "Default mock response"

class MockGuardrailsValidator:
    """Mock Guardrails validator for testing"""
    
    def __init__(self, validation_result: bool = True):
        self.validation_result = validation_result
        self.validation_calls = []
    
    def validate_text_content(self, text: str):
        """Mock text validation"""
        self.validation_calls.append(text)
        
        if self.validation_result:
            return True, "Content is safe", {"mock": True}
        else:
            return False, "Content failed validation", {"mock": True, "issues": ["test_issue"]}
    
    def validate_file_safety(self, file_path: str, content: bytes):
        """Mock file validation"""
        return self.validation_result, "Mock file validation", {"mock": True}

class MockResilienceManager:
    """Mock resilience manager for testing"""
    
    def __init__(self):
        self.health_status = {"status": "healthy", "mock": True}
        self.retry_calls = []
    
    def get_health_status(self):
        return self.health_status
    
    def resilient_execute(self, operation_type: str = "api_call"):
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.retry_calls.append((operation_type, func.__name__))
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Test data management
class TestDataManager:
    """Manages test data and mock responses"""
    
    @staticmethod
    def load_test_data(filename: str) -> Any:
        """Load test data from file"""
        test_data_dir = TEST_CONFIG["test_data_dir"]
        file_path = os.path.join(test_data_dir, filename)
        
        if not os.path.exists(file_path):
            return None
        
        if filename.endswith('.json'):
            import json
            with open(file_path, 'r') as f:
                return json.load(f)
        elif filename.endswith('.txt'):
            with open(file_path, 'r') as f:
                return f.read()
        else:
            with open(file_path, 'rb') as f:
                return f.read()
    
    @staticmethod
    def save_test_data(data: Any, filename: str) -> None:
        """Save test data to file"""
        test_data_dir = TEST_CONFIG["test_data_dir"]
        os.makedirs(test_data_dir, exist_ok=True)
        
        file_path = os.path.join(test_data_dir, filename)
        
        if filename.endswith('.json'):
            import json
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif isinstance(data, str):
            with open(file_path, 'w') as f:
                f.write(data)
        else:
            with open(file_path, 'wb') as f:
                f.write(data)

# Test result collection
class TestResults:
    """Collects and manages test results"""
    
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "coverage": 0.0,
            "performance": {},
            "categories": {}
        }
    
    def add_result(self, category: str, test_name: str, status: str, duration: float = 0.0):
        """Add a test result"""
        self.results["total_tests"] += 1
        
        if status == "passed":
            self.results["passed"] += 1
        elif status == "failed":
            self.results["failed"] += 1
        elif status == "skipped":
            self.results["skipped"] += 1
        
        if category not in self.results["categories"]:
            self.results["categories"][category] = {"passed": 0, "failed": 0, "skipped": 0}
        
        self.results["categories"][category][status] += 1
        
        if duration > 0:
            self.results["performance"][test_name] = duration
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test results summary"""
        success_rate = 0
        if self.results["total_tests"] > 0:
            success_rate = (self.results["passed"] / self.results["total_tests"]) * 100
        
        return {
            **self.results,
            "success_rate": success_rate,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }

# Test runner utilities
def run_test_suite(categories: Optional[List[str]] = None) -> TestResults:
    """Run the complete test suite"""
    import subprocess
    
    results = TestResults()
    
    # Build pytest command
    cmd = ["python", "-m", "pytest", "tests/", "-v"]
    
    if categories:
        markers = " or ".join(categories)
        cmd.extend(["-m", markers])
    
    try:
        # Run pytest
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse results (simplified)
        output_lines = result.stdout.split('\n')
        for line in output_lines:
            if "passed" in line or "failed" in line or "skipped" in line:
                # Parse test results from pytest output
                # This is a simplified parser - in practice you'd use pytest plugins
                if "PASSED" in line:
                    results.add_result("general", line.split("::")[-1], "passed")
                elif "FAILED" in line:
                    results.add_result("general", line.split("::")[-1], "failed")
                elif "SKIPPED" in line:
                    results.add_result("general", line.split("::")[-1], "skipped")
        
        return results
        
    except Exception as e:
        logging.error(f"Test suite execution failed: {e}")
        return results

# Test environment setup
def setup_test_environment():
    """Set up the test environment"""
    # Create necessary directories
    for dir_path in TEST_CONFIG.values():
        if isinstance(dir_path, str) and dir_path.endswith(('_dir', 'temp')):
            os.makedirs(dir_path, exist_ok=True)
    
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["LOG_LEVEL"] = "ERROR"  # Reduce log noise during testing
    os.environ["GUARDRAILS_ENABLED"] = "false"  # Use mocks by default
    
    logging.info("Test environment setup completed")

def teardown_test_environment():
    """Clean up test environment"""
    TestUtilities.cleanup_test_files()
    logging.info("Test environment cleanup completed")

# Public API
__all__ = [
    # Test utilities
    "TestUtilities",
    "TestDataManager",
    "TestResults",
    
    # Mock classes
    "MockGeminiClient",
    "MockGuardrailsValidator", 
    "MockResilienceManager",
    
    # Test configuration
    "TEST_CONFIG",
    "TEST_MARKERS",
    
    # Test execution
    "run_test_suite",
    "setup_test_environment",
    "teardown_test_environment"
]

# Auto-setup test environment when package is imported
try:
    setup_test_environment()
except Exception as e:
    logging.warning(f"Test environment auto-setup failed: {e}")

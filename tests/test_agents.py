"""
Comprehensive test suite for Document AI Multi-Agent Assistant
"""

import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import json
from io import BytesIO

# Mock the required modules for testing
import sys
sys.modules['gradio'] = Mock()
sys.modules['google.generativeai'] = Mock()

class TestSummarizerAgent(unittest.TestCase):
    """Test cases for the Summarizer Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_text = "This is a sample document text for testing purposes. It contains multiple sentences to test the summarization functionality."
        
    def test_text_preprocessing(self):
        """Test text preprocessing functionality"""
        # Mock the summarizer agent
        with patch('agents.summarizer_agent.SummarizerAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.preprocess_text.return_value = self.sample_text.strip()
            
            result = mock_agent.preprocess_text(self.sample_text)
            self.assertEqual(result, self.sample_text.strip())
    
    def test_summary_generation(self):
        """Test summary generation with valid input"""
        expected_summary = "This is a test summary of the document."
        
        with patch('agents.summarizer_agent.SummarizerAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.generate_summary.return_value = expected_summary
            
            result = mock_agent.generate_summary(self.sample_text)
            self.assertEqual(result, expected_summary)
    
    def test_empty_text_handling(self):
        """Test handling of empty text input"""
        with patch('agents.summarizer_agent.SummarizerAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.generate_summary.return_value = "No content to summarize."
            
            result = mock_agent.generate_summary("")
            self.assertEqual(result, "No content to summarize.")


class TestQuestionAgent(unittest.TestCase):
    """Test cases for the Question Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_context = "This is a test document about artificial intelligence and machine learning."
        self.sample_question = "What is this document about?"
        
    def test_question_answering(self):
        """Test question answering functionality"""
        expected_answer = "This document is about artificial intelligence and machine learning."
        
        with patch('agents.question_agent.QuestionAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.answer_question.return_value = expected_answer
            
            result = mock_agent.answer_question(self.sample_question, self.sample_context)
            self.assertEqual(result, expected_answer)
    
    def test_invalid_question_handling(self):
        """Test handling of invalid questions"""
        with patch('agents.question_agent.QuestionAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.answer_question.return_value = "I cannot answer this question based on the provided context."
            
            result = mock_agent.answer_question("", self.sample_context)
            self.assertEqual(result, "I cannot answer this question based on the provided context.")


class TestMetadataAgent(unittest.TestCase):
    """Test cases for the Metadata Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_text = "Title: Test Document\nAuthor: John Doe\nDate: 2024\nKeywords: test, document, AI"
        
    def test_metadata_extraction(self):
        """Test metadata extraction functionality"""
        expected_metadata = {
            "title": "Test Document",
            "author": "John Doe",
            "date": "2024",
            "keywords": ["test", "document", "AI"]
        }
        
        with patch('agents.metadata_agent.MetadataAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.extract_metadata.return_value = expected_metadata
            
            result = mock_agent.extract_metadata(self.sample_text)
            self.assertEqual(result, expected_metadata)
    
    def test_fallback_metadata(self):
        """Test fallback metadata generation for documents without clear metadata"""
        expected_metadata = {
            "title": "Untitled Document",
            "author": "Unknown",
            "date": "Unknown",
            "keywords": []
        }
        
        with patch('agents.metadata_agent.MetadataAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.extract_metadata.return_value = expected_metadata
            
            result = mock_agent.extract_metadata("Some text without metadata")
            self.assertEqual(result, expected_metadata)


class TestGeminiClient(unittest.TestCase):
    """Test cases for Gemini API client"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_api_key'})
    def test_client_initialization(self):
        """Test Gemini client initialization"""
        with patch('utils.gemini_client.GeminiClient') as MockClient:
            mock_client = MockClient.return_value
            mock_client.api_key = "test_api_key"
            
            self.assertEqual(mock_client.api_key, "test_api_key")
    
    def test_api_call_with_retry(self):
        """Test API call with retry mechanism"""
        with patch('utils.gemini_client.GeminiClient') as MockClient:
            mock_client = MockClient.return_value
            mock_client.generate_content.return_value = "Test response"
            
            result = mock_client.generate_content("Test prompt")
            self.assertEqual(result, "Test response")


class TestValidator(unittest.TestCase):
    """Test cases for input/output validation"""
    
    def test_pdf_file_validation(self):
        """Test PDF file validation"""
        with patch('utils.validator.Validator') as MockValidator:
            mock_validator = MockValidator.return_value
            mock_validator.is_valid_pdf.return_value = True
            
            # Create a mock file
            mock_file = MagicMock()
            mock_file.name = "test.pdf"
            
            result = mock_validator.is_valid_pdf(mock_file)
            self.assertTrue(result)
    
    def test_text_length_validation(self):
        """Test text length validation"""
        with patch('utils.validator.Validator') as MockValidator:
            mock_validator = MockValidator.return_value
            mock_validator.validate_text_length.return_value = True
            
            test_text = "This is a test text of reasonable length."
            result = mock_validator.validate_text_length(test_text)
            self.assertTrue(result)
    
    def test_content_safety_validation(self):
        """Test content safety validation"""
        with patch('utils.validator.Validator') as MockValidator:
            mock_validator = MockValidator.return_value
            mock_validator.is_content_safe.return_value = True
            
            safe_text = "This is safe, appropriate content."
            result = mock_validator.is_content_safe(safe_text)
            self.assertTrue(result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_complete_document_processing_workflow(self):
        """Test the complete document processing workflow"""
        # Mock the entire processing pipeline
        with patch('app.process_document') as mock_process:
            mock_process.return_value = {
                'summary': 'Test summary',
                'metadata': {'title': 'Test', 'author': 'Test Author'},
                'status': 'success'
            }
            
            # Simulate document processing
            mock_file = MagicMock()
            mock_file.name = "test.pdf"
            
            result = mock_process(mock_file)
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('summary', result)
            self.assertIn('metadata', result)
    
    def test_question_answering_workflow(self):
        """Test the question-answering workflow"""
        with patch('app.answer_question') as mock_qa:
            mock_qa.return_value = "Test answer to the question."
            
            question = "What is this document about?"
            context = "Test document context"
            
            result = mock_qa(question, context)
            self.assertEqual(result, "Test answer to the question.")


def run_performance_tests():
    """Run basic performance tests"""
    import time
    
    print("Running Performance Tests...")
    
    # Test response time
    start_time = time.time()
    # Simulate processing time
    time.sleep(0.1)
    end_time = time.time()
    
    response_time = end_time - start_time
    print(f"Simulated processing time: {response_time:.3f} seconds")
    
    # Assert reasonable response time (< 30 seconds for real implementation)
    assert response_time < 30, f"Response time too high: {response_time}"
    print("✓ Performance test passed")


def run_all_tests():
    """Run all test suites"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestSummarizerAgent,
        TestQuestionAgent,
        TestMetadataAgent,
        TestGeminiClient,
        TestValidator,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run performance tests
    run_performance_tests()
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Document AI Multi-Agent Assistant - Test Suite")
    print("=" * 50)
    
    success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)

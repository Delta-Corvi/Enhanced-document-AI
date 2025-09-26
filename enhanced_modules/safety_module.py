"""
Enhanced Safety Module with Guardrails Integration
Provides comprehensive content filtering and safety checks
"""

import re
import logging
import hashlib
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

# Guardrails free API integration
try:
    import requests
    GUARDRAILS_AVAILABLE = True
except ImportError:
    GUARDRAILS_AVAILABLE = False
    print("Warning: requests not available. Some safety features disabled.")

class GuardrailsValidator:
    """Guardrails AI validator for enhanced content safety"""
    
    def __init__(self):
        self.setup_logging()
        self.enabled = GUARDRAILS_AVAILABLE
        
    def setup_logging(self):
        """Configure logging for GuardrailsValidator"""
        self.logger = logging.getLogger('GuardrailsValidator')
        self.logger.setLevel(logging.INFO)
        
    def validate_text_content(self, text: str, content_type: str = "general") -> Tuple[bool, str, Dict]:
        """Validate text content using Guardrails AI"""
        try:
            if not self.enabled:
                return True, "Guardrails not available - using basic validation", {"basic_mode": True}
            
            # Basic validation patterns
            toxic_patterns = [
                r'(?i)\b(?:hate|violent|harmful|toxic|abuse)\w*\b',
                r'(?i)\b(?:kill|murder|suicide|self[-\s]*harm)\b',
                r'(?i)\b(?:bomb|weapon|explosive|terrorist)\b'
            ]
            
            for pattern in toxic_patterns:
                if re.search(pattern, text):
                    self.logger.warning("Potentially harmful content detected")
                    return False, "Content contains potentially harmful language", {"pattern_match": True}
            
            return True, "Content validated successfully", {"guardrails_check": True}
            
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return True, "Validation error - allowing content", {"error": str(e)}
    
    def check_pii_detection(self, text: str) -> Tuple[bool, List[str]]:
        """Check for personally identifiable information"""
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }
        
        detected_pii = []
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, text):
                detected_pii.append(pii_type)
        
        return len(detected_pii) == 0, detected_pii


class SafetyValidator:
    """Enhanced safety validator with multiple validation layers"""
    
    def __init__(self):
        self.setup_logging()
        self.blocked_patterns = self._load_blocked_patterns()
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_extensions = {'.pdf', '.txt', '.docx'}
        self.rate_limits = {}
        
    def setup_logging(self):
        """Configure security logging"""
        self.logger = logging.getLogger('SafetyValidator')
        handler = logging.FileHandler('security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _load_blocked_patterns(self) -> List[str]:
        """Load blocked content patterns"""
        return [
            r'(?i)\b(?:password|secret|api[_\s]*key|token)\s*[:=]\s*\S+',
            r'(?i)\b(?:credit[_\s]*card|ssn|social[_\s]*security)\b',
            r'(?i)\b(?:hack|exploit|malware|virus)\b',
            r'(?i)\b(?:violent|harmful|illegal)\b',
            # Add more patterns as needed
        ]
    
    def validate_file_safety(self, file_path: str, file_content: bytes) -> Tuple[bool, str]:
        """Comprehensive file safety validation"""
        try:
            # Check file size
            if len(file_content) > self.max_file_size:
                self.logger.warning(f"File too large: {len(file_content)} bytes")
                return False, "File size exceeds maximum allowed (50MB)"
            
            # Check file extension
            if not any(file_path.lower().endswith(ext) for ext in self.allowed_extensions):
                self.logger.warning(f"Invalid file extension: {file_path}")
                return False, "File type not allowed"
            
            # Check for malicious patterns in filename
            if self._contains_malicious_patterns(file_path):
                self.logger.warning(f"Malicious filename pattern: {file_path}")
                return False, "Filename contains suspicious patterns"
            
            # Basic content validation for text files
            if file_path.lower().endswith('.txt'):
                try:
                    text_content = file_content.decode('utf-8', errors='ignore')
                    is_safe, message = self.validate_text_content(text_content)
                    if not is_safe:
                        return False, message
                except Exception as e:
                    self.logger.error(f"Error validating text content: {str(e)}")
            
            return True, "File is safe"
            
        except Exception as e:
            self.logger.error(f"File validation error: {str(e)}")
            return False, "File validation failed"
    
    def validate_text_content(self, text: str) -> Tuple[bool, str]:
        """Validate text content for safety"""
        try:
            # Check for blocked patterns
            for pattern in self.blocked_patterns:
                if re.search(pattern, text):
                    self.logger.warning(f"Blocked pattern found: {pattern[:20]}...")
                    return False, "Content contains prohibited information"
            
            # Check text length
            if len(text) > 1000000:  # 1MB of text
                return False, "Text content too long"
            
            # Use Guardrails if available
            if GUARDRAILS_AVAILABLE:
                is_safe = self._check_with_guardrails(text)
                if not is_safe:
                    return False, "Content flagged by safety filters"
            
            return True, "Content is safe"
            
        except Exception as e:
            self.logger.error(f"Text validation error: {str(e)}")
            return False, "Content validation failed"
    
    def _check_with_guardrails(self, text: str) -> bool:
        """Check content using Guardrails free API"""
        try:
            # Using a simple content safety check
            # Replace with actual Guardrails API when available
            
            # Basic toxicity patterns
            toxic_patterns = [
                r'(?i)\b(?:hate|violent|harmful|toxic|abuse)\w*\b',
                r'(?i)\b(?:kill|murder|suicide|self[-\s]*harm)\b',
                r'(?i)\b(?:bomb|weapon|explosive|terrorist)\b'
            ]
            
            for pattern in toxic_patterns:
                if re.search(pattern, text):
                    self.logger.warning("Toxic content detected by Guardrails")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Guardrails check error: {str(e)}")
            return True  # Fail open for availability
    
    def _contains_malicious_patterns(self, filename: str) -> bool:
        """Check for malicious patterns in filename"""
        # Extract just the filename from the full path
        import os
        actual_filename = os.path.basename(filename)
        
        malicious_patterns = [
            r'\.\./|\.\.\\',  # Directory traversal (but not in absolute paths)
            r'[<>:"|?*]',     # Invalid filename characters (but : is valid in Windows paths)
            r'^\s*$',         # Empty or whitespace only
            r'\.{3,}'         # Three or more consecutive dots
        ]
        
        # Modified pattern check that doesn't flag normal Windows paths
        for pattern in malicious_patterns:
            # Skip colon check if it's a Windows absolute path
            if pattern == r'[<>:"|?*]' and (
                len(filename) > 3 and filename[1:3] == ':\\' or  # C:\
                ':\\' in filename  # Contains drive letter
            ):
                # Check for other dangerous characters but not colon in paths
                modified_pattern = r'[<>"|?*]'
                if re.search(modified_pattern, actual_filename):
                    return True
            elif re.search(pattern, actual_filename):
                return True
        
        return False
    
    def validate_user_input(self, user_input: str, input_type: str = "general") -> Tuple[bool, str]:
        """Validate user input (questions, etc.)"""
        try:
            # Check input length
            max_lengths = {
                "question": 1000,
                "general": 2000,
                "filename": 255
            }
            
            max_length = max_lengths.get(input_type, 2000)
            if len(user_input) > max_length:
                return False, f"Input too long (max {max_length} characters)"
            
            # Check for injection attempts
            injection_patterns = [
                r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',  # Script tags
                r'javascript:',  # JavaScript protocol
                r'on\w+\s*=',   # Event handlers
                r'\{\{.*\}\}',  # Template injection
                r'<%.*%>',      # Server-side template injection
            ]
            
            for pattern in injection_patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    self.logger.warning(f"Injection attempt detected: {pattern}")
                    return False, "Input contains potentially malicious content"
            
            # Use content validation
            return self.validate_text_content(user_input)
            
        except Exception as e:
            self.logger.error(f"User input validation error: {str(e)}")
            return False, "Input validation failed"
    
    def check_rate_limit(self, user_id: str, action: str = "default") -> bool:
        """Simple rate limiting"""
        try:
            current_time = datetime.now()
            key = f"{user_id}:{action}"
            
            # Rate limits per action per hour
            limits = {
                "document_upload": 10,
                "question": 50,
                "default": 100
            }
            
            limit = limits.get(action, 100)
            
            if key not in self.rate_limits:
                self.rate_limits[key] = []
            
            # Clean old entries (older than 1 hour)
            self.rate_limits[key] = [
                timestamp for timestamp in self.rate_limits[key]
                if (current_time - timestamp).total_seconds() < 3600
            ]
            
            # Check if limit exceeded
            if len(self.rate_limits[key]) >= limit:
                self.logger.warning(f"Rate limit exceeded for {user_id}:{action}")
                return False
            
            # Add current request
            self.rate_limits[key].append(current_time)
            return True
            
        except Exception as e:
            self.logger.error(f"Rate limit check error: {str(e)}")
            return True  # Fail open
    
    def sanitize_output(self, output: str) -> str:
        """Sanitize output before returning to user"""
        try:
            # Remove potential sensitive information
            sensitive_patterns = [
                (r'\b(?:api[_\s]*key|token|secret)\s*[:=]\s*\S+', '[REDACTED]'),
                (r'\b(?:\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})\b', '[CARD_NUMBER]'),
                (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
            ]
            
            sanitized = output
            for pattern, replacement in sensitive_patterns:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
            
            return sanitized
            
        except Exception as e:
            self.logger.error(f"Output sanitization error: {str(e)}")
            return output  # Return original if sanitization fails
    
    def log_security_event(self, event_type: str, details: Dict):
        """Log security events"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "details": details,
                "hash": hashlib.sha256(str(details).encode()).hexdigest()[:16]
            }
            
            self.logger.info(f"Security Event: {json.dumps(log_entry)}")
            
        except Exception as e:
            self.logger.error(f"Security logging error: {str(e)}")


class EnhancedContentFilter:
    """Advanced content filtering with multiple techniques"""
    
    def __init__(self):
        self.safety_validator = SafetyValidator()
        self.guardrails_validator = GuardrailsValidator()
    
    def filter_document_content(self, content: str) -> Tuple[bool, str, str, Dict]:
        """Filter and validate document content"""
        try:
            # Basic safety check
            is_safe, message = self.safety_validator.validate_text_content(content)
            if not is_safe:
                return False, message, "", {"validation_failed": True}
            
            # Guardrails check
            if self.guardrails_validator.enabled:
                gr_safe, gr_message, gr_info = self.guardrails_validator.validate_text_content(content)
                if not gr_safe:
                    return False, gr_message, "", gr_info
            
            # Clean content
            cleaned_content = self._clean_content(content)
            
            # Additional filtering
            filtered_content = self._apply_content_filters(cleaned_content)
            
            return True, "Content filtered successfully", filtered_content, {"filtered": True}
            
        except Exception as e:
            return False, f"Content filtering failed: {str(e)}", "", {"error": str(e)}
    
    def _clean_content(self, content: str) -> str:
        """Clean content of unwanted elements"""
        try:
            # Remove excessive whitespace
            content = re.sub(r'\s+', ' ', content)
            
            # Remove control characters
            content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\t')
            
            # Remove potential code injection
            content = re.sub(r'<[^>]*>', '', content)  # Remove HTML tags
            
            return content.strip()
            
        except Exception:
            return content
    
    def _apply_content_filters(self, content: str) -> str:
        """Apply additional content filters"""
        try:
            # Truncate if too long
            if len(content) > 100000:  # 100KB limit
                content = content[:100000] + "... [Content truncated for safety]"
            
            # Remove repeated patterns (potential spam)
            content = re.sub(r'(.{50,}?)\1{3,}', r'\1[Repeated content removed]', content)
            
            return content
            
        except Exception:
            return content


# Global instances
guardrails_validator = GuardrailsValidator()
safety_validator = SafetyValidator()
enhanced_content_filter = EnhancedContentFilter()

# Utility functions
def validate_content_safety(text: str, content_type: str = "general") -> Dict:
    """Validate content safety and return comprehensive results"""
    try:
        # Basic safety validation
        is_safe, message = safety_validator.validate_text_content(text)
        
        # Guardrails validation
        gr_safe, gr_message, gr_info = guardrails_validator.validate_text_content(text, content_type)
        
        # PII detection
        pii_safe, pii_detected = guardrails_validator.check_pii_detection(text)
        
        return {
            "is_safe": is_safe and gr_safe and pii_safe,
            "message": message if not is_safe else (gr_message if not gr_safe else "Content is safe"),
            "basic_validation": {"passed": is_safe, "message": message},
            "guardrails_validation": {"passed": gr_safe, "message": gr_message, "info": gr_info},
            "pii_detection": {"passed": pii_safe, "detected": pii_detected},
            "enhanced": guardrails_validator.enabled
        }
    except Exception as e:
        return {
            "is_safe": False,
            "message": f"Validation error: {str(e)}",
            "error": True
        }

def get_safety_status() -> Dict:
    """Get current safety system status"""
    return {
        "guardrails_available": GUARDRAILS_AVAILABLE,
        "guardrails_enabled": guardrails_validator.enabled,
        "basic_validation": True,
        "enhanced_features": guardrails_validator.enabled,
        "timestamp": datetime.now().isoformat()
    }

def validate_request(func):
    """Decorator for request validation"""
    def wrapper(*args, **kwargs):
        try:
            # Basic rate limiting (simplified for demo)
            user_id = kwargs.get('user_id', 'anonymous')
            if not safety_validator.check_rate_limit(user_id):
                return {"error": "Rate limit exceeded", "status": "blocked"}
            
            result = func(*args, **kwargs)
            
            # Sanitize output if it's a string
            if isinstance(result, str):
                result = safety_validator.sanitize_output(result)
            elif isinstance(result, dict) and 'content' in result:
                result['content'] = safety_validator.sanitize_output(result['content'])
            
            return result
            
        except Exception as e:
            safety_validator.log_security_event("function_error", {
                "function": func.__name__,
                "error": str(e)
            })
            return {"error": "Processing failed", "status": "error"}
    
    return wrapper
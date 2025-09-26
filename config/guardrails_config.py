"""
Guardrails AI Configuration for Enhanced Document AI Assistant
Centralized configuration for all Guardrails AI validators and guards
"""

import os
from typing import Dict, List, Any

# Guardrails AI configuration
GUARDRAILS_CONFIG = {
    # Global settings
    "enabled": True,
    "fallback_to_basic": True,  # Use basic patterns if Guardrails fails
    "log_validation_results": True,
    "cache_validation_results": False,  # Set to True for performance in production
    
    # Content validation thresholds
    "toxicity_threshold": 0.8,  # Lower = more strict (0.0-1.0)
    "profanity_threshold": 0.0,  # Zero tolerance for profanity
    "pii_sensitivity": "medium",  # low, medium, high
    
    # Text length limits
    "max_document_length": 100000,  # 100KB
    "max_question_length": 1000,
    "max_response_length": 5000,
    "min_content_length": 1,
    
    # Rate limiting (requests per hour)
    "rate_limits": {
        "document_upload": 10,
        "question": 50,
        "validation": 200,
        "default": 100
    },
    
    # PII detection settings
    "pii_entities": [
        "PHONE_NUMBER",
        "EMAIL_ADDRESS", 
        "CREDIT_CARD",
        "SSN",
        "PERSON",  # Names
        "LOCATION",  # Addresses
        "DATE_TIME",
        "URL"
    ],
    
    # Topic restrictions
    "allowed_topics": [
        "research",
        "academic", 
        "business",
        "technical",
        "educational",
        "scientific",
        "literature",
        "legal",
        "medical",
        "financial"
    ],
    
    "forbidden_topics": [
        "violence",
        "hate", 
        "adult",
        "illegal",
        "weapons",
        "drugs",
        "gambling",
        "terrorism"
    ],
    
    # SQL injection patterns (in addition to Guardrails)
    "sql_injection_patterns": [
        r"(?i)(union\s+select)",
        r"(?i)(drop\s+table)",
        r"(?i)(delete\s+from)",
        r"(?i)(insert\s+into)",
        r"(?i)(update\s+.*\s+set)",
        r"(?i)(\bor\b\s+\d+\s*=\s*\d+)",
        r"(?i)(exec\s*\()",
        r"(?i)(script\s*>)"
    ],
    
    # Custom validation rules
    "custom_patterns": {
        "api_keys": r'\b[A-Za-z0-9]{32,}\b',
        "passwords": r'(?i)password\s*[:=]\s*\S+',
        "tokens": r'(?i)token\s*[:=]\s*\S+',
        "secrets": r'(?i)secret\s*[:=]\s*\S+',
        "private_keys": r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----'
    }
}

# Validator-specific configurations
VALIDATOR_CONFIGS = {
    "ToxicLanguage": {
        "threshold": GUARDRAILS_CONFIG["toxicity_threshold"],
        "validation_method": "sentence",
        "on_fail": "filter"  # filter, fix, exception, reask
    },
    
    "ProfanityFree": {
        "threshold": GUARDRAILS_CONFIG["profanity_threshold"],
        "on_fail": "filter"
    },
    
    "DetectPII": {
        "pii_entities": GUARDRAILS_CONFIG["pii_entities"],
        "on_fail": "filter"
    },
    
    "ValidLength": {
        "min": GUARDRAILS_CONFIG["min_content_length"],
        "max": GUARDRAILS_CONFIG["max_document_length"],
        "on_fail": "fix"
    },
    
    "RestrictToTopic": {
        "valid_topics": GUARDRAILS_CONFIG["allowed_topics"],
        "invalid_topics": GUARDRAILS_CONFIG["forbidden_topics"],
        "on_fail": "exception"
    },
    
    "BugFreeSQL": {
        "on_fail": "exception"
    }
}

# Environment-specific overrides
def get_environment_config() -> Dict[str, Any]:
    """Get environment-specific configuration overrides"""
    config = GUARDRAILS_CONFIG.copy()
    
    # Override from environment variables
    if os.getenv("GUARDRAILS_STRICT_MODE", "false").lower() == "true":
        config["toxicity_threshold"] = 0.5  # More strict
        config["pii_sensitivity"] = "high"
    
    if os.getenv("GUARDRAILS_PERMISSIVE_MODE", "false").lower() == "true":
        config["toxicity_threshold"] = 0.9  # Less strict
        config["pii_sensitivity"] = "low"
    
    # Production vs Development
    if os.getenv("ENVIRONMENT", "development") == "production":
        config["cache_validation_results"] = True
        config["log_validation_results"] = True
        # Stricter rate limits for production
        config["rate_limits"] = {
            "document_upload": 5,
            "question": 30,
            "validation": 100,
            "default": 50
        }
    
    return config

# Guard templates for different content types
GUARD_TEMPLATES = {
    "document_content": {
        "validators": [
            ("ValidLength", {"min": 10, "max": 100000}),
            ("ToxicLanguage", {"threshold": 0.8}),
            ("ProfanityFree", {}),
            ("DetectPII", {"pii_entities": ["PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD"]})
        ],
        "description": "For validating uploaded document content"
    },
    
    "user_question": {
        "validators": [
            ("ValidLength", {"min": 1, "max": 1000}),
            ("ToxicLanguage", {"threshold": 0.9}),
            ("ProfanityFree", {}),
            ("BugFreeSQL", {})
        ],
        "description": "For validating user questions and inputs"
    },
    
    "ai_response": {
        "validators": [
            ("ValidLength", {"min": 1, "max": 5000}),
            ("DetectPII", {"pii_entities": ["PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD", "SSN"]})
        ],
        "description": "For validating AI-generated responses before output"
    },
    
    "metadata": {
        "validators": [
            ("ValidLength", {"min": 1, "max": 1000}),
            ("DetectPII", {"pii_entities": ["EMAIL_ADDRESS", "PHONE_NUMBER"]})
        ],
        "description": "For validating extracted metadata"
    }
}

# Error messages and user-friendly responses
ERROR_MESSAGES = {
    "toxic_content": "The content contains language that may be inappropriate or harmful. Please review and modify your input.",
    "profanity_detected": "The content contains profanity. Please use appropriate language.",
    "pii_detected": "The content may contain personally identifiable information. Please remove sensitive data before proceeding.",
    "content_too_long": "The content exceeds the maximum allowed length. Please shorten your input.",
    "content_too_short": "The content is too short to process meaningfully. Please provide more information.",
    "sql_injection": "The input appears to contain potentially malicious code. Please review your input.",
    "rate_limit_exceeded": "You have exceeded the rate limit for this action. Please wait before trying again.",
    "topic_violation": "The content discusses topics that are not appropriate for this system.",
    "validation_failed": "The content failed safety validation. Please review and modify your input.",
    "system_error": "A system error occurred during validation. Please try again later."
}

# Logging configuration for Guardrails
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - [Guardrails] %(message)s",
    "file": "logs/guardrails.log",
    "max_size": "10MB",
    "backup_count": 5,
    "include_validation_details": True,
    "log_passed_validations": False,  # Only log failures by default
    "log_performance_metrics": True
}

# Performance and caching settings
PERFORMANCE_CONFIG = {
    "enable_caching": False,  # Enable in production
    "cache_ttl": 3600,  # 1 hour
    "max_cache_size": 1000,
    "batch_validation": True,
    "parallel_validation": False,  # Enable with caution
    "validation_timeout": 30  # seconds
}

def get_guard_config(guard_type: str) -> Dict[str, Any]:
    """Get configuration for a specific guard type"""
    if guard_type not in GUARD_TEMPLATES:
        raise ValueError(f"Unknown guard type: {guard_type}")
    
    template = GUARD_TEMPLATES[guard_type].copy()
    env_config = get_environment_config()
    
    # Apply environment-specific overrides to validators
    for i, (validator_name, validator_config) in enumerate(template["validators"]):
        if validator_name in VALIDATOR_CONFIGS:
            # Merge with global validator config
            merged_config = VALIDATOR_CONFIGS[validator_name].copy()
            merged_config.update(validator_config)
            template["validators"][i] = (validator_name, merged_config)
    
    return template

def validate_config() -> bool:
    """Validate the Guardrails configuration"""
    try:
        # Check required settings
        required_keys = ["enabled", "toxicity_threshold", "max_document_length"]
        for key in required_keys:
            if key not in GUARDRAILS_CONFIG:
                print(f"Missing required config key: {key}")
                return False
        
        # Validate thresholds
        if not 0.0 <= GUARDRAILS_CONFIG["toxicity_threshold"] <= 1.0:
            print("toxicity_threshold must be between 0.0 and 1.0")
            return False
        
        # Validate rate limits
        for action, limit in GUARDRAILS_CONFIG["rate_limits"].items():
            if not isinstance(limit, int) or limit <= 0:
                print(f"Invalid rate limit for {action}: {limit}")
                return False
        
        return True
        
    except Exception as e:
        print(f"Config validation error: {e}")
        return False

# Export main configuration
def get_config() -> Dict[str, Any]:
    """Get the complete Guardrails configuration"""
    if not validate_config():
        raise ValueError("Invalid Guardrails configuration")
    
    return {
        "guardrails": get_environment_config(),
        "validators": VALIDATOR_CONFIGS,
        "guards": GUARD_TEMPLATES,
        "errors": ERROR_MESSAGES,
        "logging": LOGGING_CONFIG,
        "performance": PERFORMANCE_CONFIG
    }

# Example usage and testing
if __name__ == "__main__":
    print("🔧 Guardrails AI Configuration")
    print("=" * 40)
    
    config = get_config()
    
    print("✅ Configuration loaded successfully")
    print(f"📊 Guardrails enabled: {config['guardrails']['enabled']}")
    print(f"🛡️  Toxicity threshold: {config['guardrails']['toxicity_threshold']}")
    print(f"📝 Max document length: {config['guardrails']['max_document_length']:,}")
    print(f"🚦 Rate limits: {config['guardrails']['rate_limits']}")
    
    print(f"\n🔍 Available guard types:")
    for guard_type, template in config['guards'].items():
        print(f"   • {guard_type}: {template['description']}")
        print(f"     Validators: {', '.join([v[0] for v in template['validators']])}")
    
    print(f"\n📋 Validation successful: {validate_config()}")

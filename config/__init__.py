"""
Configuration Package for Enhanced Document AI Assistant

This package contains all configuration files and settings management:
- Guardrails AI configuration and validator settings
- Application settings and environment management
- Logging configuration
- Feature flags and environment-specific overrides

Usage:
    from config import guardrails_config, settings
    from config.guardrails_config import get_config, GUARDRAILS_CONFIG
"""

__version__ = "1.0.0"
__description__ = "Configuration management for Enhanced Document AI"

# Import configuration modules
try:
    from .guardrails_config import (
        GUARDRAILS_CONFIG,
        VALIDATOR_CONFIGS,
        GUARD_TEMPLATES,
        ERROR_MESSAGES,
        get_config,
        get_guard_config,
        get_environment_config,
        validate_config,
        check_compatibility
    )
    
    CONFIG_LOADED = True
    
except ImportError as e:
    import logging
    logging.warning(f"Configuration modules not fully loaded: {e}")
    CONFIG_LOADED = False
    
    # Provide default configuration fallbacks
    GUARDRAILS_CONFIG = {
        "enabled": False,
        "fallback_to_basic": True,
        "toxicity_threshold": 0.8
    }
    
    def get_config():
        return {"basic_config": True, "enhanced_features": False}

# Settings management
import os
from typing import Dict, Any, Optional

class Settings:
    """Centralized settings management"""
    
    def __init__(self):
        self._settings = {}
        self._load_environment_variables()
    
    def _load_environment_variables(self):
        """Load settings from environment variables"""
        # API Keys
        self._settings["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
        self._settings["GUARDRAILS_API_KEY"] = os.getenv("GUARDRAILS_API_KEY")
        
        # Application settings
        self._settings["SERVER_HOST"] = os.getenv("SERVER_HOST", "0.0.0.0")
        self._settings["SERVER_PORT"] = int(os.getenv("SERVER_PORT", 7860))
        self._settings["ENVIRONMENT"] = os.getenv("ENVIRONMENT", "development")
        self._settings["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "INFO")
        
        # Guardrails settings
        self._settings["GUARDRAILS_ENABLED"] = os.getenv("GUARDRAILS_ENABLED", "true").lower() == "true"
        self._settings["TOXICITY_THRESHOLD"] = float(os.getenv("TOXICITY_THRESHOLD", "0.8"))
        
        # Security settings
        self._settings["MAX_FILE_SIZE"] = int(os.getenv("MAX_FILE_SIZE", "52428800"))
        self._settings["RATE_LIMIT_REQUESTS"] = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        
        # Feature flags
        self._settings["ENABLE_PII_DETECTION"] = os.getenv("ENABLE_PII_DETECTION", "true").lower() == "true"
        self._settings["ENABLE_CACHING"] = os.getenv("ENABLE_CACHING", "false").lower() == "true"
        self._settings["DEBUG_MODE"] = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value"""
        self._settings[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self._settings.copy()
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.get("ENVIRONMENT", "").lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.get("ENVIRONMENT", "").lower() == "development"
    
    def validate_required_settings(self) -> Dict[str, Any]:
        """Validate that all required settings are present"""
        required_settings = ["GEMINI_API_KEY"]
        missing = []
        
        for setting in required_settings:
            if not self.get(setting):
                missing.append(setting)
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "optional_missing": [
                key for key in ["GUARDRAILS_API_KEY"] 
                if not self.get(key)
            ]
        }

# Global settings instance
settings = Settings()

# Configuration validation
def validate_all_config() -> Dict[str, Any]:
    """Validate all configuration components"""
    results = {
        "settings": settings.validate_required_settings(),
        "config_loaded": CONFIG_LOADED,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }
    
    if CONFIG_LOADED:
        results["guardrails_config"] = validate_config()
    
    return results

# Environment detection utilities
def get_environment_info() -> Dict[str, Any]:
    """Get comprehensive environment information"""
    import platform
    import sys
    
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "environment": settings.get("ENVIRONMENT"),
        "debug_mode": settings.get("DEBUG_MODE"),
        "config_loaded": CONFIG_LOADED,
        "settings_valid": validate_all_config()["settings"]["valid"]
    }

# Feature flag management
class FeatureFlags:
    """Centralized feature flag management"""
    
    @staticmethod
    def is_enabled(feature: str) -> bool:
        """Check if a feature is enabled"""
        feature_map = {
            "guardrails": settings.get("GUARDRAILS_ENABLED", False),
            "pii_detection": settings.get("ENABLE_PII_DETECTION", True),
            "caching": settings.get("ENABLE_CACHING", False),
            "batch_processing": settings.get("ENABLE_BATCH_PROCESSING", False),
            "advanced_analytics": settings.get("ENABLE_ADVANCED_ANALYTICS", False),
            "export_features": settings.get("ENABLE_EXPORT_FEATURES", True),
            "question_history": settings.get("ENABLE_QUESTION_HISTORY", True),
            "health_monitoring": settings.get("HEALTH_CHECK_ENABLED", True),
            "performance_monitoring": settings.get("PERFORMANCE_MONITORING", True),
        }
        
        return feature_map.get(feature.lower(), False)
    
    @staticmethod
    def get_all_flags() -> Dict[str, bool]:
        """Get all feature flags and their status"""
        return {
            "guardrails": FeatureFlags.is_enabled("guardrails"),
            "pii_detection": FeatureFlags.is_enabled("pii_detection"),
            "caching": FeatureFlags.is_enabled("caching"),
            "batch_processing": FeatureFlags.is_enabled("batch_processing"),
            "advanced_analytics": FeatureFlags.is_enabled("advanced_analytics"),
            "export_features": FeatureFlags.is_enabled("export_features"),
            "question_history": FeatureFlags.is_enabled("question_history"),
            "health_monitoring": FeatureFlags.is_enabled("health_monitoring"),
            "performance_monitoring": FeatureFlags.is_enabled("performance_monitoring"),
        }

# Global feature flags instance
feature_flags = FeatureFlags()

# Public API
__all__ = [
    # Configuration objects
    "GUARDRAILS_CONFIG",
    "VALIDATOR_CONFIGS", 
    "GUARD_TEMPLATES",
    "ERROR_MESSAGES",
    
    # Configuration functions
    "get_config",
    "get_guard_config",
    "get_environment_config",
    "validate_config",
    "validate_all_config",
    
    # Settings management
    "Settings",
    "settings",
    
    # Feature flags
    "FeatureFlags",
    "feature_flags",
    
    # Utilities
    "get_environment_info",
    "check_compatibility",
    
    # Status flags
    "CONFIG_LOADED"
]

# Initialization logging
def _log_initialization():
    """Log configuration initialization status"""
    import logging
    
    validation_result = validate_all_config()
    env_info = get_environment_info()
    
    logging.info(f"Configuration package initialized:")
    logging.info(f"  Environment: {env_info['environment']}")
    logging.info(f"  Config loaded: {CONFIG_LOADED}")
    logging.info(f"  Settings valid: {validation_result['settings']['valid']}")
    
    if not validation_result['settings']['valid']:
        logging.warning(f"Missing required settings: {validation_result['settings']['missing']}")
    
    if validation_result['settings']['optional_missing']:
        logging.info(f"Missing optional settings: {validation_result['settings']['optional_missing']}")

# Auto-initialize logging
try:
    _log_initialization()
except Exception as e:
    print(f"Configuration initialization logging failed: {e}")

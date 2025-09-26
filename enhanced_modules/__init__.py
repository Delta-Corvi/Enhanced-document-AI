"""
Enhanced Modules Package for Document AI Multi-Agent Assistant

This package provides enterprise-grade enhancements including:
- Advanced safety validation with Guardrails AI
- Operational resilience with circuit breakers and retry logic
- Health monitoring and performance metrics
- State management and persistence

Usage:
    from enhanced_modules import safety_module, resilience_module
    from enhanced_modules.safety_module import guardrails_validator
    from enhanced_modules.resilience_module import with_resilience
"""

# Package metadata
__version__ = "1.1.0"
__author__ = "Enhanced Document AI Team"
__description__ = "Enterprise-grade enhancements for Document AI Assistant"

# Import main classes and functions for easy access
try:
    from .safety_module import (
        GuardrailsValidator,
        SafetyValidator,
        EnhancedContentFilter,
        guardrails_validator,
        safety_validator,
        enhanced_content_filter,
        validate_request,
        validate_content_safety,
        get_safety_status,
        GUARDRAILS_AVAILABLE
    )

    from .resilience_module import (
        ResilienceManager,
        CircuitBreaker,
        RetryManager,
        HealthMonitor,
        FallbackManager,
        StateManager,
        ErrorRecovery,
        GracefulShutdown,
        resilience_manager,
        error_recovery,
        graceful_shutdown,
        with_resilience,
        with_fallback,
        with_recovery,
        get_health_status,
        get_system_metrics
    )

    # Flag to indicate successful import
    MODULES_LOADED = True

except ImportError as e:
    # Graceful degradation if modules can't be imported
    import logging
    logging.warning(f"Enhanced modules not fully available: {e}")
    MODULES_LOADED = False

    # Provide dummy implementations to prevent import errors
    class DummyGuardrailsValidator:
        def __init__(self):
            self.logger = logging.getLogger('DummyGuardrailsValidator')
            self.enabled = False

        def validate_text_content(self, text, content_type="general"):
            return True, "Enhanced validation not available", {"basic_mode": True}

        def check_pii_detection(self, text):
            return True, []

    class DummySafetyValidator:
        def __init__(self):
            self.logger = logging.getLogger('DummySafetyValidator')

        def validate_text_content(self, text):
            return True, "Enhanced validation not available"

        def validate_file_safety(self, file_path, content):
            return True, "Enhanced validation not available"

        def validate_user_input(self, user_input, input_type="general"):
            return True, "Enhanced validation not available"

        def sanitize_output(self, output):
            return output

        def check_rate_limit(self, user_id, action="default"):
            return True

        def log_security_event(self, event_type, details):
            pass

    class DummyContentFilter:
        def __init__(self):
            self.safety_validator = DummySafetyValidator()
            self.guardrails_validator = DummyGuardrailsValidator()

        def filter_document_content(self, content):
            return True, "Basic filtering applied", content, {"basic_mode": True}

    class DummyManager:
        def __init__(self):
            self.logger = logging.getLogger('DummyManager')

        def get_health_status(self):
            return {
                "status": "basic",
                "enhanced_features": False,
                "message": "Running in basic mode - enhanced features not available"
            }

        def get_system_metrics(self):
            return {
                "basic_mode": True,
                "enhanced_metrics": False,
                "message": "Enhanced metrics not available"
            }

    class DummyCircuitBreaker:
        def call(self, func, *args, **kwargs):
            return func(*args, **kwargs)

    # Create dummy instances
    GUARDRAILS_AVAILABLE = False
    guardrails_validator = DummyGuardrailsValidator()
    safety_validator = DummySafetyValidator()
    enhanced_content_filter = DummyContentFilter()
    resilience_manager = DummyManager()
    error_recovery = DummyManager()
    graceful_shutdown = DummyManager()

    # Dummy classes
    GuardrailsValidator = DummyGuardrailsValidator
    SafetyValidator = DummySafetyValidator
    EnhancedContentFilter = DummyContentFilter
    ResilienceManager = DummyManager
    CircuitBreaker = DummyCircuitBreaker
    RetryManager = DummyManager
    HealthMonitor = DummyManager
    FallbackManager = DummyManager
    StateManager = DummyManager
    ErrorRecovery = DummyManager
    GracefulShutdown = DummyManager

    def validate_content_safety(text, content_type="general"):
        return {
            "is_safe": True,
            "message": "Basic validation only - enhanced safety not available",
            "enhanced": False,
            "basic_mode": True
        }

    def get_safety_status():
        return {
            "enhanced_safety": False,
            "basic_mode": True,
            "message": "Enhanced safety features not available"
        }

    def get_health_status():
        return {
            "status": "basic",
            "enhanced_features": False,
            "message": "Enhanced health monitoring not available"
        }

    def get_system_metrics():
        return {
            "basic_mode": True,
            "enhanced_metrics": False
        }

    def with_resilience(operation_type="default"):
        def decorator(func):
            return func  # No-op decorator in basic mode
        return decorator

    def with_fallback(service_name):
        def decorator(func):
            return func  # No-op decorator in basic mode
        return decorator

    def with_recovery(func):
        return func  # No-op decorator in basic mode

    def validate_request(func):
        return func  # No-op decorator in basic mode

# Public API - what gets imported with "from enhanced_modules import *"
__all__ = [
    # Classes
    'GuardrailsValidator',
    'SafetyValidator',
    'EnhancedContentFilter',
    'ResilienceManager',
    'CircuitBreaker',
    'RetryManager',
    'HealthMonitor',
    'FallbackManager',
    'StateManager',
    'ErrorRecovery',
    'GracefulShutdown',

    # Global instances
    'guardrails_validator',
    'safety_validator',
    'enhanced_content_filter',
    'resilience_manager',
    'error_recovery',
    'graceful_shutdown',

    # Decorators
    'validate_request',
    'with_resilience',
    'with_fallback',
    'with_recovery',

    # Utility functions
    'validate_content_safety',
    'get_safety_status',
    'get_health_status',
    'get_system_metrics',

    # Status flags
    'MODULES_LOADED',
    'GUARDRAILS_AVAILABLE'
]

# Package initialization
def initialize_enhanced_modules():
    """Initialize enhanced modules with proper configuration"""
    initialization_log = []

    try:
        if MODULES_LOADED:
            # Check Guardrails availability
            guardrails_available = GUARDRAILS_AVAILABLE

            # Initialize resilience manager if available
            if hasattr(resilience_manager, 'health_monitor'):
                health_status = resilience_manager.health_monitor.get_health_status()
            else:
                health_status = {"status": "basic"}

            status = {
                "enhanced_modules": True,
                "guardrails_available": guardrails_available,
                "resilience_active": True,
                "health_status": health_status.get("status", "unknown"),
                "version": __version__,
                "initialization_time": __import__("datetime").datetime.now().isoformat()
            }

            initialization_log.append("✅ Enhanced modules initialized successfully")
            initialization_log.append(f"   Guardrails AI: {'Available' if guardrails_available else 'Not Available'}")
            initialization_log.append("   Resilience: Active")
            initialization_log.append(f"   Health Status: {health_status.get('status', 'unknown')}")

            import logging
            for log_msg in initialization_log:
                logging.info(log_msg)

            return status

        else:
            status = {
                "enhanced_modules": False,
                "basic_mode": True,
                "reason": "modules_not_loaded",
                "message": "Running in basic compatibility mode"
            }

            import logging
            logging.warning("Enhanced modules running in basic mode - some features unavailable")

            return status

    except Exception as e:
        import logging
        logging.error(f"Enhanced modules initialization failed: {e}")
        return {
            "enhanced_modules": False,
            "error": str(e),
            "basic_mode": True
        }

# Auto-initialize when package is imported
_initialization_status = initialize_enhanced_modules()

# Convenience functions
def is_enhanced():
    """Check if enhanced features are available and properly initialized"""
    return MODULES_LOADED and _initialization_status.get("enhanced_modules", False)

def is_basic_mode():
    """Check if running in basic compatibility mode"""
    return not MODULES_LOADED or _initialization_status.get("basic_mode", False)

def get_package_info():
    """Get comprehensive package information"""
    return {
        "name": "enhanced_modules",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "modules_loaded": MODULES_LOADED,
        "initialization_status": _initialization_status,
        "enhanced_features": is_enhanced(),
        "basic_mode": is_basic_mode(),
        "available_features": __all__ if MODULES_LOADED else ["basic_functionality"],
        "feature_count": len(__all__)
    }

def get_feature_status():
    """Get detailed feature availability status"""
    if not MODULES_LOADED:
        return {
            "safety_validation": "basic",
            "guardrails_ai": "unavailable",
            "resilience": "basic",
            "health_monitoring": "basic",
            "circuit_breakers": "unavailable",
            "state_management": "basic",
            "error_recovery": "basic"
        }

    try:
        return {
            "safety_validation": "enhanced" if GUARDRAILS_AVAILABLE else "basic",
            "guardrails_ai": "available" if GUARDRAILS_AVAILABLE else "unavailable",
            "resilience": "enhanced",
            "health_monitoring": "enhanced",
            "circuit_breakers": "available",
            "state_management": "enhanced",
            "error_recovery": "enhanced"
        }
    except ImportError:
        return {
            "safety_validation": "basic",
            "guardrails_ai": "unavailable",
            "resilience": "basic",
            "health_monitoring": "basic",
            "circuit_breakers": "unavailable",
            "state_management": "basic",
            "error_recovery": "basic"
        }

# Version check function
def check_compatibility():
    """Check compatibility with required dependencies"""
    compatibility = {
        "python_version": True,  # Assume compatible if we got this far
        "dependencies": {},
        "optional_dependencies": {},
        "recommendations": []
    }

    import sys
    python_version = sys.version_info

    # Check Python version
    if python_version < (3, 8):
        compatibility["python_version"] = False
        compatibility["recommendations"].append("Upgrade to Python 3.8+")

    # Check required dependencies
    required_deps = {
        "gradio": "gradio",
        "requests": "requests",
        "google-generativeai": "google.generativeai"
    }

    for dep_name, import_name in required_deps.items():
        try:
            __import__(import_name)
            compatibility["dependencies"][dep_name] = True
        except ImportError:
            compatibility["dependencies"][dep_name] = False
            compatibility["recommendations"].append(f"Install {dep_name}")

    # Check optional dependencies
    optional_deps = {
        "guardrails-ai": "guardrails",
        "pytest": "pytest",
        "psutil": "psutil"
    }

    for dep_name, import_name in optional_deps.items():
        try:
            __import__(import_name)
            compatibility["optional_dependencies"][dep_name] = True
        except ImportError:
            compatibility["optional_dependencies"][dep_name] = False

    # Add recommendations based on missing optional deps
    if not compatibility["optional_dependencies"].get("guardrails-ai", False):
        compatibility["recommendations"].append("Install guardrails-ai for enhanced security")

    if not compatibility["optional_dependencies"].get("pytest", False):
        compatibility["recommendations"].append("Install pytest for testing capabilities")

    return compatibility

# Health check function
def perform_health_check():
    """Perform comprehensive health check of enhanced modules"""
    health_report = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "package_info": get_package_info(),
        "feature_status": get_feature_status(),
        "compatibility": check_compatibility(),
        "system_health": None,
        "overall_status": "unknown"
    }

    try:
        # Get system health if available
        if MODULES_LOADED:
            health_report["system_health"] = get_health_status()
        else:
            health_report["system_health"] = {
                "status": "basic",
                "message": "Enhanced health monitoring not available"
            }

        # Determine overall status
        if is_enhanced():
            health_report["overall_status"] = "enhanced"
        elif MODULES_LOADED:
            health_report["overall_status"] = "partial"
        else:
            health_report["overall_status"] = "basic"

    except Exception as e:
        health_report["system_health"] = {"error": str(e)}
        health_report["overall_status"] = "error"

    return health_report

# Module cleanup function
def cleanup_enhanced_modules():
    """Clean up enhanced modules resources"""
    try:
        if MODULES_LOADED and hasattr(resilience_manager, 'state_manager'):
            # Save final state
            resilience_manager.state_manager.save_state()

            # Cleanup old sessions
            resilience_manager.state_manager.cleanup_old_sessions()

        return {"cleanup": "success"}

    except Exception as e:
        import logging
        logging.error(f"Enhanced modules cleanup failed: {e}")
        return {"cleanup": "failed", "error": str(e)}

# Add cleanup to __all__ for external access
__all__.extend([
    'is_enhanced',
    'is_basic_mode',
    'get_package_info',
    'get_feature_status',
    'check_compatibility',
    'perform_health_check',
    'cleanup_enhanced_modules',
    'initialize_enhanced_modules'
])

# Register cleanup function for graceful shutdown
import atexit
atexit.register(cleanup_enhanced_modules)

# Final initialization log
def _log_final_status():
    """Log final initialization status"""
    try:
        import logging

        status = "ENHANCED" if is_enhanced() else "BASIC"
        logging.info(f"Enhanced Modules Package: {status} mode active")
        logging.info(f"Version: {__version__}")
        logging.info(f"Features available: {len(__all__)}")

        if is_basic_mode():
            logging.info("Some enhanced features may not be available - check dependencies")

    except Exception:
        pass  # Don't fail if logging fails

# Execute final logging
_log_final_status()
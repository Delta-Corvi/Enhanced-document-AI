"""
Operational Resilience Module
Provides retry mechanisms, fallback strategies, monitoring, and error recovery
Fixed version with proper health status handling for idle systems
"""

import time
import logging
import json
import threading
from functools import wraps
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime, timedelta
import os
import pickle
from collections import defaultdict, deque
import traceback

class CircuitBreaker:
    """Circuit breaker pattern for external API calls"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'


class RetryManager:
    """Advanced retry mechanism with exponential backoff"""
    
    def __init__(self):
        self.retry_configs = {
            'api_call': {'max_retries': 3, 'base_delay': 1, 'max_delay': 60},
            'file_processing': {'max_retries': 2, 'base_delay': 0.5, 'max_delay': 10},
            'database': {'max_retries': 5, 'base_delay': 0.1, 'max_delay': 5}
        }
    
    def retry_with_backoff(self, operation_type: str = 'api_call'):
        """Decorator for retry with exponential backoff"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                config = self.retry_configs.get(operation_type, self.retry_configs['api_call'])
                
                last_exception = None
                for attempt in range(config['max_retries'] + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        
                        if attempt == config['max_retries']:
                            break
                        
                        # Calculate delay with exponential backoff and jitter
                        delay = min(
                            config['base_delay'] * (2 ** attempt) + (time.time() % 1),
                            config['max_delay']
                        )
                        
                        logging.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay:.2f}s"
                        )
                        time.sleep(delay)
                
                raise last_exception
            return wrapper
        return decorator


class HealthMonitor:
    """System health monitoring and alerts with proper idle state handling"""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_failed': 0,
            'response_times': deque(maxlen=1000),
            'memory_usage': deque(maxlen=100),
            'cpu_usage': deque(maxlen=100),
            'api_calls': defaultdict(int),
            'errors': deque(maxlen=500)
        }
        self.alerts = []
        self.start_time = time.time()
        self.lock = threading.Lock()
        self.min_requests_for_health_check = 5  # Minimum requests before health evaluation
        self.logger = logging.getLogger('HealthMonitor')
    
    def record_request(self, response_time: float, success: bool = True):
        """Record request metrics"""
        with self.lock:
            self.metrics['requests_total'] += 1
            self.metrics['response_times'].append(response_time)
            
            if not success:
                self.metrics['requests_failed'] += 1
                
            # Check for performance alerts
            self._check_performance_alerts()
    
    def record_error(self, error: Exception, context: Dict[str, Any]):
        """Record error for monitoring"""
        with self.lock:
            error_info = {
                'timestamp': datetime.now().isoformat(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context,
                'traceback': traceback.format_exc()
            }
            self.metrics['errors'].append(error_info)
            
            # Check for error rate alerts
            self._check_error_alerts()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status with proper idle handling"""
        with self.lock:
            uptime = time.time() - self.start_time
            
            # Handle idle system (no requests processed)
            if self.metrics['requests_total'] == 0:
                return {
                    'status': 'idle',
                    'uptime_seconds': uptime,
                    'requests_total': 0,
                    'success_rate': None,  # No data available
                    'avg_response_time': None,
                    'recent_errors': [],
                    'alerts': self.alerts[-10:],
                    'timestamp': datetime.now().isoformat(),
                    'message': 'System is idle - no requests processed yet'
                }
            
            # Calculate rates only when we have requests
            success_rate = (
                (self.metrics['requests_total'] - self.metrics['requests_failed']) /
                self.metrics['requests_total']
            ) * 100
            
            # Average response time
            avg_response_time = (
                sum(self.metrics['response_times']) / len(self.metrics['response_times'])
                if self.metrics['response_times'] else 0
            )
            
            # Determine status with proper logic
            if self.metrics['requests_total'] < self.min_requests_for_health_check:
                status = 'starting'  # System is starting up
                message = f'System starting up - {self.metrics["requests_total"]} requests processed'
            elif success_rate > 95:
                status = 'healthy'
                message = 'System operating normally'
            elif success_rate > 80:
                status = 'degraded'
                message = f'System degraded - {success_rate:.1f}% success rate'
            else:
                status = 'unhealthy'
                message = f'System unhealthy - {success_rate:.1f}% success rate'
            
            # Check for additional warning conditions
            if avg_response_time > 5.0 and status == 'healthy':
                status = 'degraded'
                message = f'System degraded - high response time ({avg_response_time:.2f}s)'
            
            return {
                'status': status,
                'uptime_seconds': uptime,
                'requests_total': self.metrics['requests_total'],
                'success_rate': round(success_rate, 2),
                'avg_response_time': round(avg_response_time, 3),
                'recent_errors': list(self.metrics['errors'])[-5:],
                'alerts': self.alerts[-10:],
                'timestamp': datetime.now().isoformat(),
                'message': message
            }
    
    def _check_performance_alerts(self):
        """Check for performance-related alerts"""
        if len(self.metrics['response_times']) >= 10:
            recent_avg = sum(list(self.metrics['response_times'])[-10:]) / 10
            if recent_avg > 5.0:  # 5 second threshold
                alert = {
                    'type': 'performance',
                    'message': f'High response time detected: {recent_avg:.2f}s',
                    'timestamp': datetime.now().isoformat()
                }
                # Avoid duplicate alerts
                if not self.alerts or self.alerts[-1].get('message') != alert['message']:
                    self.alerts.append(alert)
    
    def _check_error_alerts(self):
        """Check for error rate alerts"""
        recent_errors = len([e for e in self.metrics['errors'] 
                           if datetime.fromisoformat(e['timestamp']) > 
                           datetime.now() - timedelta(minutes=5)])
        
        if recent_errors > 10:
            alert = {
                'type': 'error_rate',
                'message': f'High error rate: {recent_errors} errors in 5 minutes',
                'timestamp': datetime.now().isoformat()
            }
            # Avoid duplicate alerts
            if not self.alerts or self.alerts[-1].get('message') != alert['message']:
                self.alerts.append(alert)
    
    def reset_metrics(self):
        """Reset metrics (useful for testing or manual reset)"""
        with self.lock:
            self.metrics = {
                'requests_total': 0,
                'requests_failed': 0,
                'response_times': deque(maxlen=1000),
                'memory_usage': deque(maxlen=100),
                'cpu_usage': deque(maxlen=100),
                'api_calls': defaultdict(int),
                'errors': deque(maxlen=500)
            }
            self.alerts = []
            self.start_time = time.time()
    
    def force_health_check(self):
        """Force a health check by recording a dummy successful request"""
        self.record_request(0.1, True)
        self.logger.info("Forced health check - recorded dummy request")
    
    def set_minimum_requests_threshold(self, threshold: int):
        """Set minimum requests needed before health evaluation"""
        with self.lock:
            self.min_requests_for_health_check = max(1, threshold)
            self.logger.info(f"Set minimum requests threshold to {threshold}")


class FallbackManager:
    """Manages fallback strategies when primary services fail"""
    
    def __init__(self):
        self.fallback_strategies = {}
        self.circuit_breakers = {}
        self.logger = logging.getLogger('FallbackManager')
    
    def register_fallback(self, service_name: str, primary_func: Callable, 
                         fallback_func: Callable, circuit_breaker: CircuitBreaker = None):
        """Register a fallback strategy for a service"""
        if circuit_breaker is None:
            circuit_breaker = CircuitBreaker()
        
        self.fallback_strategies[service_name] = {
            'primary': primary_func,
            'fallback': fallback_func,
            'circuit_breaker': circuit_breaker
        }
        self.circuit_breakers[service_name] = circuit_breaker
        self.logger.info(f"Registered fallback for service: {service_name}")
    
    def execute_with_fallback(self, service_name: str, *args, **kwargs):
        """Execute service with fallback protection"""
        if service_name not in self.fallback_strategies:
            raise ValueError(f"No fallback strategy registered for {service_name}")
        
        strategy = self.fallback_strategies[service_name]
        
        try:
            # Try primary service with circuit breaker
            result = strategy['circuit_breaker'].call(strategy['primary'], *args, **kwargs)
            self.logger.debug(f"Primary service {service_name} succeeded")
            return result
        except Exception as primary_error:
            self.logger.warning(f"Primary service {service_name} failed: {str(primary_error)}")
            
            try:
                # Try fallback service
                result = strategy['fallback'](*args, **kwargs)
                self.logger.info(f"Fallback successful for {service_name}")
                return result
            except Exception as fallback_error:
                self.logger.error(f"Both primary and fallback failed for {service_name}")
                raise Exception(f"Service {service_name} completely unavailable. "
                              f"Primary: {str(primary_error)}, Fallback: {str(fallback_error)}")


class StateManager:
    """Manages application state with persistence and recovery"""
    
    def __init__(self, state_file: str = "app_state.pkl"):
        self.state_file = state_file
        self.lock = threading.Lock()
        self.logger = logging.getLogger('StateManager')
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'rb') as f:
                    loaded_state = pickle.load(f)
                    self.logger.info(f"Loaded state from {self.state_file}")
                    return loaded_state
        except Exception as e:
            self.logger.error(f"Failed to load state: {str(e)}")
        
        # Return default state
        default_state = {
            'sessions': {},
            'cache': {},
            'metrics': {},
            'last_saved': time.time()
        }
        self.logger.info("Created new default state")
        return default_state
    
    def save_state(self):
        """Save state to file"""
        try:
            with self.lock:
                self.state['last_saved'] = time.time()
                
                # Create backup first
                backup_file = f"{self.state_file}.bak"
                if os.path.exists(self.state_file):
                    import shutil
                    shutil.copy2(self.state_file, backup_file)
                
                # Save current state
                with open(self.state_file, 'wb') as f:
                    pickle.dump(self.state, f)
                
                self.logger.debug(f"State saved to {self.state_file}")
                    
        except Exception as e:
            self.logger.error(f"Failed to save state: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from state"""
        with self.lock:
            return self.state.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set value in state"""
        with self.lock:
            self.state[key] = value
            
            # Auto-save periodically
            if time.time() - self.state.get('last_saved', 0) > 300:  # 5 minutes
                threading.Thread(target=self.save_state, daemon=True).start()
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old sessions"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        with self.lock:
            sessions = self.state.get('sessions', {})
            old_sessions = [
                session_id for session_id, session_data in sessions.items()
                if session_data.get('created_at', 0) < cutoff_time
            ]
            
            for session_id in old_sessions:
                del sessions[session_id]
            
            if old_sessions:
                self.logger.info(f"Cleaned up {len(old_sessions)} old sessions")


class ResilienceManager:
    """Main resilience coordinator with improved health monitoring"""
    
    def __init__(self):
        self.retry_manager = RetryManager()
        self.health_monitor = HealthMonitor()
        self.fallback_manager = FallbackManager()
        self.state_manager = StateManager()
        self.logger = logging.getLogger('ResilienceManager')
        self.setup_logging()
        self.setup_fallbacks()
        
        # Start background tasks
        self._start_health_check_thread()
        self._start_state_cleanup_thread()
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )
        
        # Separate error log
        error_handler = logging.FileHandler('errors.log')
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(exc_info)s'
        )
        error_handler.setFormatter(error_formatter)
        logging.getLogger().addHandler(error_handler)
    
    def setup_fallbacks(self):
        """Setup fallback strategies for critical services"""
        def fallback_summarize(text: str) -> str:
            """Simple fallback summarization"""
            sentences = text.split('.')[:3]  # First 3 sentences
            return '. '.join(sentences) + "... [Summarized using fallback method]"
        
        # Register fallback without primary function (to be set by actual implementation)
        self.fallback_manager.fallback_strategies['summarization'] = {
            'primary': None,  # To be set by actual implementation
            'fallback': fallback_summarize,
            'circuit_breaker': CircuitBreaker()
        }
    
    def _start_health_check_thread(self):
        """Start background health monitoring with improved logging"""
        def health_check_loop():
            while True:
                try:
                    # Perform health checks
                    health_status = self.health_monitor.get_health_status()
                    
                    # Intelligent logging based on status
                    if health_status['status'] == 'unhealthy':
                        self.logger.critical(f"System unhealthy: {health_status}")
                    elif health_status['status'] == 'degraded':
                        self.logger.warning(f"System degraded: {health_status}")
                    elif health_status['status'] in ['idle', 'starting']:
                        # Log at debug level for idle/starting systems to avoid spam
                        self.logger.debug(f"System {health_status['status']}: {health_status.get('message', '')}")
                    else:
                        # Healthy systems - log at info level occasionally
                        if health_status['requests_total'] > 0 and health_status['requests_total'] % 100 == 0:
                            self.logger.info(f"System healthy: {health_status['requests_total']} requests processed")
                    
                    # Save health metrics to state
                    self.state_manager.set('health_status', health_status)
                    
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    self.logger.error(f"Health check error: {str(e)}")
                    time.sleep(60)
        
        health_thread = threading.Thread(target=health_check_loop, daemon=True)
        health_thread.start()
        self.logger.info("Health monitoring thread started")
    
    def _start_state_cleanup_thread(self):
        """Start background state cleanup"""
        def cleanup_loop():
            while True:
                try:
                    # Cleanup old sessions
                    self.state_manager.cleanup_old_sessions()
                    
                    # Save state
                    self.state_manager.save_state()
                    
                    time.sleep(3600)  # Every hour
                    
                except Exception as e:
                    self.logger.error(f"Cleanup error: {str(e)}")
                    time.sleep(3600)
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        self.logger.info("State cleanup thread started")
    
    def monitor_request(self, func):
        """Decorator to monitor requests"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                self.health_monitor.record_error(e, {
                    'function': func.__name__,
                    'args': str(args)[:100],  # Truncate for privacy
                    'kwargs': str(kwargs)[:100]
                })
                raise
            finally:
                response_time = time.time() - start_time
                self.health_monitor.record_request(response_time, success)
        
        return wrapper
    
    def resilient_execute(self, operation_type: str = 'api_call'):
        """Decorator combining retry and monitoring"""
        def decorator(func):
            monitored_func = self.monitor_request(func)
            retried_func = self.retry_manager.retry_with_backoff(operation_type)(monitored_func)
            return retried_func
        return decorator


class GracefulShutdown:
    """Handles graceful application shutdown"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.shutdown_handlers = []
        self.is_shutting_down = False
        self.logger = logging.getLogger('GracefulShutdown')
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        import signal
        
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.initiate_shutdown()
        
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except ValueError:
            # Signal handling not available in all environments
            self.logger.warning("Signal handling not available in this environment")
    
    def register_shutdown_handler(self, handler: Callable):
        """Register a function to be called during shutdown"""
        self.shutdown_handlers.append(handler)
        self.logger.debug(f"Registered shutdown handler: {handler.__name__}")
    
    def initiate_shutdown(self):
        """Initiate graceful shutdown process"""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        self.logger.info("Starting graceful shutdown...")
        
        # Execute shutdown handlers
        for handler in self.shutdown_handlers:
            try:
                handler()
                self.logger.info(f"Executed shutdown handler: {handler.__name__}")
            except Exception as e:
                self.logger.error(f"Error in shutdown handler {handler.__name__}: {str(e)}")
        
        # Save final state
        try:
            self.state_manager.save_state()
            self.logger.info("Final state saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving final state: {str(e)}")
        
        self.logger.info("Graceful shutdown completed")


class ErrorRecovery:
    """Automatic error recovery mechanisms"""
    
    def __init__(self, resilience_manager: ResilienceManager):
        self.resilience_manager = resilience_manager
        self.recovery_strategies = {}
        self.logger = logging.getLogger('ErrorRecovery')
        self.setup_default_strategies()
    
    def setup_default_strategies(self):
        """Setup default recovery strategies"""
        self.recovery_strategies.update({
            'memory_error': self._handle_memory_error,
            'api_timeout': self._handle_api_timeout,
            'file_not_found': self._handle_file_error,
            'connection_error': self._handle_connection_error,
            'validation_error': self._handle_validation_error
        })
    
    def recover_from_error(self, error: Exception, context: Dict[str, Any]) -> Any:
        """Attempt to recover from an error"""
        error_type = type(error).__name__.lower()
        
        # Find appropriate recovery strategy
        strategy = None
        for strategy_name, strategy_func in self.recovery_strategies.items():
            if strategy_name in error_type or error_type in strategy_name:
                strategy = strategy_func
                break
        
        if strategy:
            try:
                self.logger.info(f"Attempting recovery for {error_type} using {strategy.__name__}")
                return strategy(error, context)
            except Exception as recovery_error:
                self.logger.error(f"Recovery failed: {str(recovery_error)}")
                raise error  # Re-raise original error
        else:
            self.logger.warning(f"No recovery strategy for {error_type}")
            raise error
    
    def _handle_memory_error(self, error: Exception, context: Dict[str, Any]):
        """Handle memory-related errors"""
        import gc
        gc.collect()  # Force garbage collection
        
        # Clear caches if available
        cache = self.resilience_manager.state_manager.get('cache', {})
        if cache:
            cache.clear()
            self.resilience_manager.state_manager.set('cache', {})
            self.logger.info("Cleared application cache to free memory")
        
        return {"status": "recovery_attempted", "message": "Memory cleaned up"}
    
    def _handle_api_timeout(self, error: Exception, context: Dict[str, Any]):
        """Handle API timeout errors"""
        time.sleep(2)
        return {"status": "recovery_attempted", "message": "Applied timeout backoff"}
    
    def _handle_file_error(self, error: Exception, context: Dict[str, Any]):
        """Handle file-related errors"""
        file_path = context.get('file_path', '')
        if file_path:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        return {"status": "recovery_attempted", "message": "Created missing directories"}
    
    def _handle_connection_error(self, error: Exception, context: Dict[str, Any]):
        """Handle connection errors"""
        time.sleep(1)
        return {"status": "recovery_attempted", "message": "Applied connection retry backoff"}
    
    def _handle_validation_error(self, error: Exception, context: Dict[str, Any]):
        """Handle validation errors"""
        return {"status": "validation_failed", "message": str(error)}


# Global resilience manager instance
resilience_manager = ResilienceManager()
error_recovery = ErrorRecovery(resilience_manager)
graceful_shutdown = GracefulShutdown(resilience_manager.state_manager)

def with_resilience(operation_type: str = 'api_call'):
    """Main decorator that applies all resilience features"""
    return resilience_manager.resilient_execute(operation_type)

def with_fallback(service_name: str):
    """Decorator to execute with fallback protection"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return resilience_manager.fallback_manager.execute_with_fallback(
                service_name, *args, **kwargs
            )
        return wrapper
    return decorator

def with_recovery(func):
    """Decorator to add automatic error recovery"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = {
                'function': func.__name__,
                'args': str(args)[:100],
                'kwargs': str(kwargs)[:100]
            }
            return error_recovery.recover_from_error(e, context)
    return wrapper

# Health check endpoint function
def get_health_status():
    """Get current system health status"""
    return resilience_manager.health_monitor.get_health_status()

# System metrics function
def get_system_metrics():
    """Get detailed system metrics"""
    health_status = resilience_manager.health_monitor.get_health_status()
    
    return {
        'health': health_status,
        'circuit_breakers': {
            name: {
                'state': cb.state,
                'failure_count': cb.failure_count,
                'last_failure': cb.last_failure_time
            }
            for name, cb in resilience_manager.fallback_manager.circuit_breakers.items()
        },
        'state_info': {
            'sessions_count': len(resilience_manager.state_manager.get('sessions', {})),
            'cache_size': len(resilience_manager.state_manager.get('cache', {})),
            'last_saved': resilience_manager.state_manager.get('last_saved', 0)
        },
        'uptime': time.time() - resilience_manager.health_monitor.start_time
    }

# Utility functions for manual testing
def simulate_request_activity(num_requests: int = 10, success_rate: float = 0.9):
    """Simulate request activity for testing health monitoring"""
    import random
    
    for i in range(num_requests):
        response_time = random.uniform(0.1, 2.0)
        success = random.random() < success_rate
        resilience_manager.health_monitor.record_request(response_time, success)
    
    logging.info(f"Simulated {num_requests} requests with {success_rate*100}% success rate")

def reset_health_metrics():
    """Reset health metrics (useful for testing)"""
    resilience_manager.health_monitor.reset_metrics()
    logging.info("Health metrics reset")
#!/usr/bin/env python3
"""
Docker Health Check Script for Enhanced Document AI Assistant
Performs comprehensive health checks for containerized deployment
"""

import sys
import time
import subprocess
import socket
import os
from pathlib import Path

def check_port(port=7860, host='localhost'):
    """Check if the application port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Port check failed: {e}")
        return False

def check_process():
    """Check if the main application process is running"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'enhanced_ui.py'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0 and result.stdout.strip()
    except Exception as e:
        print(f"Process check failed: {e}")
        return False

def check_file_system():
    """Check if required directories and files are accessible"""
    try:
        required_paths = [
            '/app/logs',
            '/app/data',
            '/app/state',
            '/app/enhanced_ui.py'
        ]
        
        for path in required_paths:
            if not Path(path).exists():
                print(f"Required path not found: {path}")
                return False
        
        # Check write permissions
        test_file = Path('/app/state/health_check.tmp')
        try:
            test_file.write_text(str(time.time()))
            test_file.unlink()
        except Exception as e:
            print(f"Write permission check failed: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"File system check failed: {e}")
        return False

def check_memory_usage():
    """Check memory usage is within acceptable limits"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        # Alert if memory usage is above 90%
        if memory.percent > 90:
            print(f"High memory usage: {memory.percent}%")
            return False
        
        return True
    except ImportError:
        # psutil not available, skip check
        return True
    except Exception as e:
        print(f"Memory check failed: {e}")
        return False

def check_disk_space():
    """Check available disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage('/app')
        
        # Alert if less than 100MB free
        if free < 100 * 1024 * 1024:
            print(f"Low disk space: {free / (1024*1024):.1f}MB free")
            return False
        
        return True
    except Exception as e:
        print(f"Disk space check failed: {e}")
        return False

def check_environment_variables():
    """Check required environment variables"""
    try:
        required_vars = ['GEMINI_API_KEY']
        optional_vars = ['GUARDRAILS_API_KEY', 'LOG_LEVEL']
        
        for var in required_vars:
            if not os.getenv(var):
                print(f"Required environment variable not set: {var}")
                return False
        
        return True
    except Exception as e:
        print(f"Environment check failed: {e}")
        return False

def check_application_health():
    """Check application-specific health via internal health check"""
    try:
        # Try to import and run health check
        sys.path.insert(0, '/app')
        from resilience_module import get_health_status
        
        health = get_health_status()
        if health['status'] not in ['healthy', 'degraded']:
            print(f"Application unhealthy: {health['status']}")
            return False
        
        return True
    except ImportError:
        # Resilience module not available, skip internal check
        return True
    except Exception as e:
        print(f"Application health check failed: {e}")
        return False

def main():
    """Main health check function"""
    print("Starting Docker health check...")
    
    checks = [
        ("Port accessibility", check_port),
        ("Process running", check_process),
        ("File system", check_file_system),
        ("Memory usage", check_memory_usage),
        ("Disk space", check_disk_space),
        ("Environment variables", check_environment_variables),
        ("Application health", check_application_health),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            start_time = time.time()
            passed = check_func()
            duration = time.time() - start_time
            
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{check_name}: {status} ({duration:.2f}s)")
            
            if not passed:
                all_passed = False
                
        except Exception as e:
            print(f"{check_name}: ✗ ERROR - {e}")
            all_passed = False
    
    # Overall status
    if all_passed:
        print("🟢 Health check PASSED - Container is healthy")
        sys.exit(0)
    else:
        print("🔴 Health check FAILED - Container is unhealthy")
        sys.exit(1)

if __name__ == "__main__":
    main()

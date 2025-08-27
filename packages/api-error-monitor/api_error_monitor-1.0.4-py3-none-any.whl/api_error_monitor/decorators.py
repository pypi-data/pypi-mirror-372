from functools import wraps
from typing import Callable, Any, Optional, Dict
import requests

from .core import ApiErrorMonitor

def monitor_errors(
    integration_name: str,
    endpoint: Optional[str] = None,
    context_provider: Optional[Callable[..., Dict[str, Any]]] = None
):
    """
    Decorator for monitoring errors in functions
    
    Example:
        @monitor_errors('salesforce_integration', endpoint='get_report')
        def get_salesforce_report(report_id):
            # Function implementation
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create error monitor
            monitor = ApiErrorMonitor(integration_name)
            
            # Extract context if provided
            context = context_provider(*args, **kwargs) if context_provider else {}
            
            # Determine endpoint value
            endpoint_value = endpoint or func.__name__
            
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                # Use HTTP-specific error capture
                monitor.capture_http_error(
                    exception=e,
                    endpoint=endpoint_value,
                    context=context
                )
                raise
            except Exception as e:
                # Capture the error
                monitor.capture_error(
                    message=f"Error in {func.__name__}: {str(e)}",
                    endpoint=endpoint_value,
                    exception=e,
                    context=context
                )
                raise
                
        return wrapper
    return decorator
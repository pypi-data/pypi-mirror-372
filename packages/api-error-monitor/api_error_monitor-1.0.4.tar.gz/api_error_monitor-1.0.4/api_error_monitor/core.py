

import datetime
import json
import os
import sys
import traceback
import uuid
from typing import Dict, Any, Optional, List, Callable, Union

import requests

class ApiErrorMonitor:
    """
    Core error monitoring class for API integrations
    """
    def __init__(
        self, 
        integration_name: str,
        version: str = "1.0.0",
        context: Optional[Dict[str, Any]] = None
    ):
        self.integration_name = integration_name
        self.version = version
        self.context = context or {}
        self.execution_id = str(uuid.uuid4())
        self.errors: List[Dict[str, Any]] = []
        
        # Create output directory if it doesn't exist
        os.makedirs("errors", exist_ok=True)
        
    def capture_error(
        self,
        message: str,
        error_type: str = "GENERAL_ERROR",
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Union[Dict[str, Any], str]] = None,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Capture error details and write to appropriate outputs
        """
        
        # Create error record with standard fields
        error_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        error_data = {
            "error_id": error_id,
            "timestamp": timestamp,
            "integration": self.integration_name,
            "integration_version": self.version,
            "execution_id": self.execution_id,
            "error_type": error_type,
            "message": message,
        }
        
        # Add optional fields
        if endpoint:
            error_data["endpoint"] = endpoint
        if status_code:
            error_data["status_code"] = status_code
        if request_data:
            error_data["request_data"] = self._sanitize_data(request_data)
        if response_data:
            error_data["response_data"] = self._sanitize_data(response_data)
        if context:
            error_data["context"] = context
        if exception:
            error_data["exception_type"] = type(exception).__name__
            
        # Add stack trace
        if exception:
            error_data["stack_trace"] = "".join(traceback.format_exception(
                type(exception), exception, exception.__traceback__
            ))
        else:
            error_data["stack_trace"] = traceback.format_stack()
            
        # Add global context
        if self.context:
            error_data["global_context"] = self.context
        
        # Add to errors list
        self.errors.append(error_data)
        
        # Write to structured file
        self._write_to_json_file(error_data)
        
        # Also write to error summary file
        self._write_to_summary_file(error_data)
        
        # Print to stderr with markers for parsing
        # self._print_to_stderr(error_data)
        
        return error_data
        
    def capture_http_error(
        self,
        exception: requests.exceptions.RequestException,
        endpoint: str,
        context: Optional[Dict[str, Any]] = None,
        request_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Specialized method for capturing HTTP errors from requests library
        """
       
        status_code = None
        response_data = None
        error_type = "HTTP_ERROR"
        
        print(f"exception: {exception}")
        print(f"hasattr(exception, 'response'): {hasattr(exception, 'response')}")
        print(f"exception.response: {exception.response}")
        
        if getattr(exception, 'response', None) is not None:
            status_code = exception.response.status_code
            
            # Determine severity based on status code
            error_type = f"HTTP_ERROR: {status_code}"
            
            # Try to extract response data
            try:
                response_data = exception.response.json()
            except (ValueError, json.JSONDecodeError):
                response_data = exception.response.text[:2000]  # Limit text size
        
        return self.capture_error(
            message=str(exception),
            error_type=error_type,
            endpoint=endpoint,
            status_code=status_code,
            request_data=request_data,
            response_data=response_data,
            exception=exception,
            context=context
        )
    
    def wrap_request(
        self,
        request_func: Callable[[], requests.Response],
        endpoint: str,
        context: Optional[Dict[str, Any]] = None,
        request_data: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Wrapper for HTTP requests that automatically captures errors
        """
        try:
            response = request_func()
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.capture_http_error(e, endpoint, context, request_data)
            raise
        except Exception as e:
            self.capture_error(
                message=str(e),
                error_type="REQUEST_EXECUTION_ERROR",
                endpoint=endpoint,
                exception=e,
                context=context,
                request_data=request_data
            )
            raise
    
    def get_all_errors(self) -> List[Dict[str, Any]]:
        """Get all errors for this execution"""
        return self.errors
    
    def _sanitize_data(self, data: Union[Dict[str, Any], str]) -> Union[Dict[str, Any], str]:
        """Sanitize sensitive data before logging"""
        if isinstance(data, str):
            return data
            
        sanitized = data.copy() if isinstance(data, dict) else data
        
        # Example sanitization (would need to be customized)
        sensitive_fields = ["password", "token", "api_key", "secret", "authorization"]
        
        if isinstance(sanitized, dict):
            for key in sanitized:
                # Check if the key contains any sensitive field name
                if any(field in key.lower() for field in sensitive_fields):
                    sanitized[key] = "[REDACTED]"
        
        return sanitized
    
    def _write_to_json_file(self, error_data: Dict[str, Any]) -> None:
        """Write error to JSON file"""
        filename = f"errors/{self.integration_name}_{error_data['error_id']}.json"
        with open(filename, "w") as f:
            json.dump(error_data, f, indent=2)
    
    def _write_to_summary_file(self, error_data: Dict[str, Any]) -> None:
        """Write error to summary file for human reading"""
        with open("errors/error_summary.txt", "a") as f:
            f.write(f"ERROR [{error_data['error_id']}]: {error_data['message']}\n")
            f.write(f"Integration: {self.integration_name}\n")
            f.write(f"Type: {error_data['error_type']}\n")
            f.write(f"Timestamp: {error_data['timestamp']}\n")
            if 'endpoint' in error_data:
                f.write(f"Endpoint: {error_data['endpoint']}\n")
            if 'status_code' in error_data:
                f.write(f"Status Code: {error_data['status_code']}\n")
            f.write(f"Stack Trace: {error_data['stack_trace'][:500]}...\n")
            f.write("-" * 80 + "\n")
    
    def _print_to_stderr(self, error_data: Dict[str, Any]) -> None:
        """Print error to stderr with markers for easy parsing"""
        print(f"ERROR_JSON_START{json.dumps(error_data)}ERROR_JSON_END", file=sys.stderr)

# api_error_monitor/decorators.py

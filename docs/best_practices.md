# Xray GraphQL Integration Best Practices

This guide outlines recommended practices for using the Xray GraphQL integration effectively and securely.

## API Token Management

### DO:
- Store API tokens in environment variables or secure configuration management systems
- Use different tokens for different environments (development, staging, production)
- Regularly rotate API tokens
- Set appropriate token permissions (read/write access only where needed)

### DON'T:
- Hardcode API tokens in source code
- Share tokens across different applications or teams
- Commit tokens to version control
- Use production tokens in development environments

## Error Handling

### DO:
- Catch and handle specific exceptions (`XrayAuthenticationError`, `XrayAPIError`)
- Log errors with appropriate context
- Implement retry logic for transient failures
- Validate input data before making API calls

### DON'T:
- Catch generic exceptions without proper handling
- Expose sensitive information in error messages
- Ignore error responses from the API
- Continue execution after critical errors

## Rate Limiting

### DO:
- Implement exponential backoff for retries
- Monitor API usage and response times
- Cache frequently accessed data
- Batch operations where possible

### DON'T:
- Send too many requests in parallel
- Ignore rate limit headers
- Retry failed requests without delay
- Make unnecessary API calls

## Code Organization

### DO:
- Separate concerns (models, client, business logic)
- Use type hints and documentation
- Follow consistent naming conventions
- Create reusable utility functions

### DON'T:
- Mix business logic with API calls
- Duplicate code across different modules
- Use ambiguous names or abbreviations
- Ignore code style guidelines

## Testing

### DO:
- Write unit tests for all components
- Mock API responses in tests
- Test error scenarios
- Use integration tests for critical paths

### DON'T:
- Use production credentials in tests
- Skip error case testing
- Rely solely on manual testing
- Ignore test coverage

## Example: Error Handling Implementation

```python
from src.client import XrayClient, XrayAPIError, XrayAuthenticationError

def create_test_suite():
    try:
        client = XrayClient()
        # Create test cases and test set
        
    except XrayAuthenticationError as e:
        logger.error("Authentication failed: %s", str(e))
        # Handle authentication error (e.g., refresh token)
        
    except XrayAPIError as e:
        logger.error("API error: %s", str(e))
        # Handle API error (e.g., retry with backoff)
        
    except Exception as e:
        logger.critical("Unexpected error: %s", str(e))
        # Handle unexpected errors
```

## Example: Rate Limiting Implementation

```python
import time
from functools import wraps

def rate_limit(max_per_second):
    min_interval = 1.0 / max_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(2)  # Maximum 2 calls per second
def create_test_case(client, data):
    return client.create_test_case(**data)
```

## Example: Caching Implementation

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedXrayClient:
    @lru_cache(maxsize=100)
    def get_test_case(self, test_case_id: str):
        return super().get_test_case(test_case_id)

    def invalidate_cache(self):
        self.get_test_case.cache_clear()
```

## Performance Optimization

### DO:
- Use connection pooling
- Implement caching for frequently accessed data
- Batch related operations
- Monitor and optimize query complexity

### DON'T:
- Make redundant API calls
- Fetch unnecessary fields
- Ignore performance metrics
- Use blocking operations in async code

## Security Considerations

### DO:
- Use HTTPS for all API communications
- Validate and sanitize input data
- Implement proper authentication
- Follow the principle of least privilege

### DON'T:
- Store sensitive data in logs
- Disable SSL verification
- Share credentials between environments
- Expose internal errors to users

## Monitoring and Logging

### DO:
- Implement structured logging
- Monitor API response times
- Track error rates and types
- Set up alerts for critical issues

### DON'T:
- Log sensitive information
- Ignore warning signs
- Rely on manual monitoring
- Mix log levels inappropriately

## Example: Structured Logging

```python
import structlog

logger = structlog.get_logger()

def create_test_plan(client, name, test_sets):
    logger.info("creating_test_plan",
                name=name,
                test_set_count=len(test_sets))
    try:
        plan = client.create_test_plan(name=name, test_sets=test_sets)
        logger.info("test_plan_created",
                   plan_id=plan.id,
                   test_set_count=len(test_sets))
        return plan
    except Exception as e:
        logger.error("test_plan_creation_failed",
                    error=str(e),
                    name=name)
        raise
```

## Maintenance and Updates

### DO:
- Keep dependencies updated
- Monitor for API changes
- Document breaking changes
- Maintain backwards compatibility

### DON'T:
- Use deprecated features
- Skip security updates
- Ignore API announcements
- Make breaking changes without notice

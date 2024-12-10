"""
Advanced example demonstrating more complex usage patterns of the Xray GraphQL client.
This example shows:
1. Custom error handling and retries
2. Rate limiting
3. Batch operations
4. Caching
5. Structured logging
"""

import os
import sys
import time
import structlog
from datetime import datetime, timedelta
from functools import wraps, lru_cache
from typing import List, Optional, Any, Callable

# Add the parent directory to the Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.client import XrayClient, XrayAPIError, XrayAuthenticationError
from src.models import TestStep, TestCase, ExecutionStatus, TestType

# Configure structured logging
logger = structlog.get_logger()

def retry_with_backoff(retries: int = 3, backoff_in_seconds: int = 1):
    """
    Decorator that implements retry logic with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retry_count = 0
            while retry_count < retries:
                try:
                    return func(*args, **kwargs)
                except (XrayAPIError, XrayAuthenticationError) as e:
                    retry_count += 1
                    if retry_count == retries:
                        logger.error("max_retries_reached",
                                   function=func.__name__,
                                   error=str(e))
                        raise
                    
                    wait_time = (backoff_in_seconds * 2 ** retry_count)
                    logger.warning("retrying_operation",
                                 function=func.__name__,
                                 attempt=retry_count,
                                 wait_time=wait_time)
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

def rate_limit(max_per_second: int = 2):
    """
    Decorator that implements rate limiting.
    """
    min_interval = 1.0 / float(max_per_second)
    last_called = [0.0]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

class CachedXrayClient(XrayClient):
    """
    Extended XrayClient with caching capabilities.
    """
    
    @lru_cache(maxsize=100)
    def get_test_case(self, test_case_id: str) -> TestCase:
        return super().get_test_case(test_case_id)

    def invalidate_cache(self) -> None:
        self.get_test_case.cache_clear()

class TestSuiteManager:
    """
    High-level manager for creating and managing test suites.
    """
    
    def __init__(self):
        self.client = CachedXrayClient()
        self.logger = structlog.get_logger()

    @retry_with_backoff(retries=3)
    @rate_limit(max_per_second=2)
    def create_test_suite(self, name: str, test_cases: List[dict]) -> None:
        """
        Creates a complete test suite with multiple test cases.
        """
        try:
            self.logger.info("creating_test_suite", name=name)
            
            # Create test cases in batch
            created_cases = []
            for tc in test_cases:
                test_case = self.client.create_test_case(**tc)
                created_cases.append(test_case)
                self.logger.info("test_case_created",
                               test_case_id=test_case.id,
                               summary=test_case.summary)

            # Create test set
            test_set = self.client.create_test_set(
                name=f"{name} Test Set",
                test_cases=created_cases,
                labels=["automated", "regression"]
            )
            self.logger.info("test_set_created",
                           test_set_id=test_set.id,
                           test_case_count=len(created_cases))

            # Create test plan
            start_date = datetime.now().isoformat()
            end_date = (datetime.now() + timedelta(days=14)).isoformat()
            
            test_plan = self.client.create_test_plan(
                name=f"{name} Test Plan",
                test_sets=[test_set],
                start_date=start_date,
                end_date=end_date
            )
            self.logger.info("test_plan_created",
                           test_plan_id=test_plan.id,
                           start_date=start_date,
                           end_date=end_date)

        except Exception as e:
            self.logger.error("test_suite_creation_failed",
                            error=str(e),
                            name=name)
            raise

def main():
    try:
        # Initialize the test suite manager
        manager = TestSuiteManager()
        
        # Define complex test scenarios
        test_cases = [
            {
                "summary": "User Registration Flow",
                "steps": [
                    TestStep(
                        id="1",
                        action="Navigate to registration page",
                        data="https://example.com/register",
                        expected_result="Registration form is displayed"
                    ),
                    TestStep(
                        id="2",
                        action="Fill in user details",
                        data="""
                        {
                            "email": "test@example.com",
                            "password": "****",
                            "confirm_password": "****",
                            "name": "Test User",
                            "country": "US"
                        }
                        """,
                        expected_result="All fields are filled correctly"
                    ),
                    TestStep(
                        id="3",
                        action="Accept terms and conditions",
                        expected_result="Terms accepted"
                    ),
                    TestStep(
                        id="4",
                        action="Click register button",
                        expected_result="Account created successfully"
                    ),
                    TestStep(
                        id="5",
                        action="Verify confirmation email",
                        expected_result="Email received and contains activation link"
                    )
                ],
                "description": "Complete user registration flow including email verification",
                "test_type": TestType.MANUAL,
                "labels": ["registration", "user-management", "email"]
            },
            {
                "summary": "Password Reset Flow",
                "steps": [
                    TestStep(
                        id="1",
                        action="Navigate to login page",
                        data="https://example.com/login",
                        expected_result="Login page is displayed"
                    ),
                    TestStep(
                        id="2",
                        action="Click forgot password link",
                        expected_result="Password reset page is displayed"
                    ),
                    TestStep(
                        id="3",
                        action="Enter email address",
                        data="test@example.com",
                        expected_result="Reset email sent successfully"
                    ),
                    TestStep(
                        id="4",
                        action="Click reset link in email",
                        expected_result="Password reset form is displayed"
                    ),
                    TestStep(
                        id="5",
                        action="Enter and confirm new password",
                        data="new_password",
                        expected_result="Password updated successfully"
                    )
                ],
                "description": "Complete password reset flow including email verification",
                "test_type": TestType.MANUAL,
                "labels": ["password-reset", "user-management", "email"]
            }
        ]

        # Create the test suite
        manager.create_test_suite("User Management", test_cases)
        
        print("Advanced example completed successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

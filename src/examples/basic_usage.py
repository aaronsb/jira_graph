"""
Basic example demonstrating common usage patterns of the Xray GraphQL client.
This example shows how to:
1. Create test cases with steps
2. Organize test cases into test sets
3. Create a test plan
4. Record test executions
"""

import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.client import XrayClient
from src.models import TestStep, ExecutionStatus, TestType

def main():
    try:
        # Initialize the client
        client = XrayClient()
        
        # Create test steps for login functionality
        login_steps = [
            TestStep(
                id="1",
                action="Navigate to login page",
                data="https://example.com/login",
                expected_result="Login page is displayed with username and password fields"
            ),
            TestStep(
                id="2",
                action="Enter valid credentials",
                data="username: test@example.com, password: ****",
                expected_result="Credentials are entered in respective fields"
            ),
            TestStep(
                id="3",
                action="Click login button",
                expected_result="User is successfully logged in and redirected to dashboard"
            )
        ]

        # Create test steps for logout functionality
        logout_steps = [
            TestStep(
                id="1",
                action="Click user profile menu",
                expected_result="Profile menu dropdown is displayed"
            ),
            TestStep(
                id="2",
                action="Click logout option",
                expected_result="User is logged out and redirected to login page"
            )
        ]

        print("Creating test cases...")
        
        # Create test cases
        login_test = client.create_test_case(
            summary="Verify user login with valid credentials",
            steps=login_steps,
            description="Test the user login process with valid credentials",
            test_type=TestType.MANUAL,
            labels=["login", "authentication", "smoke-test"]
        )
        
        logout_test = client.create_test_case(
            summary="Verify user logout functionality",
            steps=logout_steps,
            description="Test the user logout process",
            test_type=TestType.MANUAL,
            labels=["logout", "authentication", "smoke-test"]
        )

        print(f"Created test cases: {login_test.id}, {logout_test.id}")

        # Create a test set containing both test cases
        print("\nCreating test set...")
        test_set = client.create_test_set(
            name="Authentication Test Suite",
            test_cases=[login_test, logout_test],
            labels=["authentication", "smoke-test"]
        )
        
        print(f"Created test set: {test_set.id}")

        # Create a test plan
        print("\nCreating test plan...")
        start_date = datetime.now().isoformat()
        end_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        test_plan = client.create_test_plan(
            name="Sprint 1 Smoke Tests",
            test_sets=[test_set],
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"Created test plan: {test_plan.id}")

        # Record test executions
        print("\nRecording test executions...")
        
        # Record successful login test execution
        login_execution = client.record_test_execution(
            test_case=login_test,
            status=ExecutionStatus.PASS,
            executed_by="john.doe@example.com",
            environment="staging"
        )
        
        print(f"Recorded login test execution: {login_execution.id} - {login_execution.status}")

        # Record successful logout test execution
        logout_execution = client.record_test_execution(
            test_case=logout_test,
            status=ExecutionStatus.PASS,
            executed_by="john.doe@example.com",
            environment="staging"
        )
        
        print(f"Recorded logout test execution: {logout_execution.id} - {logout_execution.status}")

        print("\nAll operations completed successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

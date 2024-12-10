import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from dotenv import load_dotenv
from .models import (
    TestCase, TestSet, TestPlan, TestExecution, TestStep,
    ExecutionStatus, TestType, CustomField
)

class XrayClientError(Exception):
    """Base exception for Xray client errors"""
    pass

class XrayAuthenticationError(XrayClientError):
    """Raised when authentication fails"""
    pass

class XrayAPIError(XrayClientError):
    """Raised when the API returns an error"""
    pass

class XrayClient:
    """
    Client for interacting with Xray's GraphQL API.
    
    This client provides a Pythonic interface to Xray's GraphQL API, handling
    authentication, request formatting, and error handling.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Xray client.
        
        Args:
            config_path: Optional path to .env file. If not provided,
                        will look for .env in config directory.
        """
        self._load_config(config_path)
        self._setup_client()

    def _load_config(self, config_path: Optional[str] = None):
        """Load configuration from environment variables"""
        if config_path:
            load_dotenv(config_path)
        else:
            default_path = os.path.join(os.path.dirname(__file__), '../config/.env')
            load_dotenv(default_path)

        self.endpoint = os.getenv('XRAY_API_ENDPOINT')
        self.token = os.getenv('XRAY_API_TOKEN')
        
        if not self.endpoint or not self.token:
            raise XrayClientError("Missing required configuration. Please set XRAY_API_ENDPOINT and XRAY_API_TOKEN")

        self.timeout = int(os.getenv('XRAY_REQUEST_TIMEOUT', '30'))
        self.environment = os.getenv('XRAY_ENVIRONMENT', 'staging')
        self.default_project = os.getenv('XRAY_DEFAULT_PROJECT')

    def _setup_client(self):
        """Configure the GraphQL client"""
        try:
            transport = RequestsHTTPTransport(
                url=self.endpoint,
                headers={'Authorization': f'Bearer {self.token}'},
                timeout=self.timeout
            )
            self.client = Client(
                transport=transport,
                fetch_schema_from_transport=True
            )
        except Exception as e:
            raise XrayAuthenticationError(f"Failed to initialize client: {str(e)}")

    def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query and handle errors.
        
        Args:
            query: The GraphQL query string
            variables: Optional variables for the query
            
        Returns:
            Dict containing the query result
            
        Raises:
            XrayAPIError: If the API returns an error
        """
        try:
            return self.client.execute(gql(query), variable_values=variables)
        except Exception as e:
            raise XrayAPIError(f"API request failed: {str(e)}")

    def create_test_case(self, summary: str, steps: List[TestStep], **kwargs) -> TestCase:
        """
        Create a new test case in Xray.
        
        Args:
            summary: Test case summary
            steps: List of TestStep objects
            **kwargs: Additional test case fields (description, precondition, etc.)
            
        Returns:
            TestCase object representing the created test case
        """
        mutation = """
            mutation CreateTestCase($input: TestCaseInput!) {
                createTestCase(input: $input) {
                    id
                    summary
                    description
                    steps {
                        id
                        action
                        data
                        expectedResult
                    }
                }
            }
        """
        
        variables = {
            "input": {
                "summary": summary,
                "steps": [step.to_dict() for step in steps],
                **kwargs
            }
        }
        
        result = self._execute_query(mutation, variables)
        return TestCase(**result["createTestCase"])

    def create_test_set(self, name: str, test_cases: List[TestCase], labels: Optional[List[str]] = None) -> TestSet:
        """
        Create a new test set containing the specified test cases.
        
        Args:
            name: Name of the test set
            test_cases: List of TestCase objects to include
            labels: Optional list of labels to apply
            
        Returns:
            TestSet object representing the created test set
        """
        mutation = """
            mutation CreateTestSet($input: TestSetInput!) {
                createTestSet(input: $input) {
                    id
                    name
                    testCases {
                        id
                        summary
                    }
                }
            }
        """
        
        variables = {
            "input": {
                "name": name,
                "testCases": [{"id": tc.id} for tc in test_cases],
                "labels": labels
            }
        }
        
        result = self._execute_query(mutation, variables)
        return TestSet(**result["createTestSet"])

    def create_test_plan(self, name: str, **kwargs) -> TestPlan:
        """
        Create a new test plan.
        
        Args:
            name: Name of the test plan
            **kwargs: Additional test plan fields (start_date, end_date, etc.)
            
        Returns:
            TestPlan object representing the created test plan
        """
        mutation = """
            mutation CreateTestPlan($input: TestPlanInput!) {
                createTestPlan(input: $input) {
                    id
                    name
                    startDate
                    endDate
                    testSets {
                        id
                        name
                    }
                }
            }
        """
        
        variables = {
            "input": {
                "name": name,
                **kwargs
            }
        }
        
        result = self._execute_query(mutation, variables)
        return TestPlan(**result["createTestPlan"])

    def record_test_execution(
        self,
        test_case: TestCase,
        status: ExecutionStatus,
        executed_by: str,
        environment: Optional[str] = None
    ) -> TestExecution:
        """
        Record a test execution result.
        
        Args:
            test_case: The TestCase that was executed
            status: ExecutionStatus indicating the result
            executed_by: Username or email of the person who executed the test
            environment: Optional environment where the test was executed
            
        Returns:
            TestExecution object representing the recorded execution
        """
        mutation = """
            mutation RecordTestExecution($input: TestExecutionInput!) {
                recordTestExecution(input: $input) {
                    id
                    status
                    executedBy
                    executedOn
                    testCase {
                        id
                        summary
                    }
                }
            }
        """
        
        variables = {
            "input": {
                "testCase": {"id": test_case.id},
                "status": status.value,
                "executedBy": executed_by,
                "executedOn": datetime.utcnow().isoformat(),
                "environment": environment or self.environment
            }
        }
        
        result = self._execute_query(mutation, variables)
        return TestExecution(**result["recordTestExecution"])

    def get_test_case(self, test_case_id: str) -> TestCase:
        """
        Retrieve a test case by ID.
        
        Args:
            test_case_id: The ID of the test case to retrieve
            
        Returns:
            TestCase object
        """
        query = """
            query GetTestCase($id: ID!) {
                testCase(id: $id) {
                    id
                    summary
                    description
                    steps {
                        id
                        action
                        data
                        expectedResult
                    }
                }
            }
        """
        
        result = self._execute_query(query, {"id": test_case_id})
        return TestCase(**result["testCase"])

    def get_test_plan(self, test_plan_id: str) -> TestPlan:
        """
        Retrieve a test plan by ID.
        
        Args:
            test_plan_id: The ID of the test plan to retrieve
            
        Returns:
            TestPlan object
        """
        query = """
            query GetTestPlan($id: ID!) {
                testPlan(id: $id) {
                    id
                    name
                    startDate
                    endDate
                    testSets {
                        id
                        name
                    }
                }
            }
        """
        
        result = self._execute_query(query, {"id": test_plan_id})
        return TestPlan(**result["testPlan"])

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Enums
class TestType(str, Enum):
    MANUAL = "MANUAL"
    CUCUMBER = "CUCUMBER"
    GENERIC = "GENERIC"
    ROBOT = "ROBOT"

class ExecutionStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"

# Data Classes
@dataclass
class TestStep:
    id: str
    action: str
    expected_result: str
    data: Optional[str] = None

@dataclass
class TestCase:
    id: str
    summary: str
    steps: List[TestStep]
    description: Optional[str] = None
    precondition: Optional[str] = None
    labels: Optional[List[str]] = None
    priority: Optional[str] = None
    test_type: Optional[TestType] = None

@dataclass
class TestSet:
    id: str
    name: str
    test_cases: List[TestCase]
    labels: Optional[List[str]] = None

@dataclass
class TestPlan:
    id: str
    name: str
    test_sets: Optional[List[TestSet]] = None
    test_cases: Optional[List[TestCase]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@dataclass
class TestExecution:
    id: str
    test_case: TestCase
    status: ExecutionStatus
    executed_by: str
    executed_on: str
    environment: Optional[str] = None

class XrayClient:
    def __init__(self, endpoint: str, token: str):
        transport = RequestsHTTPTransport(
            url=endpoint,
            headers={'Authorization': f'Bearer {token}'}
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def create_test_case(self, summary: str, steps: List[TestStep], **kwargs) -> TestCase:
        mutation = gql("""
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
        """)
        
        variables = {
            "input": {
                "summary": summary,
                "steps": [
                    {
                        "id": step.id,
                        "action": step.action,
                        "data": step.data,
                        "expectedResult": step.expected_result
                    } for step in steps
                ],
                **kwargs
            }
        }
        
        result = self.client.execute(mutation, variable_values=variables)
        return TestCase(**result["createTestCase"])

    def create_test_set(self, name: str, test_cases: List[TestCase], labels: Optional[List[str]] = None) -> TestSet:
        mutation = gql("""
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
        """)
        
        variables = {
            "input": {
                "name": name,
                "testCases": [{"id": tc.id} for tc in test_cases],
                "labels": labels
            }
        }
        
        result = self.client.execute(mutation, variable_values=variables)
        return TestSet(**result["createTestSet"])

    def create_test_plan(self, name: str, **kwargs) -> TestPlan:
        mutation = gql("""
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
        """)
        
        variables = {
            "input": {
                "name": name,
                **kwargs
            }
        }
        
        result = self.client.execute(mutation, variable_values=variables)
        return TestPlan(**result["createTestPlan"])

    def record_test_execution(self, test_case: TestCase, status: ExecutionStatus, executed_by: str,
                            environment: Optional[str] = None) -> TestExecution:
        mutation = gql("""
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
        """)
        
        variables = {
            "input": {
                "testCase": {"id": test_case.id},
                "status": status.value,
                "executedBy": executed_by,
                "executedOn": datetime.utcnow().isoformat(),
                "environment": environment
            }
        }
        
        result = self.client.execute(mutation, variable_values=variables)
        return TestExecution(**result["recordTestExecution"])

def main():
    # Initialize client
    client = XrayClient(
        endpoint="https://xray.cloud.getxray.app/api/v2/graphql",
        token="your-api-token"
    )

    # Create test steps
    steps = [
        TestStep(
            id="1",
            action="Navigate to login page",
            data="https://example.com/login",
            expected_result="Login page is displayed"
        ),
        TestStep(
            id="2",
            action="Enter valid credentials",
            data="username: test@example.com, password: ****",
            expected_result="Credentials are accepted"
        ),
        TestStep(
            id="3",
            action="Click login button",
            expected_result="User is successfully logged in and redirected to dashboard"
        )
    ]

    # Create test case
    test_case = client.create_test_case(
        summary="Verify user login functionality",
        steps=steps,
        description="Test the user login process with valid credentials",
        test_type=TestType.MANUAL,
        labels=["login", "authentication"]
    )

    # Create test set
    test_set = client.create_test_set(
        name="Authentication Test Suite",
        test_cases=[test_case],
        labels=["authentication", "regression"]
    )

    # Create test plan
    test_plan = client.create_test_plan(
        name="Sprint 23 Regression",
        test_sets=[test_set],
        start_date="2024-01-01",
        end_date="2024-01-15"
    )

    # Record test execution
    test_execution = client.record_test_execution(
        test_case=test_case,
        status=ExecutionStatus.PASS,
        executed_by="john.doe@example.com",
        environment="staging"
    )

    print(f"Test Plan created: {test_plan.id}")
    print(f"Test Execution recorded: {test_execution.id}")

if __name__ == "__main__":
    main()

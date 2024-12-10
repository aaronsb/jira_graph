from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime

class TestType(str, Enum):
    """Test types supported by Xray"""
    MANUAL = "MANUAL"
    CUCUMBER = "CUCUMBER"
    GENERIC = "GENERIC"
    ROBOT = "ROBOT"

class ExecutionStatus(str, Enum):
    """Possible statuses for test executions"""
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"

@dataclass
class TestStep:
    """Represents a single step in a test case"""
    id: str
    action: str
    expected_result: str
    data: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert the test step to a dictionary for GraphQL mutations"""
        return {
            "id": self.id,
            "action": self.action,
            "expectedResult": self.expected_result,
            "data": self.data
        }

@dataclass
class TestCase:
    """Represents a test case in Xray"""
    id: str
    summary: str
    steps: List[TestStep]
    description: Optional[str] = None
    precondition: Optional[str] = None
    labels: Optional[List[str]] = None
    priority: Optional[str] = None
    test_type: Optional[TestType] = None

    def to_dict(self) -> dict:
        """Convert the test case to a dictionary for GraphQL mutations"""
        return {
            "id": self.id,
            "summary": self.summary,
            "steps": [step.to_dict() for step in self.steps],
            "description": self.description,
            "precondition": self.precondition,
            "labels": self.labels,
            "priority": self.priority,
            "testType": self.test_type.value if self.test_type else None
        }

@dataclass
class TestSet:
    """Represents a test set (collection of test cases)"""
    id: str
    name: str
    test_cases: List[TestCase]
    labels: Optional[List[str]] = None

    def to_dict(self) -> dict:
        """Convert the test set to a dictionary for GraphQL mutations"""
        return {
            "id": self.id,
            "name": self.name,
            "testCases": [{"id": tc.id} for tc in self.test_cases],
            "labels": self.labels
        }

@dataclass
class TestPlan:
    """Represents a test plan in Xray"""
    id: str
    name: str
    test_sets: Optional[List[TestSet]] = None
    test_cases: Optional[List[TestCase]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert the test plan to a dictionary for GraphQL mutations"""
        return {
            "id": self.id,
            "name": self.name,
            "testSets": [ts.to_dict() for ts in self.test_sets] if self.test_sets else None,
            "testCases": [tc.to_dict() for tc in self.test_cases] if self.test_cases else None,
            "startDate": self.start_date,
            "endDate": self.end_date
        }

@dataclass
class TestExecution:
    """Represents a test execution record"""
    id: str
    test_case: TestCase
    status: ExecutionStatus
    executed_by: str
    executed_on: str
    environment: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert the test execution to a dictionary for GraphQL mutations"""
        return {
            "id": self.id,
            "testCase": {"id": self.test_case.id},
            "status": self.status.value,
            "executedBy": self.executed_by,
            "executedOn": self.executed_on,
            "environment": self.environment
        }

@dataclass
class CustomField:
    """Represents a custom field in Xray"""
    id: str
    name: str
    value: str

    def to_dict(self) -> dict:
        """Convert the custom field to a dictionary for GraphQL mutations"""
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value
        }

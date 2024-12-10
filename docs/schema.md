# Xray GraphQL Schema Documentation

This document outlines the GraphQL schema for Xray's API, including available types, queries, and mutations.

## Types

### TestCase
```graphql
type TestCase {
  id: ID!
  summary: String!
  description: String
  precondition: String
  steps: [TestStep]!
  labels: [String]
  priority: Priority
  testType: TestType
  customFields: [CustomField]
}
```

### TestStep
```graphql
type TestStep {
  id: ID!
  action: String!
  data: String
  expectedResult: String!
}
```

### TestSet
```graphql
type TestSet {
  id: ID!
  name: String!
  testCases: [TestCase]!
  labels: [String]
}
```

### TestPlan
```graphql
type TestPlan {
  id: ID!
  name: String!
  testSets: [TestSet]
  testCases: [TestCase]
  startDate: String
  endDate: String
}
```

### TestExecution
```graphql
type TestExecution {
  id: ID!
  testCase: TestCase!
  status: ExecutionStatus!
  executedBy: String!
  executedOn: String!
  environment: String
  evidence: [Evidence]
}
```

### Enums

```graphql
enum TestType {
  MANUAL
  CUCUMBER
  GENERIC
  ROBOT
}

enum ExecutionStatus {
  PASS
  FAIL
  BLOCKED
  PENDING
}

enum Priority {
  LOW
  MEDIUM
  HIGH
}
```

## Queries

### Get Test Case
```graphql
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
    labels
    testType
  }
}
```

### Get Test Plan
```graphql
query GetTestPlan($id: ID!) {
  testPlan(id: $id) {
    id
    name
    startDate
    endDate
    testSets {
      id
      name
      testCases {
        id
        summary
      }
    }
  }
}
```

### Get Test Set
```graphql
query GetTestSet($id: ID!) {
  testSet(id: $id) {
    id
    name
    testCases {
      id
      summary
      steps {
        id
        action
        expectedResult
      }
    }
    labels
  }
}
```

## Mutations

### Create Test Case
```graphql
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
```

Input type:
```graphql
input TestCaseInput {
  summary: String!
  description: String
  precondition: String
  steps: [TestStepInput]!
  labels: [String]
  priority: Priority
  testType: TestType
  customFields: [CustomFieldInput]
}
```

### Create Test Set
```graphql
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
```

Input type:
```graphql
input TestSetInput {
  name: String!
  testCases: [TestCaseReference]!
  labels: [String]
}
```

### Create Test Plan
```graphql
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
```

Input type:
```graphql
input TestPlanInput {
  name: String!
  testSets: [TestSetReference]
  testCases: [TestCaseReference]
  startDate: String
  endDate: String
}
```

### Record Test Execution
```graphql
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
```

Input type:
```graphql
input TestExecutionInput {
  testCase: TestCaseReference!
  status: ExecutionStatus!
  executedBy: String!
  executedOn: String!
  environment: String
}
```

## Example Usage

### Creating a Test Case with Steps
```graphql
mutation {
  createTestCase(input: {
    summary: "Verify user login"
    description: "Test the user login functionality"
    steps: [
      {
        id: "1"
        action: "Navigate to login page"
        data: "https://example.com/login"
        expectedResult: "Login page is displayed"
      },
      {
        id: "2"
        action: "Enter credentials"
        data: "username: test@example.com"
        expectedResult: "Credentials accepted"
      }
    ]
    testType: MANUAL
    labels: ["login", "authentication"]
  }) {
    id
    summary
    steps {
      id
      action
    }
  }
}
```

### Recording a Test Execution
```graphql
mutation {
  recordTestExecution(input: {
    testCase: { id: "TC-123" }
    status: PASS
    executedBy: "john.doe@example.com"
    executedOn: "2024-01-15T10:00:00Z"
    environment: "staging"
  }) {
    id
    status
    executedBy
  }
}
```

## Error Handling

The API returns errors in the following format:
```json
{
  "errors": [
    {
      "message": "Error message",
      "path": ["path", "to", "field"],
      "extensions": {
        "code": "ERROR_CODE",
        "classification": "ERROR_TYPE"
      }
    }
  ]
}
```

Common error codes:
- `AUTHENTICATION_ERROR`: Invalid or missing authentication
- `VALIDATION_ERROR`: Invalid input data
- `NOT_FOUND`: Requested resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server-side error

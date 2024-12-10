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

type TestStep {
  id: ID!
  action: String!
  data: String
  expectedResult: String!
}

type TestSet {
  id: ID!
  name: String!
  testCases: [TestCase]!
  labels: [String]
}

type TestPlan {
  id: ID!
  name: String!
  testSets: [TestSet]
  testCases: [TestCase]
  startDate: String
  endDate: String
}

type TestExecution {
  id: ID!
  testCase: TestCase!
  status: ExecutionStatus!
  executedBy: String!
  executedOn: String!
  environment: String
  evidence: [Evidence]
}

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
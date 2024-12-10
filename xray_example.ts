import { GraphQLClient } from 'graphql-request';

// Types based on the schema
interface TestStep {
  id: string;
  action: string;
  data?: string;
  expectedResult: string;
}

interface TestCase {
  id: string;
  summary: string;
  description?: string;
  precondition?: string;
  steps: TestStep[];
  labels?: string[];
  priority?: string;
  testType?: 'MANUAL' | 'CUCUMBER' | 'GENERIC' | 'ROBOT';
}

interface TestSet {
  id: string;
  name: string;
  testCases: TestCase[];
  labels?: string[];
}

interface TestPlan {
  id: string;
  name: string;
  testSets?: TestSet[];
  testCases?: TestCase[];
  startDate?: string;
  endDate?: string;
}

interface TestExecution {
  id: string;
  testCase: TestCase;
  status: 'PASS' | 'FAIL' | 'BLOCKED' | 'PENDING';
  executedBy: string;
  executedOn: string;
  environment?: string;
}

// Example implementation
class XrayClient {
  private client: GraphQLClient;

  constructor(endpoint: string, token: string) {
    this.client = new GraphQLClient(endpoint, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  // Create a new test case
  async createTestCase(input: Omit<TestCase, 'id'>): Promise<TestCase> {
    const mutation = `
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
    `;

    return this.client.request(mutation, { input });
  }

  // Create a test set
  async createTestSet(input: Omit<TestSet, 'id'>): Promise<TestSet> {
    const mutation = `
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
    `;

    return this.client.request(mutation, { input });
  }

  // Create a test plan
  async createTestPlan(input: Omit<TestPlan, 'id'>): Promise<TestPlan> {
    const mutation = `
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
    `;

    return this.client.request(mutation, { input });
  }

  // Record a test execution
  async recordTestExecution(input: Omit<TestExecution, 'id'>): Promise<TestExecution> {
    const mutation = `
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
    `;

    return this.client.request(mutation, { input });
  }
}

// Usage example
async function main() {
  const client = new XrayClient(
    'https://xray.cloud.getxray.app/api/v2/graphql',
    'your-api-token'
  );

  // Create a test case
  const testCase = await client.createTestCase({
    summary: 'Verify user login functionality',
    description: 'Test the user login process with valid credentials',
    steps: [
      {
        id: '1',
        action: 'Navigate to login page',
        data: 'https://example.com/login',
        expectedResult: 'Login page is displayed'
      },
      {
        id: '2',
        action: 'Enter valid credentials',
        data: 'username: test@example.com, password: ****',
        expectedResult: 'Credentials are accepted'
      },
      {
        id: '3',
        action: 'Click login button',
        expectedResult: 'User is successfully logged in and redirected to dashboard'
      }
    ],
    testType: 'MANUAL',
    labels: ['login', 'authentication']
  });

  // Create a test set
  const testSet = await client.createTestSet({
    name: 'Authentication Test Suite',
    testCases: [testCase],
    labels: ['authentication', 'regression']
  });

  // Create a test plan
  const testPlan = await client.createTestPlan({
    name: 'Sprint 23 Regression',
    testSets: [testSet],
    startDate: '2024-01-01',
    endDate: '2024-01-15'
  });

  // Record test execution
  const testExecution = await client.recordTestExecution({
    testCase: testCase,
    status: 'PASS',
    executedBy: 'john.doe@example.com',
    executedOn: new Date().toISOString(),
    environment: 'staging'
  });

  console.log('Test Plan created:', testPlan.id);
  console.log('Test Execution recorded:', testExecution.id);
}

// Run the example
main().catch(console.error);

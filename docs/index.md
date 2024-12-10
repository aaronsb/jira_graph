# Xray GraphQL API Documentation

Welcome to the Xray GraphQL API documentation. This documentation package provides comprehensive information about using the Xray GraphQL API integration.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Schema Reference](schema.md)
3. [Best Practices](best_practices.md)

## Getting Started

The Xray GraphQL API allows you to interact with Xray's test management features through a powerful GraphQL interface. This documentation will help you understand and effectively use the API.

### Quick Links

- [Schema Documentation](schema.md) - Comprehensive schema reference with types, queries, mutations, and examples
- [Best Practices](best_practices.md) - Guidelines for effective and secure API usage

### Authentication

To use the Xray GraphQL API, you'll need to:
1. Obtain API credentials from your Xray instance
2. Store credentials securely (see [Best Practices - API Token Management](best_practices.md#api-token-management))
3. Include authentication in your API requests

### Basic Usage

Here's a simple example of querying a test case:

```graphql
query {
  testCase(id: "TC-123") {
    id
    summary
    description
    steps {
      action
      expectedResult
    }
  }
}
```

For more examples and detailed usage instructions, refer to the [Schema Documentation](schema.md#example-usage).

### Error Handling

The API uses standard GraphQL error formatting. See the [Schema Documentation - Error Handling](schema.md#error-handling) section for details on error types and handling strategies.

### Next Steps

1. Review the [Schema Documentation](schema.md) to understand available operations
2. Follow the [Best Practices](best_practices.md) for secure and efficient API usage
3. Explore example implementations in the source code

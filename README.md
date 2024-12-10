# Jira Xray GraphQL Integration Example

This repository serves as a comprehensive example and starting point for integrating with Jira Xray using GraphQL. It demonstrates best practices for test management automation through Xray's GraphQL API.

## Prerequisites

- Python 3.7+
- Jira Cloud account with Xray installed
- Xray API token

## Project Structure

```
.
├── README.md
├── requirements.txt
├── config/
│   └── .env.example
├── src/
│   ├── client.py        # XrayClient implementation
│   ├── models.py        # Data models
│   └── examples/
│       ├── basic_usage.py
│       └── advanced_usage.py
└── docs/
    ├── schema.md        # GraphQL schema documentation
    └── best_practices.md
```

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your Xray API credentials:
   ```bash
   cp config/.env.example config/.env
   ```

## Quick Start

1. Configure your environment variables in `config/.env`
2. Run the basic example:
   ```bash
   python src/examples/basic_usage.py
   ```

## Features

- Full GraphQL schema implementation for Xray test management
- Type-safe data models using Python dataclasses
- Comprehensive error handling
- Example implementations for common use cases:
  - Creating test cases
  - Managing test sets
  - Creating test plans
  - Recording test executions

## Best Practices

See [docs/best_practices.md](docs/best_practices.md) for detailed guidelines on:
- API token management
- Error handling
- Rate limiting
- Testing strategies
- Code organization

## GraphQL Schema

The complete GraphQL schema documentation is available in [docs/schema.md](docs/schema.md). This includes:
- All available queries and mutations
- Type definitions
- Example queries

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this code in your own projects.

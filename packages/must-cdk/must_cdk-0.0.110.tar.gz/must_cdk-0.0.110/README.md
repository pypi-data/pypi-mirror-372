# Must CDK

A collection of AWS CDK constructs that implement common architectural patterns and best practices for AWS services. This library aims to simplify the deployment of common cloud infrastructure patterns while maintaining security, scalability, and operational excellence.

## Getting Started

### TypeScript/JavaScript

```bash
npm install must-cdk
# or
yarn add must-cdk
```

### Python

```bash
pip install must-cdk
```

### CLI Tool

Install globally to quickly initialize Amplify projects:

```bash
# Install CLI globally
npm install -g must-cdk

# Initialize Amplify project with React template
must-cdk amplify init

# Initialize in specific directory
must-cdk amplify init -d /path/to/project
```

## Features

### 🏗️ Amplify Patterns

* Next.js application deployment optimizations
* Multi-environment branch configurations
* Custom domain and SSL setup
* GitHub personal access token authentication
* Automated build and deployment pipelines
* Migration path to GitHub Apps for production
* CLI tool for quick project initialization

### 🚢 ECS CodeDeploy Patterns

* Blue/Green deployment strategies
* Load balanced service deployments
* Auto-scaling configurations
* Health check implementations
* Environment variables support
* Secrets management integration
* Custom container names
* Enhanced container configuration
* Container access after creation

### 🌐 CloudFront Patterns

* API Gateway integrations
* Multi-origin configurations
* Cross-region setups
* Security headers and WAF integration
* Caching strategies
* Custom domain configurations

### 🔌 API Gateway Lambda Patterns

* REST API implementations
* WebSocket API setups
* Custom domain configurations
* Lambda authorizers
* Rate limiting and API key management

## 🏷️ Tags Management

Must CDK provides a unified tagging system that automatically applies tags to all resources across all constructs. This system supports both environment-based tags and construct-specific tags.

### Environment Tags

Set tags globally using the `TAGS` environment variable:

```bash
# Format: key1=value1,key2=value2
export TAGS="Product=MyApp,Owner=TeamName,Environment=production,CostCenter=engineering"

# Deploy with environment tags
cdk deploy
```

### Construct-Specific Tags

Add tags directly to individual constructs:

```python
// TypeScript
new AmplifyApp(this, 'MyApp', {
  appName: 'my-application',
  repository: 'https://github.com/user/repo',
  tags: {
    Team: 'frontend',
    Version: 'v1.0.0',
    Component: 'web-app'
  }
});
```

```python
# Python
AmplifyApp(self, 'MyApp',
  app_name='my-application',
  repository='https://github.com/user/repo',
  tags={
    'Team': 'frontend',
    'Version': 'v1.0.0',
    'Component': 'web-app'
  }
)
```

### Tag Precedence

Environment tags take precedence over construct-specific tags:

```bash
# Environment variable
export TAGS="Environment=production,Team=platform"

# In your code
tags: {
  Team: 'frontend',      # Will be overridden by environment
  Component: 'web-app'   # Will be preserved
}

# Final tags applied:
# Environment=production (from env)
# Team=platform (from env, overrides construct tag)
# Component=web-app (from construct)
```

## Documentation

Detailed documentation for each construct can be found in:

* [Python API Reference](./docs/python/api.md)
* [Tags Documentation](./docs/TAGS.md)
* [Examples](./examples/README.md)

## Examples

The [examples](./examples) directory contains working examples for each construct category:

* Amplify deployment patterns
* ECS with CodeDeploy configurations
* CloudFront distribution setups
* API Gateway with Lambda integrations

Each example is provided in both TypeScript and Python with detailed comments and instructions.

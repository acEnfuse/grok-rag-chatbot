# RAG Chatbot Test Suite

This document describes the comprehensive test suite for the RAG Chatbot application, designed to achieve 80%+ code coverage using modern testing best practices.

## Overview

The test suite includes:
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and workflows
- **Mocking**: Comprehensive mocking of external dependencies
- **Coverage Reporting**: Detailed coverage analysis with HTML reports
- **Async Testing**: Proper testing of async operations

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and shared fixtures
├── test_document_processor.py # DocumentProcessor unit tests
├── test_groq_service.py     # GroqService unit tests
├── test_milvus_service.py   # MilvusService unit tests
├── test_app_integration.py  # Streamlit app integration tests
└── test_utils.py            # Test utilities and helpers
```

## Quick Start

### 1. Install Testing Dependencies

```bash
# Install all dependencies including testing tools
make install-dev

# Or manually:
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov pytest-mock coverage
```

### 2. Run Tests

```bash
# Run all tests with coverage
make test-coverage

# Run tests quickly (no coverage)
make test-fast

# Run specific test files
make test-document-processor
make test-groq-service
make test-milvus-service
make test-app-integration
```

### 3. View Coverage Report

```bash
# Generate and open HTML coverage report
make coverage-html

# View coverage in terminal
make coverage-report
```

## Test Categories

### Unit Tests

Test individual components in isolation using mocks for external dependencies.

**DocumentProcessor Tests** (`test_document_processor.py`):
- PDF text extraction with Tika
- Text chunking with word boundary preservation
- Error handling for malformed documents
- Unicode character handling
- Custom chunk size and overlap configuration

**GroqService Tests** (`test_groq_service.py`):
- Async response generation
- Chat history management
- Context document formatting
- Error handling and retries
- Summary generation with fallbacks

**MilvusService Tests** (`test_milvus_service.py`):
- Vector database operations
- Embedding generation and storage
- Document search and retrieval
- Collection management
- Lazy loading of embedding models

### Integration Tests

Test component interactions and end-to-end workflows.

**App Integration Tests** (`test_app_integration.py`):
- Streamlit UI initialization
- Document upload workflow
- Chat functionality
- Error handling across components
- Session state management
- CSS styling application

## Testing Features

### Comprehensive Mocking

The test suite uses extensive mocking to isolate components:

```python
# Example: Mocking external services
@pytest.fixture
def mock_services():
    return {
        'milvus': Mock(),
        'groq': AsyncMock(), 
        'processor': Mock()
    }
```

### Async Testing

Proper testing of async operations using `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_generate_response(groq_service):
    result = await groq_service.generate_response("test query", [])
    assert result is not None
```

### Fixtures and Test Data

Reusable test data and setup:

```python
@pytest.fixture
def sample_document_chunks():
    return [
        {
            "text": "Sample text",
            "chunk_index": 0,
            "filename": "test.pdf"
        }
    ]
```

### Environment Isolation

Tests run in isolated environments with test-specific configuration:

```python
TEST_ENV_VARS = {
    "GROQ_API_KEY": "test_groq_api_key",
    "MILVUS_HOST": "localhost:19530",
    "MILVUS_TOKEN": "test_token",
    "MILVUS_COLLECTION_PREFIX": "test_"
}
```

## Coverage Goals

The test suite targets **80% code coverage** across all components:

- **backend/services/**: 85%+ coverage
- **app.py**: 75%+ coverage (Streamlit UI challenges)
- **Overall**: 80%+ coverage

### Coverage Reports

HTML coverage reports provide detailed line-by-line analysis:

```bash
# Generate detailed HTML report
make coverage-html
# Opens htmlcov/index.html in browser
```

Terminal coverage summary:

```bash
make coverage-report
# Shows coverage percentages and missing lines
```

## Test Commands

### Basic Testing

```bash
make test              # Run all tests
make test-fast         # Quick test run (no coverage)
make test-coverage     # Tests with coverage report
```

### Targeted Testing

```bash
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-debug        # Verbose output with full tracebacks
make test-failed       # Re-run only failed tests
```

### Development Workflow

```bash
make dev              # Quick development cycle (clean + fast test)
make ci               # Full CI simulation (clean + install + coverage)
```

## Best Practices

### Writing Tests

1. **Use Descriptive Names**: Test names should clearly describe what is being tested
2. **Follow AAA Pattern**: Arrange, Act, Assert
3. **Mock External Dependencies**: Use mocks for APIs, databases, file systems
4. **Test Edge Cases**: Empty inputs, error conditions, boundary values
5. **Keep Tests Independent**: Each test should be able to run in isolation

### Example Test Structure

```python
def test_process_document_success(self, processor, mock_tika_parser):
    """Test successful document processing."""
    # Arrange
    mock_tika_parser.return_value = {'content': 'Test content'}
    pdf_bytes = b"fake pdf content"
    
    # Act
    result = processor.process_document(pdf_bytes, "test.pdf")
    
    # Assert
    assert len(result) > 0
    assert all('text' in chunk for chunk in result)
```

### Async Testing

```python
@pytest.mark.asyncio
async def test_async_operation(service):
    """Test async operations properly."""
    result = await service.async_method()
    assert result is not None
```

### Mocking Guidelines

```python
# Mock external APIs
with patch('external_api.call') as mock_api:
    mock_api.return_value = {'status': 'success'}
    
# Mock file operations
with patch('builtins.open', mock_open(read_data='test')):
    result = function_that_reads_file()
```

## Continuous Integration

The test suite is designed for CI/CD integration:

```bash
# CI pipeline simulation
make ci

# This runs:
# 1. Clean environment
# 2. Install dependencies
# 3. Run tests with coverage
# 4. Generate reports
# 5. Fail if coverage < 80%
```

## Troubleshooting

### Common Issues

**Import Errors**: 
```bash
# Ensure you're in the project root and dependencies are installed
make install-dev
```

**Async Test Failures**:
```bash
# Make sure pytest-asyncio is installed
pip install pytest-asyncio
```

**Coverage Too Low**:
```bash
# Run with detailed coverage to see missing lines
make coverage-html
# Open htmlcov/index.html to see exactly what's not covered
```

### Debug Mode

```bash
# Run tests with maximum verbosity
make test-debug

# Run specific test with debugging
pytest tests/test_specific.py::test_function -v -s --tb=long
```

## Performance Testing

The test suite includes performance considerations:

```python
def test_large_document_processing():
    """Test processing of large documents."""
    large_text = "content " * 10000
    chunks = processor.chunk_text(large_text, "large.pdf")
    assert len(chunks) > 10
```

## Security Testing

Tests include security considerations:

```python
def test_environment_variable_isolation():
    """Ensure test environment doesn't leak to production."""
    assert os.getenv('GROQ_API_KEY') == 'test_groq_api_key'
```

## Contributing

When adding new features:

1. **Write Tests First**: Follow TDD when possible
2. **Maintain Coverage**: Ensure new code has adequate test coverage
3. **Update Documentation**: Update this README if adding new test patterns
4. **Run Full Suite**: Always run `make test-coverage` before committing

## Test Metrics

Current test metrics (target goals):

- **Total Tests**: 50+ tests
- **Coverage**: 80%+ overall
- **Test Types**: 
  - Unit Tests: 35+
  - Integration Tests: 15+
- **Components Covered**:
  - DocumentProcessor: 100%
  - GroqService: 95%
  - MilvusService: 90%
  - App Integration: 70%

Run `make test-coverage` to see current actual metrics. 
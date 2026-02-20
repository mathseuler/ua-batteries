# Tests for ua_batteries

This directory contains unit and integration tests for the ua_batteries project.

## Test Structure

```
tests/
├── __init__.py                 # Package marker
├── conftest.py                 # Pytest configuration and fixtures
├── test_main.py               # Tests for optimization functions
├── test_get_file.py           # Tests for data download functions
├── test_total_price.py        # Tests for pricing functions
└── test_visualization.py      # Tests for visualization functions
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests for a specific module
```bash
pytest tests/test_main.py
pytest tests/test_visualization.py
```

### Run tests with verbose output
```bash
pytest -v
```

### Run tests with coverage report
```bash
pip install pytest-cov
pytest --cov=ua_batteries
```

### Run a specific test class
```bash
pytest tests/test_main.py::TestOptimizeDayDP
```

### Run a specific test function
```bash
pytest tests/test_main.py::TestOptimizeDayDP::test_simple_case_low_high_prices
```

## Test Categories

### test_main.py
Tests for the core optimization algorithms:
- `TestOptimizeDayDP`: Dynamic programming optimization tests
- `TestOptimizeDayLP`: Linear programming optimization tests
- `TestAddOptimizationToDf`: Dataframe integration tests

Key tests:
- Capacity constraints
- Power limitations
- End-of-day zero capacity requirement
- Max buy/sell transactions
- Profit calculations

### test_get_file.py
Tests for data downloading and parsing:
- `TestDownloadFile`: File download tests
- `TestGetFile`: Data retrieval tests

Key tests:
- HTTP request handling
- HTML parsing
- Error handling for failed requests
- DataFrame structure validation

### test_total_price.py
Tests for pricing functions:
- `TestTotalBuyPrice`: Buy price calculation tests
- `TestTotalSellPrice`: Sell price calculation tests
- `TestBuySellPriceFunctions`: Combined pricing tests

Key tests:
- Positive prices
- Zero prices
- Decimal precision
- Multiple price values

### test_visualization.py
Tests for visualization and HTML generation:
- `TestCreateOptimizationVisualization`: Visualization dataframe tests
- `TestExportToHTML`: HTML file generation tests
- `TestDisplayVisualization`: Display wrapper tests

Key tests:
- HTML file creation
- Content validation
- Buy/sell hour marking
- Styling integration

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `sample_prices`: List of 24 hourly prices
- `sample_dataframe`: DataFrame with 24 hours of prices for 3 days
- `optimized_sample_dataframe`: DataFrame with optimization columns
- `mock_html_response`: Mock HTML response from data source

## Writing New Tests

When adding new tests:

1. Place them in the appropriate `test_*.py` file
2. Use the existing fixtures from `conftest.py`
3. Follow the naming convention: `test_<function_name>_<what_is_tested>`
4. Add docstrings explaining what the test validates
5. Use `@patch` decorators for external dependencies

Example:
```python
def test_exports_to_csv(self):
    """Test that DataFrames are exported to CSV format"""
    df = pd.DataFrame({'A': [1, 2, 3]})
    
    # Test assertion
    assert df is not None
```

## Continuous Integration

These tests can be integrated into CI/CD pipelines. Configure your CI tool to run:
```bash
pytest --cov=ua_batteries --cov-report=html
```

## Dependencies

Test dependencies are included in the project:
- `pytest` - Testing framework
- `pandas` - Data manipulation
- `mock` - Mocking library (built into unittest for Python 3)
- `requests` - HTTP library (for integration tests)

To install test dependencies:
```bash
pip install pytest pytest-cov
```

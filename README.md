# Energy Ukraine Battery Optimization

Optimize energy trading strategy for Ukrainian battery storage systems using dynamic programming and linear programming algorithms.

## Setup

```bash
pip install -r requirements.txt
```

## Run Tests

```bash
pytest
```

## Usage

```python
from ua_batteries.utils.get_file import get_file
from ua_batteries.visualization import display_visualization

df = get_file(month_year="02.2026")
viz = display_visualization(df, method="dp", max_buys=3, max_sells=3)
```

## Development

```bash
pip install -r requirements-dev.txt
flake8 src tests
pytest
```

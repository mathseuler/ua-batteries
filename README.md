# Energy Ukraine Battery Optimization

Optimize energy trading strategy for Ukrainian battery storage systems using dynamic programming and linear programming algorithms.

---

## Complete Setup Guide (For Beginners)

Follow these steps to set up and run the project from scratch, even if you don't have Python installed.

### Step 1: Install Python

1. Go to https://www.python.org/downloads/
2. Download **Python 3.11** (or newer)
3. Run the installer
4. **IMPORTANT:** Check the box "Add Python to PATH" during installation
5. Click "Install Now"
6. Verify installation by opening Command Prompt and typing:
   ```bash
   python --version
   ```

### Step 2: Install VS Code

1. Go to https://code.visualstudio.com/
2. Download and run the installer
3. Open VS Code after installation

### Step 3: Clone the Project

1. Open Command Prompt
2. Navigate to where you want to store the project (e.g., `C:\Users\YourName\Projects`)
3. Clone the repository:
   ```bash
   git clone https://github.com/mathseuler/ua-batteries
   cd ua-batteries
   ```

### Step 4: Open in VS Code

1. In Command Prompt (still in the `ua-batteries` folder), type:
   ```bash
   code .
   ```
   This opens the project in VS Code

### Step 5: Create Virtual Environment

1. In VS Code, open the Terminal (Ctrl + `)
2. Run:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     source .venv/bin/activate
     ```

You should see `(.venv)` at the start of your terminal prompt.

### Step 6: Install Dependencies

In the terminal, run:
```bash
pip install -r requirements.txt
```

### Step 7: Set Environment Variables (Windows)

These variables control the optimization parameters. Open Command Prompt and set them:

```bash
set MAX_BUYS=3
set MAX_SELLS=3
set CAPACITY=200
set POWER=100
```

**Explanation:**
- `MAX_BUYS`: Maximum number of times to buy per day (default: 10)
- `MAX_SELLS`: Maximum number of times to sell per day (default: 10)
- `CAPACITY`: Battery storage capacity in MWh (default: 1000)
- `POWER`: Max power to buy/sell per hour in MWh (default: 500)

**For Mac/Linux**, use `export` instead:
```bash
export MAX_BUYS=3
export MAX_SELLS=3
export CAPACITY=200
export POWER=100
```

### Step 8: Run the Visualization

In the terminal (with venv activated and env vars set), run:

```bash
python -m ua_batteries.visualization
```

This will:
1. Download the latest energy prices
2. Run the optimization algorithm
3. Generate an HTML visualization
4. Open it in your default browser

### Troubleshooting

**"python: command not found"**
- Make sure Python is added to PATH (reinstall if needed, check "Add Python to PATH")

**"No module named ua_batteries"**
- Verify virtual environment is activated (you should see `(.venv)` prefix)
- Run `pip install -r requirements.txt` again

**"ModuleNotFoundError: No module named 'requests'"**
- Virtual environment not activated. Run `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Mac/Linux)

---

## For Developers

### Run Tests

```bash
pytest
```

### Check Code Quality

```bash
flake8 ua_batteries tests
```

### Format Code

```bash
black ua_batteries tests
```

### Install Development Tools

```bash
pip install -r requirements-dev.txt
```


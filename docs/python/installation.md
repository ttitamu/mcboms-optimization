# Installation

## Prerequisites

- **Python 3.11 or higher**. Check with `python --version` or `python3 --version`. Download from [python.org](https://www.python.org/downloads/) if needed. On Windows, **check the box "Add Python to PATH"** during installation.
- **A MILP solver**. The framework supports two backends:
    - **CBC** (open-source, bundled with PuLP) — works out of the box, slower for large problems
    - **Gurobi** (commercial, free academic license) — faster, used in the validation runs

## Setup

### Linux / macOS

```bash
git clone https://github.com/sa-ameen/mcboms-optimization.git
cd mcboms-optimization
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Windows (PowerShell or Git Bash)

```powershell
git clone https://github.com/sa-ameen/mcboms-optimization.git
cd mcboms-optimization
python -m venv venv
venv\Scripts\activate
pip install -e .
```

That installs the `mcboms` package and all Python dependencies (pandas, numpy, pulp, pytest, openpyxl).

## Optional: Gurobi installation

If you want to use Gurobi instead of CBC:

1. Get a license at [gurobi.com/academia/](https://www.gurobi.com/academia/) (academic, free) or [gurobi.com/solutions/licensing/](https://www.gurobi.com/solutions/licensing/) (commercial)
2. Install Gurobi following their installer
3. Activate the license: `grbgetkey YOUR-LICENSE-KEY`
4. Install the Python interface: `pip install gurobipy`

Without Gurobi, the framework falls back to CBC automatically.

## Verifying the installation

Run the test suite. All 32 tests should pass:

```bash
pytest tests/ -q
```

Expected output:

```
............................
32 passed in 2 seconds
```

If any tests fail, see [Troubleshooting](../reference/troubleshooting.md).

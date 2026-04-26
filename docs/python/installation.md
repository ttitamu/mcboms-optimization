# Installation

There are two paths: install locally on your own machine, or run the example
notebooks on Google Colab without installing anything.

## Run on Google Colab (no install)

The repository ships with two ready-to-run notebooks. Each one installs the
framework with PuLP+CBC (no license required) and reproduces a validation
case end-to-end. Click either badge to open in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg) Worked example](https://colab.research.google.com/github/ttitamu/mcboms-optimization/blob/main/notebooks/01_worked_example.ipynb){ .md-button .md-button--primary }
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg) Harwood case study](https://colab.research.google.com/github/ttitamu/mcboms-optimization/blob/main/notebooks/02_harwood_50m.ipynb){ .md-button }

The first cell of each notebook installs MCBOMs from this repository. Allow
about 30 seconds for the install to complete, then run the remaining cells.

## Install locally

### Prerequisites

- **Python 3.11 or higher.** Check with `python --version`. Download from
  [python.org](https://www.python.org/downloads/) if needed. On Windows, tick
  "Add Python to PATH" during installation.
- **A MILP solver.** Two backends are supported:
    - **PuLP + CBC** (open-source) — works out of the box, no license required
    - **Gurobi** (commercial) — faster on large problems; free academic license available

The optimizer auto-detects which solver is installed. You can also pass
`solver="gurobi"` or `solver="pulp"` to `Optimizer.solve()` to force a choice.

### Linux / macOS

```bash
git clone https://github.com/ttitamu/mcboms-optimization.git
cd mcboms-optimization
python -m venv venv
source venv/bin/activate
pip install -e ".[pulp]"          # PuLP+CBC backend
# or
pip install -e ".[gurobi]"        # Gurobi backend (license required)
# or
pip install -e ".[pulp,gurobi]"   # Both, auto-detects at runtime
```

### Windows (PowerShell or Git Bash)

```powershell
git clone https://github.com/ttitamu/mcboms-optimization.git
cd mcboms-optimization
python -m venv venv
venv\Scripts\activate
pip install -e ".[pulp]"
```

The base install pulls in pandas, numpy, and the other runtime dependencies.
The `[pulp]` extra adds PuLP; `[gurobi]` adds gurobipy.

## Gurobi license

Gurobi requires a license to solve anything beyond very small instances.

1. Get a license at [gurobi.com/academia/](https://www.gurobi.com/academia/)
   (free for academic use) or
   [gurobi.com/solutions/licensing/](https://www.gurobi.com/solutions/licensing/)
   (commercial).
2. Install Gurobi using their installer.
3. Activate: `grbgetkey YOUR-LICENSE-KEY`.
4. `pip install -e ".[gurobi]"` in your environment.

Without Gurobi, MCBOMs falls back to PuLP+CBC automatically.

## Verifying the installation

```bash
pytest tests/ -q
```

All 109 tests should pass. If any fail, see
[Troubleshooting](../reference/troubleshooting.md).

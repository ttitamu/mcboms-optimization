# MCBOMs Setup and Run Instructions

## Step-by-Step Guide

### Prerequisites

1. **Python 3.11 or higher**
   - Check: `python --version` or `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **Gurobi Optimizer** (required for MILP)
   - Academic license (FREE): https://www.gurobi.com/academia/academic-program-and-licenses/
   - After registering, download and install Gurobi
   - Run `grbgetkey YOUR-LICENSE-KEY` to activate

---

### Setup (One Time)

#### Option A: Using Virtual Environment (Recommended)

Open terminal/command prompt in the `mcboms-optimization` folder:

**Windows:**
```cmd
cd mcboms-optimization
python -m venv venv
venv\Scripts\activate
pip install -e .
```

**Mac/Linux:**
```bash
cd mcboms-optimization
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

#### Option B: Direct Install (Simpler)

```bash
cd mcboms-optimization
pip install -e .
```

---

### Running the Validation

After setup, from the `mcboms-optimization` folder:

**Windows:**
```cmd
python run_harwood_validation.py
```

**Mac/Linux:**
```bash
python3 run_harwood_validation.py
```

---

### Expected Output

If everything works, you should see:

```
======================================================================
MCBOMs HARWOOD (2003) VALIDATION
======================================================================
Validating optimizer against benchmark results from:
  Harwood et al. (2003). Systemwide optimization of safety
  improvements for resurfacing, restoration, or rehabilitation
  (RRR) projects. TRR 1840, pp. 148-157.

----------------------------------------------------------------------
STEP 1: Loading Data
----------------------------------------------------------------------
  Sites loaded: 10
  Alternatives loaded: 27
  Alternatives per site: 2.7 avg

----------------------------------------------------------------------
STEP 2: Optimization - $50M Budget (Unconstrained)
----------------------------------------------------------------------
  Status: optimal
  Solve time: 0.XXX seconds

  COMPARISON ($50M Budget):
  ------------------------------------------------------------------
  Metric                           Expected        Actual     Diff  OK?
  ------------------------------------------------------------------
  Total Cost                     $16,271,246   $16,271,246   +0.0%  ✓
  Total Benefit                  $10,640,914   $10,640,914   +0.0%  ✓
  Net Benefit                     $6,159,517    $6,159,517   +0.0%  ✓

... [more output] ...

======================================================================
VALIDATION SUMMARY
======================================================================
  Level 2a (rigorous) result: 4/4 checks passed

  ╔════════════════════════════════════════════════════════════════╗
  ║  ✓ VALIDATION SUCCESSFUL                                       ║
  ║    MCBOMs reproduces Harwood (2003) $50M published results.    ║
  ║    $10M divergence is documented methodological choice per     ║
  ║    formulation spec Section 7.3.                               ║
  ╚════════════════════════════════════════════════════════════════╝
```

---

### Troubleshooting

#### "ModuleNotFoundError: No module named 'mcboms'"

You haven't installed the package. Run:
```bash
pip install -e .
```

#### "ModuleNotFoundError: No module named 'gurobipy'"

Gurobi is not installed. Either:
1. Install Gurobi from https://www.gurobi.com/downloads/
2. Or install via pip (may require license): `pip install gurobipy`

#### "GurobiError: No Gurobi license found"

You need to activate your Gurobi license:
1. Get a license from https://www.gurobi.com/academia/
2. Run: `grbgetkey YOUR-LICENSE-KEY`

#### "Import error" or "Syntax error"

Make sure you're using Python 3.11+:
```bash
python --version
```

---

### Project Structure

```
mcboms-optimization/
├── run_harwood_validation.py   <-- RUN THIS
├── src/
│   └── mcboms/
│       ├── core/
│       │   └── optimizer.py    # MILP optimization
│       ├── data/
│       │   └── harwood_alternatives.py  # Pre-calculated data
│       ├── io/
│       │   └── readers.py      # Data loading
│       └── utils/
│           └── economics.py    # NPV calculations
├── tests/
├── requirements.txt
└── pyproject.toml
```

---

### Next Steps After Validation

Once validation passes:

1. **Implement full benefit calculations** (safety CMFs, operational benefits)
2. **Run MCBOMs methodology** on Harwood data with enhanced alternatives
3. **Compare results** - do we find better solutions with partial-length?

---

### Questions?

Contact: Texas A&M Transportation Institute

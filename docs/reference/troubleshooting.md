# Troubleshooting

## Solver-language model issues

### LP file does not solve in CPLEX/Gurobi

The LP files have been validated by solving with CBC. If your solver rejects them, check:

- Solver version (CPLEX 12.10+ and Gurobi 9+ should both work)
- File path (LP format is sensitive to leading/trailing whitespace in line continuations)
- File encoding (must be ASCII or UTF-8)

### AMPL or GAMS reports "set is empty" warnings

The optimization model includes optional and network-level constraints that are activated only when the corresponding sets are populated in the data file. When the validation instances do not exercise these constraints, AMPL or GAMS may emit warnings; the warnings are expected and the solution remains optimal.

### Solver reports "infeasible" for an intersection sub-problem

The Banihashemi intersection notebook uses a budget of $1.3M, which is enough to accommodate the published improvements. If you tightened the budget below this and the solver reports infeasibility, increase the budget to at least the cost of the cheapest selectable alternative.

## Python-side issues

### "ModuleNotFoundError: No module named 'mcboms'"

You did not run `pip install -e .` from the repo root. Do that, then try again. If the error persists, your `pip` is pointing to a different Python than `python` is — use `python -m pip install -e .` instead.

### "ModuleNotFoundError: No module named 'gurobipy'"

You do not have Gurobi installed. The framework falls back to CBC automatically. If you still see this error, the fallback is not triggering — check that `pulp` is installed (`pip install pulp`).

### "GUROBI license expired" or "GRBgetkey error"

Your Gurobi license expired or was never activated. Either renew the academic license or skip Gurobi (the framework will use CBC).

### Tests fail on Windows with path errors

Some Windows shells handle path separators differently. Use Git Bash or WSL instead of cmd.exe. If you must use cmd.exe, replace forward slashes with backslashes in commands.

### `python run_harwood_validation.py` prints validation results but no green banner

The Level 2a check failed. Run `pytest tests/test_harwood_validation.py -v` to see which specific test failed and what the difference is. Most likely cause: someone modified `economics.py` to use non-Harwood unit costs, breaking the reproduction.

### "Python was not found" or "command not found: python"

Windows ships with a Microsoft Store stub at the `python` path that is not real Python. Install actual Python from [python.org](https://www.python.org/downloads/) and check the "Add Python to PATH" box during installation. Open a new terminal after installation.

## Excel workbook issues

### Solver does not appear on the Data tab

Enable the Solver add-in: File → Options → Add-ins → Manage Excel Add-ins → Go, then check Solver Add-in. The same path works on Excel for Windows. On Excel for Mac, the menu is Tools → Excel Add-ins.

### Excel for the web or Excel for Mac does not have Solver

Solver is a desktop-only feature on Windows and Mac. The web and mobile versions of Excel do not include it. Open the workbook in desktop Excel to run the optimization.

### Solver reports "Solver could not find a feasible solution"

The constraints are inconsistent with the inputs. The most common cause is that the budget cell was changed below the cost of any selectable combination. Reset the budget to the value documented on the Optimization sheet's setup panel.

### Solver runs but the Results sheet shows FAIL

The match indicator on the Results sheet compares the Solver output against the published optimal value. If it shows FAIL, the Solver may have used the GRG Nonlinear or Evolutionary engines instead of Simplex LP. In the Solver dialog, check that "Solving Method" is set to "Simplex LP" before clicking Solve.

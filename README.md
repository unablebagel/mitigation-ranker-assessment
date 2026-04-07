# Assessment

Ranks security mitigations by risk score. The bonus version extends this with cost-aware greedy selection.

## Files

| File | Input | Description |
|------|-------|-------------|
| [draft.py](draft.py) | `input.json` | Ranks mitigations by risk score |
| [bonus.py](bonus.py) | `input-bonus.json` | Ranks mitigations and greedily selects within a time budget |

---

## Risk Scoring (both scripts)

Each threat is scored using:

```
risk_score = impact × likelihood × log(priority)
```

A mitigation's score is the sum of risk scores from every threat it addresses. Mitigations are then ranked highest-to-lowest.

`log` dampens the effect of priority so that very high priority values (which has no upper limit) don't dominate the score disproportionately.

---

## Greedy Selection Algorithm (bonus.py only)

`greedy_select(budget, N)` iterates through the ranked mitigations and picks each one if its `time_cost` fits within the remaining budget. Stops when `N` mitigations have been selected or the budget is exhausted.

Adjust the `budget` and `N` arguments in the `greedy_select` call at the bottom of [bonus.py](bonus.py) to explore different scenarios.

---
## Usage

```python
py draft.py
py bonus.py
```

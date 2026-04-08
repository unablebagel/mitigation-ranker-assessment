# Assessment

Ranks security mitigations by risk score. Bonus extensions add cost-aware ranking and greedy budget selection.

## Files

| File | Input | Description |
|------|-------|-------------|
| [core.py](core.py) | `input-core.json` | Ranks mitigations by accumulated risk score |
| [bonus-1.py](bonus-1.py) | `input-bonus1.json` | Re-ranks mitigations by risk score per unit cost |
| [bonus-2.py](bonus-2.py) | `input-bonus2.json` | Ranks mitigations and greedily selects within a time budget |
| [test_cases.py](test_cases.py) | — | 7 property-based tests using Hypothesis |

---

## Risk Scoring

Each threat is scored using:

```
risk_score = impact × likelihood × log(priority)
```

A mitigation's score is the sum of risk scores from every threat it addresses. Mitigations are then ranked highest-to-lowest.

`log` dampens the effect of priority so that very high priority values (which have no upper limit) don't dominate the score disproportionately.

---

## Bonus 1 — Cost-Adjusted Ranking

Mitigations are re-ranked by:

```
adjusted_score = risk_score / cost
```

This surfaces mitigations that deliver the most risk reduction per unit of cost, even if their raw score is lower than others.

---

## Bonus 2 — Greedy Budget Selection

`greedy_select(budget, N)` iterates through the ranked mitigations and picks each one if its `time_cost` fits within the remaining budget. Stops when `N` mitigations have been selected or the budget is exhausted.

Adjust the `budget` and `N` arguments in the `greedy_select` call at the bottom of [bonus-2.py](bonus-2.py) to explore different scenarios.

---

## Assumptions

### Input data
- Every mitigation ID referenced inside a threat's `mitigations` list exists in the top-level `mitigations` list.
- `impact` and `likelihood` are positive numbers.

### Priority
- `priority` is always **≥ 1**
- There is no upper bound on `priority`

### Mitigation effectiveness
- Each mitigation is assumed to **fully mitigate** every threat it is linked to — no partial credit.
- All mitigations linked to the same threat are treated as **equally effective**; no weighting between them is applied.
- Because each mitigation is counted independently, the scores are additive across threats but do not account for overlapping coverage between multiple mitigations applied to the same threat simultaneously.

### Cost fields
- **`cost` (Bonus 1):** Must be a positive, non-zero number. Division by zero is not handled.
- **`time_cost` (Bonus 2):** Defaults to `1` if the field is absent from a mitigation entry.

### Ranking
- Mitigations are ranked in **descending** order (highest score first).
- Ties in score are not broken by any secondary criterion; their relative order among tied entries is undefined.

---

## Usage

```
python core.py
python bonus-1.py
python bonus-2.py
python -m unittest test_cases -v
```

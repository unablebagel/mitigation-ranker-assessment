"""
Test Cases for Assessment — Mitigation Risk Ranking
============================================================
All tests use Hypothesis property-based testing.
Hypothesis generates hundreds of random inputs per test automatically.

H01  priority >= 1 always produces a non-negative risk score
H02  Shared mitigation always outscores a non-shared one (same threat pool)
H03  Ranking output is always in descending order
H04  Bonus 1: adjusted_score = score / cost for all inputs
H05  Bonus 2: missing time_cost always defaults to 1
H06  Greedy: selected total time_cost never exceeds budget
H07  Greedy: result length never exceeds N
"""

import math
import unittest
from hypothesis import given, assume, strategies as st


# ── Pure logic (mirrors source files, no I/O) ──────────────────────────────

def risk_score(threat):
    return threat["impact"] * threat["likelihood"] * math.log(threat["priority"])


def rank_mitigations_core(threats_list, mitigations_list):
    threats = {t["id"]: t for t in threats_list}
    mitigations = {m["id"]: {"score": 0} for m in mitigations_list}
    for threat in threats.values():
        score = risk_score(threat)
        for mid in threat["mitigations"]:
            mitigations[mid]["score"] += score
    return sorted(mitigations.items(), key=lambda x: x[1]["score"], reverse=True)


def rank_mitigations_bonus1(threats_list, mitigations_list):
    threats = {t["id"]: t for t in threats_list}
    mitigations = {m["id"]: {"score": 0, "cost": m["cost"]} for m in mitigations_list}
    for threat in threats.values():
        score = risk_score(threat)
        for mid in threat["mitigations"]:
            mitigations[mid]["score"] += score
    for attrs in mitigations.values():
        attrs["adjusted_score"] = attrs["score"] / attrs["cost"]
    return sorted(mitigations.items(), key=lambda x: x[1]["adjusted_score"], reverse=True)


def rank_mitigations_bonus2(threats_list, mitigations_list):
    threats = {t["id"]: t for t in threats_list}
    mitigations = {
        m["id"]: {"score": 0, "time_cost": m.get("time_cost", 1)}
        for m in mitigations_list
    }
    for threat in threats.values():
        score = risk_score(threat)
        for mid in threat["mitigations"]:
            mitigations[mid]["score"] += score
    return sorted(mitigations.items(), key=lambda x: x[1]["score"], reverse=True)


def greedy_select(sorted_mitigations, budget, N):
    selected = []
    remaining_budget = budget
    for mid, attrs in sorted_mitigations:
        if len(selected) >= N:
            break
        if attrs["time_cost"] <= remaining_budget:
            selected.append(mid)
            remaining_budget -= attrs["time_cost"]
    return selected


# ── Reusable strategies ────────────────────────────────────────────────────

positive_float = st.floats(min_value=0.1, max_value=1e4, allow_nan=False, allow_infinity=False)
priority_float = st.floats(min_value=1.0, max_value=1e4, allow_nan=False, allow_infinity=False)
positive_int   = st.integers(min_value=1, max_value=100)


# ── Tests ──────────────────────────────────────────────────────────────────

class TestHypothesisRiskScore(unittest.TestCase):

    @given(priority_float, positive_float, positive_float)
    def test_H01_score_non_negative(self, priority, impact, likelihood):
        """H01: priority >= 1 always produces a non-negative risk score."""
        threat = {"priority": priority, "impact": impact, "likelihood": likelihood}
        self.assertGreaterEqual(risk_score(threat), 0)


class TestHypothesisRanking(unittest.TestCase):

    @given(priority_float, positive_float, positive_float, positive_float)
    def test_H02_shared_mitigation_outscores_exclusive(self, priority, impact, l1, l2):
        """H02: m1 covers two threats, m2 covers one — m1 always ranks first."""
        threats = [
            {"id": "T1", "priority": priority, "impact": impact, "likelihood": l1,
             "mitigations": ["m1", "m2"]},
            {"id": "T2", "priority": priority, "impact": impact, "likelihood": l2,
             "mitigations": ["m1"]},
        ]
        mitigations = [{"id": "m1"}, {"id": "m2"}]
        result = rank_mitigations_core(threats, mitigations)
        self.assertEqual(result[0][0], "m1")

    @given(st.lists(priority_float, min_size=1, max_size=10))
    def test_H03_ranking_always_descending(self, priorities):
        """H03: Output is descending for any combination of threat priorities."""
        threats = [
            {"id": f"T{i}", "priority": p, "impact": 2, "likelihood": 3,
             "mitigations": [f"m{i}"]}
            for i, p in enumerate(priorities)
        ]
        mitigations = [{"id": f"m{i}"} for i in range(len(priorities))]
        result = rank_mitigations_core(threats, mitigations)
        scores = [attrs["score"] for _, attrs in result]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestHypothesisBonus1(unittest.TestCase):

    @given(priority_float, positive_float, positive_float, positive_float)
    def test_H04_adjusted_score_formula(self, priority, impact, likelihood, cost):
        """H04: adjusted_score always equals raw score / cost."""
        threats = [{"id": "T1", "priority": priority, "impact": impact,
                    "likelihood": likelihood, "mitigations": ["m1"]}]
        mitigations = [{"id": "m1", "cost": cost}]
        result = rank_mitigations_bonus1(threats, mitigations)
        expected = risk_score(threats[0]) / cost
        self.assertAlmostEqual(result[0][1]["adjusted_score"], expected, places=5)


class TestHypothesisBonus2(unittest.TestCase):

    @given(st.just({"id": "m1"}))
    def test_H05_missing_time_cost_defaults_to_1(self, mitigation):
        """H05: A mitigation entry with no time_cost key always gets time_cost=1."""
        threats = [{"id": "T1", "priority": 5.0, "impact": 2, "likelihood": 3,
                    "mitigations": ["m1"]}]
        result = rank_mitigations_bonus2(threats, [mitigation])
        self.assertEqual(result[0][1]["time_cost"], 1)

    @given(
        st.lists(st.tuples(positive_int, positive_int), min_size=1, max_size=20),
        st.integers(min_value=0, max_value=50),
        st.integers(min_value=0, max_value=10),
    )
    def test_H06_greedy_never_exceeds_budget(self, mits, budget, N):
        """H06: Total time_cost of selected mitigations never exceeds budget."""
        sorted_mits = [(f"m{i}", {"score": s, "time_cost": c})
                       for i, (s, c) in enumerate(mits)]
        result = greedy_select(sorted_mits, budget=budget, N=N)
        lookup = dict(sorted_mits)
        self.assertLessEqual(sum(lookup[m]["time_cost"] for m in result), budget)

    @given(
        st.lists(st.tuples(positive_int, positive_int), min_size=1, max_size=20),
        st.integers(min_value=0, max_value=50),
        st.integers(min_value=0, max_value=10),
    )
    def test_H07_greedy_never_exceeds_n(self, mits, budget, N):
        """H07: Result length never exceeds N.
        - if N=2 and the budget is 9999, it should still only pick at most 2 mitigations"""
        sorted_mits = [(f"m{i}", {"score": s, "time_cost": c})
                       for i, (s, c) in enumerate(mits)]
        result = greedy_select(sorted_mits, budget=budget, N=N)
        self.assertLessEqual(len(result), N)


if __name__ == "__main__":
    unittest.main(verbosity=2)

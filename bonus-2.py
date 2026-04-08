import json
import math 

with open('input-bonus2.json', 'r') as file:
    data = json.load(file)

# print(data)

threats = {} # this will be a dict of dict
mitigations = {}

# print(data["threats"]) # list of dictionary from json input


# print(data["mitigations"]) # list of dictionary from json input
# print("\n")

# get the key
# print(data["threats"][0]["id"]) 

# iterate over the list (of dict)
# for i in data["threats"]:
    # print(i)
    # extract the id to use as key
    # print(i["id"])

# take id as key, subsequent values within a dict

threats = {t["id"]: t for t in data["threats"]}
mitigations = {m["id"]: {"score": 0, "time_cost": m["time_cost"]} for m in data["mitigations"]}

def risk_score(threat):
    return threat["impact"] * threat["likelihood"] * math.log(threat["priority"])

for threat in threats.values():
    score = risk_score(threat)
    for mid in threat["mitigations"]:
        mitigations[mid]["score"] += score


# print(threats)
# print(mitigations)

sorted_mitigations = sorted(mitigations.items(), key=lambda x: x[1]["score"], reverse=True)

# print(sorted_mitigations)
print(f"{'ID':<6} {'Score':>10} {'Time Cost':>10}")
print("-" * 28)
for m in sorted_mitigations:
    print(f"{m[0]:<6} {m[1]['score']:>10.3f} {m[1]['time_cost']:>10}")


def greedy_select(budget, N):
    """Greedily pick mitigations by score until budget is exhausted or N mitigations selected."""
    selected = []
    remaining_budget = budget

    for mid, attrs in sorted_mitigations:
        if len(selected) >= N:
            break
        if attrs["time_cost"] <= remaining_budget:
            selected.append(mid)
            remaining_budget -= attrs["time_cost"]

    return selected


print("\nGreedy selection (budget=4, N=3):")
print(greedy_select(4, 3)) # set budget at 4 units of time, choose top 3

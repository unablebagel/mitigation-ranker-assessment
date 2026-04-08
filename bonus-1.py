import json
import math 

with open('input-bonus1.json', 'r') as file:
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
mitigations = {m["id"]: {"score": 0, "cost": m["cost"]} for m in data["mitigations"]}

def risk_score(threat):
    return threat["impact"] * threat["likelihood"] * math.log(threat["priority"])

for threat in threats.values():
    score = risk_score(threat)
    for mid in threat["mitigations"]:
        mitigations[mid]["score"] += score

for attrs in mitigations.values():
    attrs["adjusted_score"] = attrs["score"]/attrs["cost"]

sorted_mitigations = sorted(mitigations.items(), key=lambda x: x[1]["adjusted_score"], reverse=True)

print(f"{'ID':<6} {'Score':>10} {'Cost':>6} {'Adj. Score':>12}")
print("-" * 36)
for m in sorted_mitigations:
    print(f"{m[0]:<6} {m[1]['score']:>10.3f} {m[1]['cost']:>6} {m[1]['adjusted_score']:>12.3f}")

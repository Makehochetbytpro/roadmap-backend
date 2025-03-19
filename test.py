import time
import math

def bayesian_score(likes, dislikes, C=0.5, m=50):
    total_votes = likes + dislikes
    return (likes + C * m) / (total_votes + m)

def wilson_score(likes, dislikes, confidence=1.96):
    n = likes + dislikes
    if n == 0:
        return 0
    p = likes / n
    z = confidence
    denominator = 1 + z**2 / n
    numerator = p + z**2 / (2 * n) - z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)
    return numerator / denominator

roadmaps = [
    {"name": "Roadmap A", "likes": 230, "dislikes": 58},
    {"name": "Roadmap B", "likes": 120, "dislikes": 245},
    {"name": "Roadmap C", "likes": 450, "dislikes": 34},
    {"name": "Roadmap D", "likes": 90, "dislikes": 312},
    {"name": "Roadmap E", "likes": 345, "dislikes": 76},
    {"name": "Roadmap F", "likes": 600, "dislikes": 20},
    {"name": "Roadmap G", "likes": 50, "dislikes": 400},
]

# Bayesian Score
start_time = time.perf_counter()
for roadmap in roadmaps:
    roadmap["bayesian_score"] = bayesian_score(roadmap["likes"], roadmap["dislikes"])

sorted_roadmaps = sorted(roadmaps, key=lambda x: x["bayesian_score"], reverse=True)
end_time = time.perf_counter()

print("Bayesian Score Ranking:")
for roadmap in sorted_roadmaps:
    print(f"{roadmap['name']} - Likes: {roadmap['likes']}, Dislikes: {roadmap['dislikes']}, Bayesian Score: {roadmap['bayesian_score']:.6f}")

print(f"\nExecution time: {end_time - start_time:.6f} sec\n")

# Wilson Score
start_time = time.perf_counter()
for roadmap in roadmaps:
    roadmap["wilson_score"] = wilson_score(roadmap["likes"], roadmap["dislikes"])

sorted_roadmaps = sorted(roadmaps, key=lambda x: x["wilson_score"], reverse=True)
end_time = time.perf_counter()

print("Wilson Score Ranking:")
for roadmap in sorted_roadmaps:
    print(f"{roadmap['name']} - Likes: {roadmap['likes']}, Dislikes: {roadmap['dislikes']}, Wilson Score: {roadmap['wilson_score']:.6f}")

print(f"\nExecution time: {end_time - start_time:.6f} sec")

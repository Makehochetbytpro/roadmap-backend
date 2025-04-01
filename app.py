from flask import Flask, request, jsonify
import math

app = Flask(__name__)

def bayesian_score(likes, dislikes, C=0.5, m=50):
    total_votes = likes + dislikes
    return (likes + C * m) / (total_votes + m)

@app.route('/rank', methods=['POST'])
def rank_roadmaps():
    data = request.get_json()
    roadmaps = data.get("roadmaps", [])
    
    for roadmap in roadmaps:
        roadmap["bayesian_score"] = bayesian_score(roadmap["likes"], roadmap["dislikes"])
    
    sorted_roadmaps = sorted(roadmaps, key=lambda x: x["bayesian_score"], reverse=True)
    
    return jsonify({"bayesian_ranking": sorted_roadmaps})

if __name__ == '__main__':
    app.run(debug=True)
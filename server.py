from flask import Flask, request, jsonify
import requests
import json
app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def hello():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        r2 = requests.post('http://puzzles.makkhichoose.com/sudoku/solved', data=json.dumps(data),
                           headers={'content-type': 'application/json'})
        if r2.status_code == 200:
            j2 = r2.json()
            if j2["isSolved"]:
                return jsonify(solution = data["solution"], isSolved =  True)
            else:
                return jsonify(j2)
        else:
            return jsonify(solution = "No tokens are received", isSolved =  False)
    else:
       return jsonify(requests.get('http://puzzles.makkhichoose.com/sudoku/generate').json())
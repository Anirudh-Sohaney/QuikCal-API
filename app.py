from flask import Flask, request, jsonify

import foodcode


app = Flask(__name__)
app.json.sort_keys = False
@app.route('/inp', methods=['POST'])
def pull_data():
    x = request.get_json()
    result =foodcode.main(x)

    return jsonify(result)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
   

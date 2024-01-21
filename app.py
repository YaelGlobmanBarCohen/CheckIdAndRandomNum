import json
from flask import Flask, request, jsonify, render_template
import hashlib

app = Flask(__name__, template_folder='templates', static_folder='static')

# Store the last processed JSON that transfered to md5 hash. It's initialized to None
last_json_hash = None

def is_valid_israeli_id(id):
    # Convert the input to a string and remove leading/trailing whitespaces
    id = str(id).strip()
    
    # Verify the length of the ID is not greater than 9 and contains only digit characters
    if len(id) > 9 or not id.isdigit():
        return False
    
    # Pad the ID with leading zeros if its length is less than 9
    id = id.rjust(9, '0')

    # Calculate the weighted sum of digits, considering doubling and subtracting 9 if needed
    total = sum(int(digit) * ((i % 2) + 1) if int(digit) * ((i % 2) + 1) <= 9 else int(digit) * ((i % 2) + 1) - 9
                for i, digit in enumerate(id[::-1]))

    # Verify the total sum is a multiple of 10
    return total % 10 == 0

def is_valid_random_number(num):
    if isinstance(num, int) and (1e8 <= num < 1e9):
        return True
    return False

    
def hash_json(json_data):
    # Convert the JSON data to a string
    json_string = json.dumps(json_data, sort_keys=True)

    # Use MD5 hash function
    hash_object = hashlib.md5(json_string.encode())
    return hash_object.hexdigest()

# Compares the given Json with the last processed Json, updates the last_json variable, and returns either "New" or "Same" based on the comparison result
def process_json(json_data):
    global last_json_hash

    # Generate hash for the current JSON
    current_json_hash = hash_json(json_data)

    if last_json_hash is None:
        last_json_hash = current_json_hash
        return "New"

    if last_json_hash == current_json_hash:
        return "Same"
    else:
        last_json_hash = current_json_hash
        return "New"

@app.route('/process_json', methods=['POST'])
def process_json_endpoint():
    try:
        data = request.get_json()

        # Validate input format
        if "ID" not in data or "RandomNumber" not in data:
            return jsonify({"error": "Invalid JSON format"}), 400

        # Validate Israeli ID
        if not is_valid_israeli_id(data["ID"]):
            return jsonify({"error": "Invalid Israeli ID"}), 400

        # Validate RandomNumber format
        if not is_valid_random_number(data["RandomNumber"]):
            return jsonify({"error": "Invalid RandomNumber format"}), 400

        result = process_json(data)
        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

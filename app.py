from flask import Flask, request, jsonify
import numpy as np
import pickle

# Use raw string or double backslashes for Windows paths
model = pickle.load(open(r"C:\\csv_files\\model.pkl", 'rb'))

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        cgpa = float(request.form.get('cgpa'))  # Convert to float
        iq = float(request.form.get('iq'))      # Convert to float
        profile_score = float(request.form.get('profile_score'))  # Convert to float

        # Create an array with the input data
        input_data = np.array([[cgpa, iq, profile_score]])

        result = model.predict(input_data)[0]

        return jsonify({'Placement': str(result)})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)

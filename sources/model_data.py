import json
from flask import Flask, request
import pandas as pd
import pickle
from waitress import serve

app = Flask(__name__)

# Function to load model
def load_model(file_path):
    with open(file_path, 'rb') as f:
        model = pickle.load(f)
    return model

# Read CSV files and load model
data_test = pd.read_csv("./data/application_test.csv")
data_test_ohe = pd.read_csv("./data/application_test_ohe.csv")
customers_data = data_test
customers_data_ohe = data_test_ohe
model_path = "./data/best_model.pickle"
lgbm = load_model(model_path)

@app.route('/customer_data', methods=['GET'])
def customer_data():
    customer_id = request.args.get("customer_id")
    if customer_id is None:
        return json.dumps({"error": "Customer ID is missing"}), 400
    try:
        customer_id = int(customer_id)
        customer_row = customers_data[customers_data['SK_ID_CURR'] == customer_id]
        if customer_row.empty:
            return json.dumps({"error": "Customer not found"}), 404
        response = {'customer_data': customer_row.to_json()}
        return json.dumps(response)
    except ValueError:
        return json.dumps({"error": "Invalid customer ID"}), 400

@app.route('/predict', methods=['GET'])
def predict():
    customer_id = request.args.get("customer_id")
    if customer_id is None:
        return json.dumps({"error": "Customer ID is missing"}), 400
    try:
        customer_id = int(customer_id)
        customer_row = customers_data[customers_data['SK_ID_CURR'] == customer_id]
        if customer_row.empty:
            return json.dumps({"error": "Customer not found"}), 404
        customer_row_ohe = customers_data_ohe.iloc[customer_row.index].drop(columns=['SK_ID_CURR'], axis=1)
        predictions = lgbm.predict_proba(customer_row_ohe).tolist()
        response = {'customer_predict': predictions}
        return json.dumps(response)
    except ValueError:
        return json.dumps({"error": "Invalid customer ID"}), 400

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=8080)
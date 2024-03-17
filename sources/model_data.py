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
data_test = pd.read_csv("./data/application_test.csv", dtype={'SK_ID_CURR': str})
data_test_ohe = pd.read_csv("./data/application_test_ohe.csv", dtype={'SK_ID_CURR': str})
customers_data = data_test
customers_data_ohe = data_test_ohe
model_path = "./data/best_model.pickle"
lgbm = load_model(model_path)


@app.route('/customer_data', methods=['GET'])
def customer_data():
    customer_id = request.args.get("customer_id")
    customer_row = customers_data[customers_data['SK_ID_CURR'] == customer_id]
    response = {'customer_data': customer_row.to_json()}
    #response = {'customer_data': customer_row.tolist()}
    #response = {'customer_data': customer_row}
    return json.dumps(response)

@app.route('/predict', methods=['GET'])
def predict():
    customer_id = request.args.get("customer_id")
    customer_row = customers_data[customers_data['SK_ID_CURR'] == customer_id]
    if not customer_row.empty:
        customer_row_ohe = customers_data_ohe.iloc[customer_row.index].drop(columns=['SK_ID_CURR'], axis=1)
        predictions = lgbm.predict_proba(customer_row_ohe).tolist()
        response = {'customer_predict': predictions}
        return json.dumps(response)

if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=6060, debug=False)
    #serve(app, host="0.0.0.0", port=5000)
    serve(app, host="localhost", port=5000)

#if __name__ == '__main__':
#    app.run(host="localhost", port=8080, debug=True)

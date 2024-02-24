import json
#import flask
from flask import Flask, request
import pandas as pd
import pickle


app = Flask(__name__)

def flask_runner():
    app.run(port=8080)

# read csv file
data_test = pd.read_csv("./application_test.csv")
data_test_ohe = pd.read_csv("./application_test_ohe.csv")
customers_data = data_test
customers_data_ohe = data_test_ohe

# load model
lgbm = pickle.load(open('./best_model.pickle', 'rb'))


@app.route('/customer_data', methods=['GET'])
def customer_data():
    customer_id = request.args.get("customer_id")
    customer_row = customers_data[customers_data['SK_ID_CURR']==int(customer_id)]
    customer_index = customer_row.index
    response = {'customer_data': customer_row.to_json()}
    return json.dumps(response)

@app.route('/predict', methods=['GET'])
def predict():
    customer_id = request.args.get("customer_id")
    customer_row = customers_data[customers_data['SK_ID_CURR'] == int(customer_id)]
    customer_index = customer_row.index
    customer_row_ohe = customers_data_ohe.iloc[customer_index].drop(columns=['SK_ID_CURR'], axis=1)
    lgbm.predict_proba(customer_row_ohe)
    response = {'customer_predict': lgbm.predict_proba(customer_row_ohe).tolist()}
    return json.dumps(response)

#if __name__ == '__main__':
#    #app.run(host='0.0.0.0', port=1111, debug=True)
#    #app.run(debug=True)
#    from waitress import serve
#   serve(app, host="0.0.0.0", port=8080)




if __name__ == '__main__':
    flask_runner()



#python model_data.py
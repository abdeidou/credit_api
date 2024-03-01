import pytest
import json
import requests
from sources.model_data import customers_data, customers_data_ohe, lgbm

@pytest.fixture(scope="module")
def api_url():
    return "http://localhost:1111"

def test_customer_data_api(api_url):
    """Test the /customer_data API endpoint."""
    # Mock data
    customer_id = 100028
    expected_customer_data = customers_data[customers_data['SK_ID_CURR'] == customer_id].to_json()

    # Make request to API endpoint
    response = requests.get(f"{api_url}/customer_data", params={"customer_id": customer_id})

    # Assert response status code
    assert response.status_code == 200

    # Assert response content
    response_data = json.loads(response.text)
    assert response_data['customer_data'] == expected_customer_data

def test_predict_api(api_url):
    """Test the /predict API endpoint."""
    # Mock data
    customer_id = 100028
    customer_row = customers_data[customers_data['SK_ID_CURR'] == customer_id]
    customer_row_ohe = customers_data_ohe.iloc[customer_row.index].drop(columns=['SK_ID_CURR'], axis=1)
    expected_customer_predict = lgbm.predict_proba(customer_row_ohe).tolist()

    # Make request to API endpoint
    response = requests.get(f"{api_url}/predict", params={"customer_id": customer_id})

    # Assert response status code
    assert response.status_code == 200

    # Assert response content
    response_data = json.loads(response.text)
    assert response_data['customer_predict'] == expected_customer_predict



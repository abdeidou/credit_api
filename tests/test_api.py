import pytest
import json
from sources.model_data import customers_data, customers_data_ohe, lgbm
from sources.model_data import app


@pytest.fixture()
def client():
    with app.test_client() as client:
        return client

@pytest.fixture()
def customer_id():
    return 100028

@pytest.fixture()
def expected_customer_data(customer_id):
    return customers_data[customers_data['SK_ID_CURR'] == customer_id].to_json()

@pytest.fixture()
def expected_customer_predict(customer_id):
    customer_row = customers_data[customers_data['SK_ID_CURR'] == customer_id]
    customer_row_ohe = customers_data_ohe.iloc[customer_row.index].drop(columns=['SK_ID_CURR'], axis=1)
    return lgbm.predict_proba(customer_row_ohe).tolist()

def test_customer_data_api(client, customer_id, expected_customer_data):
    """Test the /customer_data API endpoint."""
    # Make request to API endpoint
    with client.get(f"/customer_data", query_string={"customer_id": customer_id}) as response:
        # Assert response status code
        assert response.status_code == 200

        # Assert response content
        response_data = json.loads(response.text)
        assert response_data['customer_data'] == expected_customer_data

def test_predict_api(client, customer_id, expected_customer_predict):
    """Test the /predict API endpoint."""
    # Make request to API endpoint
    with client.get(f"/predict", query_string={"customer_id": customer_id}) as response:
        # Assert response status code
        assert response.status_code == 200

        # Assert response content
        response_data = json.loads(response.text)
        assert response_data['customer_predict'] == expected_customer_predict
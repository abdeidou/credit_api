import pytest
import json
from sources.model_data import customers_data, customers_data_ohe, lgbm
from sources.model_data import app

# Les fixtures pour la configuration

# Fixture fournissant un client de test Flask
@pytest.fixture()
def client():
    with app.test_client() as client:
        return client
# Fixture fournissant un customer_id d'exemple pour les tests
@pytest.fixture()
def customer_id():
    return 100038

# Fixture fournissant des données JSON attendues pour un customer_id
@pytest.fixture()
def expected_customer_data(customer_id):
    return customers_data[customers_data['SK_ID_CURR'] == str(customer_id)].to_json()

# Fixture fournissant le résultat de prédiction attendu pour un customer_id
@pytest.fixture()
def expected_customer_predict(customer_id):
    customer_row = customers_data[customers_data['SK_ID_CURR'] == str(customer_id)]
    customer_row_ohe = customers_data_ohe.iloc[customer_row.index].drop(columns=['SK_ID_CURR'], axis=1)
    return lgbm.predict_proba(customer_row_ohe).tolist()

# Les fonctions de test

# Fonction test de customer_data
def test_customer_data_api(client, customer_id, expected_customer_data):
    # Faire une requête à l'API
    with client.get(f"/customer_data", query_string={"customer_id": customer_id}) as response:
        # Vérifier le statut de la réponse
        assert response.status_code == 200
        # Vérifier la réponse
        response_data = json.loads(response.text)
        assert response_data['customer_data'] == expected_customer_data

# Fonction test de predict
def test_predict_api(client, customer_id, expected_customer_predict):
    # Faire une requête à l'API
    with client.get(f"/predict", query_string={"customer_id": customer_id}) as response:
        # Vérifier le statut de la réponse
        assert response.status_code == 200
        # Vérifier la réponse
        response_data = json.loads(response.text)
        assert response_data['customer_predict'] == expected_customer_predict
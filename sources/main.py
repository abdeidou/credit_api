import pandas as pd
import streamlit as st
import requests

# Fonction initialiser les variables de session
def initialize_session_state():
    session_state_defaults = {
        'api_url': "https://credit-predict-2olkar52da-ew.a.run.app",
        'predict': False,
        'customer_found': False,
        'customer_data': [],
        'customer_id': -1,
        'model_data': False,
        'threshold': -1
    }
    for key, value in session_state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Fonction gérer le button chercher
def handle_search_button_click():
    initialize_session_state()
def handle_search(customer_id_input):
    endpoint = "/customer_data/"
    if not customer_id_input:
        st.sidebar.write(":red[Identifiant non renseigné]")
        st.session_state['customer_found'] = False
    else:
        url = f"{st.session_state['api_url']}{endpoint}"
        params = {"customer_id": customer_id_input}
        response = requests.get(url, params=params).json()
        customer_data = pd.read_json(response['customer_data'], dtype={'SK_ID_CURR': str})
        if customer_data.empty:
            st.sidebar.write(":red[Client non trouvé]")
            st.session_state['customer_found'] = False
        else:
            st.session_state['customer_found'] = True
            st.session_state['customer_id'] = customer_id_input
            st.session_state['customer_data'] = customer_data

# Fonction gérer le button predict
def handle_predict_button_click():
    st.session_state['predict'] = True
def handle_predict():
    endpoint = "/predict/"
    if st.session_state['predict']:
        # Récupérer la prédiction
        url = f"{st.session_state['api_url']}{endpoint}"
        params = {"customer_id": st.session_state['customer_id']}
        response = requests.get(url, params=params).json()
        positive_predict = response['positive_predict']
        prob_positive_predict = positive_predict[0]
        decision = response['decision']
        # Refuser le prêt si la probabilité de classe 1 est supérieur au threshold
        if decision=="refuse":
            color = "red"
            result = "Prêt refusé"
        else:
            color = "green"
            result = "Prêt accordé"
        perc_predict = round(100 * prob_positive_predict, 1)
        st.write(f'<p style="color:{color};">{result}</p>', unsafe_allow_html=True)
        st.write(f'<p style="color:{color};">{perc_predict}%</p>', unsafe_allow_html=True)

# Initialiser la session
initialize_session_state()

# Gérer la barre latérale
st.sidebar.header('Informations client')
first_name_input = st.sidebar.text_input("Nom", key='first_name_input')
last_name_input = st.sidebar.text_input("Prénom", key='last_name_input')
customer_id_input = st.sidebar.text_input("Identifiant*", key='customer_id_input')
if st.sidebar.button('Chercher', on_click=handle_search_button_click):
    handle_search(customer_id_input)

# Gérer la page centrale
if st.session_state['customer_found']:
    st.write("""
    # Prédiction de remboursement
    """)
    st.subheader('Données client')
    st.write(st.session_state['customer_data'])
    if st.button('Prédire', on_click=handle_predict_button_click):
        handle_predict()
else:
    st.image('./data/logo.png')
    intro = "Ceci est une maquette d'application de scoring crédit pour calculer la probabilité qu’un client rembourse son\
             crédit à la consommation pour des personnes ayant peu ou pas du tout d'historique de prêt."
    st.write(f'<p style="font-size:26px; color:blue;">{intro}</p>', unsafe_allow_html=True)

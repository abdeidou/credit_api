import pandas as pd
import streamlit as st
import requests
import subprocess
import os
import sys

# Function to initialize session state variables
def initialize_session_state():
    session_state_defaults = {
        'predict': False,
        'customer_found': False,
        'customer_data': [],
        'customer_id': -1,
        'model_data': False
    }
    for key, value in session_state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Function to start model data subprocess
def start_model_data_subprocess():
    if not st.session_state['model_data']:
        model_data_path = os.path.join('./sources', 'model_data.py')
        model_data = [sys.executable, model_data_path]
        subprocess.Popen(model_data)
        st.session_state['model_data'] = True

# Function to handle search button click
def handle_search_button_click():
    initialize_session_state()


def handle_search(customer_id_input):
    response = requests.get("http://localhost:8080/customer_data", params={"customer_id": customer_id_input}).json()
    customer_data = pd.read_json(response['customer_data'], dtype={'SK_ID_CURR': str})

    if customer_data.empty:
        st.sidebar.write(":red[Client non trouvé]")
    else:
        st.session_state['customer_found'] = True
        st.session_state['customer_id'] = customer_id_input
        st.session_state['customer_data'] = customer_data

# Function to handle predict button click

def handle_predict_button_click():
    st.session_state['predict'] = True

def handle_predict():
    if st.session_state['predict']:
        response = requests.get("http://localhost:8080/predict",
                                params={"customer_id": st.session_state['customer_id']}).json()
        customer_predict = response['customer_predict']

        if customer_predict[0][1] < customer_predict[0][0]:
            color = "green"
            result = "Prêt accordé"
        else:
            color = "red"
            result = "Prêt refusé"

        perc_predict = round(100 * customer_predict[0][0], 1)
        st.write(f'<p style="color:{color};">{result}</p>', unsafe_allow_html=True)
        st.write(f'<p style="color:{color};">{perc_predict}%</p>', unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

# Start model data subprocess
start_model_data_subprocess()

# Sidebar code
st.sidebar.header('Informations client')
first_name_input = st.sidebar.text_input("Nom", key='first_name_input')
last_name_input = st.sidebar.text_input("Prénom", key='last_name_input')
customer_id_input = st.sidebar.text_input("Identifiant*", key='customer_id_input')
if st.sidebar.button('Chercher', on_click=handle_search_button_click):
    handle_search(customer_id_input)


# App code
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

# streamlit run main.py

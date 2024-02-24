# import packages
import pandas as pd
import streamlit as st
import requests
import subprocess
import os, sys


# session state
if 'predict' not in st.session_state:
    st.session_state['predict'] = False
if 'customer_found' not in st.session_state:
    st.session_state['customer_found'] = False
if 'customer_data' not in st.session_state:
    st.session_state['customer_data'] = []
if 'customer_id' not in st.session_state:
    st.session_state['customer_id'] = -1
if 'model_data' not in st.session_state:
    st.session_state['model_data'] = False

if st.session_state['model_data'] == False:
    model_data = [f'{sys.executable}', os.path.join('.', 'model_data.py'), 'localhost', '8080']
    subprocess.Popen(model_data)
    st.session_state['model_data'] = True
# buttons methods
def predict_button():
    st.session_state['predict'] = True

def search_button():
    st.session_state['predict'] = False
    st.session_state['customer_found'] = False
    st.session_state['customer_id'] = -1
    st.session_state['customer_data'] = []

# sidebar code
st.sidebar.header('Informations client')
first_name = st.sidebar.text_input("Nom", '')
last_name = st.sidebar.text_input("Prénom", '')
customer_id = st.sidebar.text_input("Identifiant*", '')
if st.sidebar.button('Chercher', on_click=search_button):
    st.session_state['customer_id'] = customer_id


    response = requests.get("http://localhost:8080/customer_data", params={"customer_id": customer_id}).json()
    st.session_state['customer_data'] = pd.read_json(response['customer_data'], dtype={'SK_ID_CURR': str})
    if st.session_state['customer_data'].empty:
        st.sidebar.write(":red[Client non trouvé]")
    else:
        st.session_state['customer_found'] = True

# app code
if st.session_state['customer_found']:
    st.write("""
    # Prédiction de remboursement
    """)
    st.subheader('Données client')
    st.write(st.session_state['customer_data'])
    st.button('Prédire', on_click=predict_button)
    if st.session_state['predict']:
        response = requests.get("http://localhost:8080/predict", params={"customer_id": customer_id}).json()
        st.session_state['customer_predict'] = response['customer_predict']
        predict = {'Bon client': [str(round(100 * st.session_state['customer_predict'][0][0], 1)) + '%'],
                   'Mauvais client': [str(round(100 * st.session_state['customer_predict'][0][1], 1)) + '%']}
        df_predict = pd.DataFrame(predict)
        st.dataframe(df_predict, hide_index=True)
else:
    st.image('./logo.png')
    st.write("Application de scoring crédit pour calculer la probabilité qu’un client rembourse son\
             crédit à la consommation pour des personnes ayant peu ou pas du tout d'historique de prêt.")

# streamlit run main.py

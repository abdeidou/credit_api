import pandas as pd
import streamlit as st
import requests
import streamviz
from PIL import Image
import io
import base64

# Fonction initialiser les variables de session
def initialize_session_state():
    session_state_defaults = {
        'api_url': "https://credit-predict-2olkar52da-ew.a.run.app",
        'customer_found': False,
        'customer_data': [],
        'customer_id': -1,
        'model_data': False,
        'threshold': -1,
        'predict': False,
        'explain_local': False,
        'explain_global': False,
        'position': False
    }
    for key, value in session_state_defaults.items():
        st.session_state[key] = value

# Initialiser la session
if 'api_url' not in st.session_state:
    initialize_session_state()


# Fonction pour gérer la recherche de client
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

# Fonction pour gérer le bouton de prédiction
def handle_predict_button_click():
    st.session_state['predict'] = True

def handle_predict():
    endpoint_predict = "/predict/"
    endpoint_threshold = "/threshold"
    if st.session_state['predict']:
        url = f"{st.session_state['api_url']}{endpoint_predict}"
        params = {"customer_id": st.session_state['customer_id']}
        response = requests.get(url, params=params).json()
        negative_predict = response['negative_predict']
        prob_negative_predict = negative_predict[0]

        url = f"{st.session_state['api_url']}{endpoint_threshold}"
        response = requests.get(url).json()
        threshold = response['threshold']
        streamviz.gauge(gVal=prob_negative_predict, grLow=threshold, gcLow='#008000', gcMid='#FF0000', gcHigh='#FF0000', sFix='%')

# Fonctions pour gérer l'explication locale
def handle_explain_local_button_click():
    st.empty()
    st.session_state['explain_global'] = False
    st.session_state['explain_local'] = True
    st.session_state['predict'] = False
    st.session_state['position'] = False

st.empty()

def handle_explain_local():
    st.write("handle_explain_local")
    endpoint = "/explain_local"
    if st.session_state['explain_local']:
        url = f"{st.session_state['api_url']}{endpoint}"
        shap_plot_data = get_shap_plot_data(url, mode='local')
        if shap_plot_data is not None:
            graph_data_base64 = shap_plot_data.get('shap_plot', '')
            # Convertir les données base64 en image PIL
            image_base64 = Image.open(io.BytesIO(base64.b64decode(graph_data_base64)))
            # Convertir l'image en mode RGB
            image_base64 = image_base64.convert('RGB')
            # Créer un buffer mémoire pour sauvegarder l'image
            buffered = io.BytesIO()
            # Sauvegarder l'image dans le buffer au format JPEG
            image_base64.save(buffered, format="JPEG")
            # Convertir l'image sauvegardée dans le buffer en données base64
            jpeg_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            # Construire le lien HTML avec l'image encodée en base64
            image_html = f'<img src="data:image/jpeg;base64,{jpeg_image_base64}" alt="Description de l\'image">'
            # Afficher l'image dans Streamlit à l'aide de st.markdown
            st.markdown(image_html, unsafe_allow_html=True)


# Fonctions pour gérer l'explication globale
def handle_explain_global_button_click():
    st.session_state['explain_global'] = True
    st.session_state['explain_local'] = False
    st.session_state['predict'] = False
    st.session_state['position'] = False


def handle_explain_global():
    st.write("handle_explain_global")
    endpoint = "/explain_global"
    if st.session_state['explain_global']:
        url = f"{st.session_state['api_url']}{endpoint}"
        shap_plot_data = get_shap_plot_data(url, mode='global')
        if shap_plot_data is not None:
            graph_data_base64 = shap_plot_data.get('shap_plot', '')
            # Convertir les données base64 en image PIL
            image_base64 = Image.open(io.BytesIO(base64.b64decode(graph_data_base64)))
            # Convertir l'image en mode RGB
            image_base64 = image_base64.convert('RGB')
            # Créer un buffer mémoire pour sauvegarder l'image
            buffered = io.BytesIO()
            # Sauvegarder l'image dans le buffer au format JPEG
            image_base64.save(buffered, format="JPEG")
            # Convertir l'image sauvegardée dans le buffer en données base64
            jpeg_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            # Construire le lien HTML avec l'image encodée en base64
            image_html = f'<img src="data:image/jpeg;base64,{jpeg_image_base64}" alt="Description de l\'image">'
            # Afficher l'image dans Streamlit à l'aide de st.markdown
            st.markdown(image_html, unsafe_allow_html=True)

# Fonction pour récupérer les données SHAP
def get_shap_plot_data(url, mode):
    try:
        if mode=='local':
            params = {"customer_id": st.session_state['customer_id']}
            response = requests.get(url, params=params)
        else:
            response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur lors de la récupération des données : {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {str(e)}")
        return None

# Fonction pour gérer le positionnement
def handle_position_button_click():
    st.session_state['explain_global'] = False
    st.session_state['explain_local'] = False
    st.session_state['predict'] = False
    st.session_state['position'] = True

def handle_position():
    st.write('position')

# Gérer la barre latérale
st.sidebar.header('Informations client')
customer_id_input = st.sidebar.text_input("Identifiant*", key='customer_id_input')
if st.sidebar.button('Chercher', on_click=handle_search_button_click):
    handle_search(customer_id_input)
if st.session_state['customer_found']:
    st.sidebar.button('Prédire', on_click=handle_predict_button_click)
    st.sidebar.button('Expliquer local ', on_click=handle_explain_local_button_click)
    st.sidebar.button('Expliquer global', on_click=handle_explain_global_button_click)
    st.sidebar.button('Positionner', on_click=handle_position_button_click)

# Gérer la page centrale
if st.session_state['customer_found']:
    if st.session_state['predict']:
        st.write("""
        # Prédiction
        """)
        handle_predict()
    elif st.session_state['explain_local']:
        st.write("""
        # Expliquer local
        """)
        handle_explain_local()
    elif st.session_state['explain_global']:
        st.write("""
        # Expliquer global
        """)
        handle_explain_global()
    elif st.session_state['position']:
        st.write("""
        # Position
        """)
        handle_position()
    else:
        st.write("""
        # Données client
        """)
        st.write(st.session_state['customer_data'])
else:
    st.image('../data/logo.png')
    intro = "Ceci est une maquette d'application de scoring crédit pour calculer la probabilité qu’un client rembourse son\
             crédit à la consommation pour des personnes ayant peu ou pas du tout d'historique de prêt."
    st.write(f'<p style="font-size:26px; color:blue;">{intro}</p>', unsafe_allow_html=True)


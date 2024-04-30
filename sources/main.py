import pandas as pd
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import os


# Fonction pour initialiser les variables de session
def initialize_session_state():
    session_state_defaults = {
        'api_url': "https://credit-predict-2olkar52da-ew.a.run.app",
        'customer_found': False,
        'customer_id': -1,
        'search': False,
        'predict': False,
        'explain': False,
        'position': False,
        'position_page_index': 1,
        'search_df_file_path': '',
        'predict_fig_file_path': '',
        'explain_local_img_file_path': '',
        'explain_global_img_file_path': '',
    }
    for key, value in session_state_defaults.items():
        st.session_state[key] = value


# Initialisation de la session
if 'api_url' not in st.session_state:
    initialize_session_state()


# SupprimeR les fichiers temporaires.
def safe_delete_data_files():
    file_paths = [
        'search_df_file_path',
        'predict_fig_file_path',
        'explain_local_img_file_path',
        'explain_global_img_file_path'
    ]
    for file_key in file_paths:
        if file_key in st.session_state:
            file_path = st.session_state[file_key]
            if os.path.exists(file_path):
                os.remove(file_path)

# EnregistreR les données (en fonction du mode) dans un répertoire local.
def save_to_data(obj, mode):
    directory = "./data"
    if not os.path.exists(directory):
        st.error(f"Dossier '{directory}' n'existe pas.")
        return
    full_path = ''
    if mode == 'search':
        file_name = "search.csv"
        full_path = os.path.join(directory, file_name)
        obj.to_csv(full_path, index=False)
    elif mode == 'predict':
        file_name = "predict.png"
        full_path = os.path.join(directory, file_name)
        obj.write_image(full_path)
    elif mode == 'explain_local':
        file_name = "explain_local.png"
        full_path = os.path.join(directory, file_name)
        obj.save(full_path, 'PNG')
    elif mode == 'explain_global':
        file_name = "explain_global.png"
        full_path = os.path.join(directory, file_name)
        obj.save(full_path, 'PNG')
    return full_path


# Fonction pour gérer la recherche de client
def handle_search_button_click():
    safe_delete_data_files()
    initialize_session_state()
    st.session_state['search'] = True


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
            st.session_state['search_df_file_path'] = save_to_data(customer_data, 'search')


def display_result_search():
    """Affiche les résultats de la recherche dans un tableau."""
    st.markdown('<div id="search"><h1>Données client</h1></div>', unsafe_allow_html=True)
    customer_row = pd.read_csv(st.session_state['search_df_file_path'], dtype={'SK_ID_CURR': str})
    st.dataframe(customer_row, use_container_width=True)


# Gestion de la prédiction
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

        # Récupérer le seuil de décision
        url = f"{st.session_state['api_url']}{endpoint_threshold}"
        response = requests.get(url).json()
        threshold = response['threshold']

        # Définir la décision et la couleur en fonction du seuil
        if prob_negative_predict < threshold - 0.05:
            decision_text = "Prêt accordé"
            gauge_color = "green"
        elif threshold - 0.05 <= prob_negative_predict <= threshold + 0.05:
            decision_text = "Décision en attente"
            gauge_color = "orange"
        else:
            decision_text = "Prêt refusé"
            gauge_color = "red"

        # Création d'un indicateur de jauge
        fig = go.Figure(go.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=prob_negative_predict,
            number={'font': {'color': gauge_color}},
            mode="gauge+number+delta",
            title={'text': decision_text, 'font': {'color': gauge_color, 'size': 24}},
            delta={'reference': threshold, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            gauge={'axis': {'range': [None, 1]},
                   'bar': {'color': "blue"},
                   'steps': [
                       {'range': [0, threshold - 0.05], 'color': "green"},
                       {'range': [threshold - 0.05, threshold + 0.05], 'color': "orange"},
                       {'range': [threshold + 0.05, 1], 'color': "red"}],
                   'threshold': {'line': {'color': "red", 'width': 3}, 'thickness': 0.75, 'value': threshold}}))

        st.session_state['predict_fig_file_path'] = save_to_data(fig, 'predict')


def display_result_predict():
    """Affiche les résultats de la prédiction."""
    st.markdown('<div id="predict"><h1>Prédiction</h1></div>', unsafe_allow_html=True)
    st.image(st.session_state['predict_fig_file_path'], caption="Résultat de prédiction")


# Fonction pour expliquer les résultats
def handle_explain_button_click():
    st.session_state['explain'] = True


def handle_explain():
    if st.session_state['explain']:
        col1, col2 = st.columns(2)
        # Explication locale
        with col1:
            endpoint = "/explain_local/"
            url = f"{st.session_state['api_url']}{endpoint}"
            response = get_shap_plot_data(url, mode='local')
            if response and response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                st.session_state['explain_local_img_file_path'] = save_to_data(img, 'explain_local')
            else:
                st.error("Une erreur s'est produite lors de la récupération de l'explication locale.")

        # Explication globale
        with col2:
            endpoint = "/explain_global/"
            url = f"{st.session_state['api_url']}{endpoint}"
            response = get_shap_plot_data(url, mode='global')
            if response and response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                st.session_state['explain_global_img_file_path'] = save_to_data(img, 'explain_global')
            else:
                st.error("Une erreur s'est produite lors de la récupération de l'explication globale.")


def get_shap_plot_data(url, mode):
    """Récupère les données pour le tracé SHAP en mode local ou global."""
    try:
        if mode == 'local':
            params = {"customer_id": st.session_state['customer_id']}
            response = requests.get(url, params=params)
        else:
            response = requests.get(url)
        if response.status_code == 200:
            return response
        else:
            st.error(f"Erreur lors de la récupération de shap plot : {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erreur lors de la récupération de shap plot : {str(e)}")
        return None


def display_result_explain():
    """Affiche les explications sous forme d'images."""
    st.markdown('<div id="explain"><h1>Explication</h1></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.image(st.session_state['explain_local_img_file_path'], caption='Locale')
    with col2:
        st.image(st.session_state['explain_global_img_file_path'], caption='Globale')


# Gestion du positionnement
def handle_position_button_click():
    st.session_state['position'] = True
    st.session_state['position_page_index'] = 1

def handle_position():
    return

def display_result_position():
    st.markdown('<div id="position"><h1>Positionnement</h1></div>', unsafe_allow_html=True)
    # Récuperer la liste de variables
    endpoint_feature_names = "/feature_names"
    url = f"{st.session_state['api_url']}{endpoint_feature_names}"
    response = requests.get(url).json()
    feature_names = response['feature_names']
    # Déterminez le nombre d'options à afficher à la fois
    options_per_page = 10
    # Déterminez le nombre total de pages
    total_pages = len(feature_names) // options_per_page
    # Sélectionnez les options pour la page actuelle
    page_index = st.session_state['position_page_index']
    start_index = page_index * options_per_page
    end_index = min((page_index + 1) * options_per_page, len(feature_names))
    options_to_display = feature_names[start_index:end_index]
    # Ajouter une option vide au début de chaque page
    options_to_display_with_empty = [""] + options_to_display
    # Sélectionner l'option vide par défaut
    default_index = 0
    # Afficher les options avec une option vide et un bouton "Next" et "Previous"
    variable_select = st.radio("Choix de variable:",
                               options_to_display_with_empty,
                               index=default_index)
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("Previous", disabled=(page_index == 1)):
            st.session_state['position_page_index'] = max(page_index - 1, 0)
            # Rafraichir la page
            st.rerun()
    with col2:
        st.write(f"Page {page_index}/{total_pages}")
    with col3:
        if st.button("Next", disabled=(page_index == total_pages)):
            st.session_state['position_page_index'] = min(page_index + 1, total_pages)
            # Rafraichir la page
            st.rerun()
    # En cas de sélection
    if variable_select != "":
        endpoint_position = "/position/"
        params = {"customer_id": st.session_state['customer_id'], "variable": variable_select}
        url = f"{st.session_state['api_url']}{endpoint_position}"
        response = requests.get(url, params=params)
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            response = response.json()
            customer_value = response['customer_value']
            customers_min_value = response['customers_min_value']
            customers_max_value = response['customers_max_value']
            plot_positioning_graph(customer_value, customers_min_value, customers_max_value, variable_select)
        else:
            st.error("Une erreur s'est produite lors de la génération du tracé positionnement.")

def plot_positioning_graph(customer_value, customers_min_value, customers_max_value, feature):
    # Création des étiquettes pour les barres
    labels = ['Autres clients min', 'Valeur client', 'Autres clients max']
    # Valeurs des barres
    values = [customers_min_value, customer_value, customers_max_value]
    # Création du graphique
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.barh(labels, values, color=['green', 'blue', 'red'])
    ax.set_xlabel(feature)
    # Ajouter des annotations de texte sur les barres
    for bar in bars:
        width = bar.get_width()  # Obtient la largeur de la barre
        label_x_pos = width - 0.5 * width  # Place le texte légèrement vers
        ax.text(label_x_pos, bar.get_y() + bar.get_height() / 2, f'{round(width,2)}', va='center')
    st.pyplot(fig)



# Gestion de la barre latérale
st.sidebar.header('Informations client')
customer_id_input = st.sidebar.text_input("Identifiant*", key='customer_id_input', value='100028')
if st.sidebar.button('Chercher', on_click=handle_search_button_click):
    with st.spinner('Recherche en cours...'):
        handle_search(customer_id_input)

if st.session_state['customer_found']:
    if st.sidebar.button('Prédire', on_click=handle_predict_button_click):
        with st.spinner('Prédiction en cours...'):
            handle_predict()
    if st.sidebar.button('Expliquer', on_click=handle_explain_button_click):
        with st.spinner('Explication en cours...'):
            handle_explain()
    if st.sidebar.button('Positionner', on_click=handle_position_button_click):
        with st.spinner('Positionnement en cours...'):
            handle_position()

# Gestion de la page centrale
if st.session_state['customer_found']:
    if st.session_state['search']:
        display_result_search()
    if st.session_state['predict']:
        display_result_predict()
    if st.session_state['explain']:
        display_result_explain()
    if st.session_state['position']:
        display_result_position()
else:
    st.image('./data/logo.png')
    intro = "Ceci est une maquette d'application de scoring crédit pour calculer la probabilité qu’un client rembourse son crédit à la consommation pour des personnes ayant peu ou pas du tout d'historique de prêt."
    st.write(f'<p style="font-size:26px; color:blue;">{intro}</p>', unsafe_allow_html=True)





"""Interface Streamlit de MaintAI : explorer les données, puis demander une prédiction à l'API.

Lancement (depuis la racine du projet) :
python -m streamlit run ui/app.py
"""

import httpx
import pandas as pd
import streamlit as st

from maintai.client import APIError, MaintaiClient
from maintai.config import FEATURES, get_settings


st.set_page_config(
    page_title="MaintAI",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 MaintAI · Prédiction de panne")
st.markdown(
    "Analyse des données des équipements et prédiction des risques de panne."
)


@st.cache_data
def charger(path) -> pd.DataFrame:
    # Lu une seule fois : Streamlit relance tout le script à chaque clic
    return pd.read_csv(path)


# Configuration de l'API
with st.sidebar:
    st.header("⚙️ Configuration")

    url = st.text_input(
        "URL de l'API",
        "http://localhost:8000"
    )

    cle = st.text_input(
        "Clé API",
        type="password"
    )


# Création des onglets
onglet_donnees, onglet_prediction = st.tabs(
    ["📊 Données", "🤖 Prédiction"]
)


# --------------------------------------------------
# SPRINT 1 : EXPLORATION DES DONNÉES
# --------------------------------------------------

with onglet_donnees:

    st.header("📊 Tableau de bord des équipements")
    st.caption("Vue globale et analyse des données de maintenance.")

    try:
        df = charger(get_settings().data_path)

        if df.empty:
            st.warning("Le dataset est vide.")

        else:
            # Vérification des colonnes nécessaires
            colonnes_requises = FEATURES + ["failure"]
            colonnes_manquantes = [
                c for c in colonnes_requises if c not in df.columns
            ]

            if colonnes_manquantes:
                st.error(
                    f"Colonnes manquantes dans le dataset : {colonnes_manquantes}"
                )
            else:

                # ------------------------------------------
                # 1. INDICATEURS PRINCIPAUX
                # ------------------------------------------

                st.subheader("Vue d'ensemble")

                nombre_releves = len(df)
                nombre_pannes = int(df["failure"].sum())
                nombre_normaux = nombre_releves - nombre_pannes
                taux_panne = df["failure"].mean() * 100
                temperature_moyenne = df["temperature_c"].mean()

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Total des relevés",
                    f"{nombre_releves:,}"
                )

                col2.metric(
                    "Équipements en panne",
                    f"{nombre_pannes:,}"
                )

                col3.metric(
                    "Taux de panne",
                    f"{taux_panne:.2f} %"
                )

                col4.metric(
                    "Température moyenne",
                    f"{temperature_moyenne:.2f} °C"
                )

                st.divider()

                # ------------------------------------------
                # 2. DISTRIBUTION DES PANNES
                # ------------------------------------------

                st.subheader("1. Répartition des états")

                col_graph1, col_graph2 = st.columns(2)

                with col_graph1:

                    distribution = pd.DataFrame({
                        "État": ["Normal", "Panne"],
                        "Nombre de relevés": [
                            nombre_normaux,
                            nombre_pannes
                        ]
                    })

                    st.bar_chart(
                        distribution,
                        x="État",
                        y="Nombre de relevés",
                        color="État"
                    )

                with col_graph2:

                    st.write("Proportion des relevés")

                    st.write(
                        f"🟢 Normal : {nombre_normaux / nombre_releves * 100:.2f} %"
                    )

                    st.progress(
                        nombre_normaux / nombre_releves
                    )

                    st.write(
                        f"🔴 Panne : {taux_panne:.2f} %"
                    )

                    st.progress(
                        nombre_pannes / nombre_releves
                    )

                st.divider()

                # ------------------------------------------
                # 3. TAUX DE PANNE SELON UNE VARIABLE
                # ------------------------------------------

                st.subheader("2. Analyse des facteurs de panne")

                st.write(
                    "Étudiez comment les différentes mesures des capteurs "
                    "influencent le taux de panne."
                )

                variable = st.selectbox(
                    "Choisir une variable à analyser :",
                    FEATURES
                )

                df_analyse = df[
                    [variable, "failure"]
                ].dropna().copy()

                if df_analyse[variable].nunique() > 1:

                    df_analyse["tranche"] = pd.cut(
                        df_analyse[variable],
                        bins=10,
                        duplicates="drop"
                    )

                    taux_par_tranche = (
                        df_analyse
                        .groupby("tranche", observed=False)["failure"]
                        .mean()
                        .mul(100)
                        .reset_index()
                    )

                    taux_par_tranche["tranche"] = (
                        taux_par_tranche["tranche"].astype(str)
                    )

                    st.bar_chart(
                        taux_par_tranche,
                        x="tranche",
                        y="failure",
                        x_label=variable,
                        y_label="Taux de panne (%)"
                    )

                else:
                    st.warning(
                        "Pas assez de valeurs différentes pour créer des tranches."
                    )

                st.divider()

                # ------------------------------------------
                # 4. RELATION TEMPÉRATURE / VIBRATION
                # ------------------------------------------

                st.subheader("3. Relation entre température et vibration")

                st.write(
                    "Chaque point représente un relevé de capteur. "
                    "La couleur distingue les relevés normaux des pannes."
                )

                colonnes_scatter = [
                    "temperature_c",
                    "vibration_mm_s",
                    "failure"
                ]

                df_scatter = df[colonnes_scatter].dropna().copy()

                df_scatter["État"] = df_scatter["failure"].map({
                    0: "Normal",
                    1: "Panne"
                })

                st.scatter_chart(
                    df_scatter,
                    x="temperature_c",
                    y="vibration_mm_s",
                    color="État",
                    x_label="Température (°C)",
                    y_label="Vibration (mm/s)"
                )

                st.divider()

                # ------------------------------------------
                # 5. APERÇU DES DONNÉES
                # ------------------------------------------

                st.subheader("4. Données brutes")

                with st.expander("Consulter les relevés du dataset"):

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.caption(
                        f"Dataset : {len(df)} lignes et {len(df.columns)} colonnes."
                    )

    except FileNotFoundError:
        st.error(
            "Fichier de données introuvable. Vérifiez le chemin dans config.py."
        )

    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")


# --------------------------------------------------
# SPRINT 2 : PRÉDICTION VIA L'API
# --------------------------------------------------

with onglet_prediction:

    st.header("🤖 Prédiction du risque de panne")

    st.write(
        "Saisissez les mesures d'un équipement pour estimer son risque de panne."
    )

    with st.form("releve"):

        releve = {
            "temperature_c": st.slider(
                "Température (°C)",
                -40.0, 150.0, 72.0
            ),

            "vibration_mm_s": st.slider(
                "Vibration (mm/s)",
                0.0, 50.0, 6.0
            ),

            "load_pct": st.slider(
                "Charge (%)",
                0.0, 100.0, 85.0
            ),

            "runtime_hours": st.number_input(
                "Heures de fonctionnement",
                0, 100_000, 15000
            ),
        }

        envoye = st.form_submit_button(
            "🔍 Prédire",
            use_container_width=True
        )

    if envoye:

        try:
            # Création du client et appel de l'API
            api = MaintaiClient(url, api_key=cle or None)

            resultat = api.predict(releve)

            # Récupération des informations retournées
            probabilite = resultat["failure_probability"]
            pct = probabilite * 100

            # Affichage de la probabilité
            st.subheader("Résultat de la prédiction")

            st.metric(
                "Probabilité de panne",
                f"{pct:.2f} %"
            )

            st.progress(
                min(max(float(probabilite), 0.0), 1.0)
            )

            # Affichage de l'alerte
            if resultat["alert"]:
                st.error(
                    "⚠️ Attention ! Risque de panne détecté."
                )

            else:
                st.success(
                    "✅ Fonctionnement normal. Aucune alerte de panne."
                )

            # Affichage des détails
            with st.expander("Voir les détails de la prédiction"):
                st.json(resultat)

        except APIError as e:

            st.warning(
                f"Erreur API ({e.status_code}) : {e.detail}"
            )

        except httpx.HTTPError as e:

            st.error(
                f"API injoignable. Vérifiez que le serveur est lancé. Détail : {e}"
            )

        except (KeyError, TypeError, ValueError) as e:

            st.error(
                f"Réponse de l'API invalide : {e}"
            )

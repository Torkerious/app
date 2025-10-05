import streamlit as st
import os
from streamlit-3d-model import st-3d-model # Requiere pip install streamlit-3d-model

# --- Configuración y Ruta de Archivo ---
st.set_page_config(layout="wide")
st.title("Visor de Modelo 3D Estático (tierra.glb)")

MODELO_PATH = "modelos3d/tierra.glb"

# Asegurar que la ruta y el archivo existen
if not os.path.exists(MODELO_PATH):
    st.error(f"¡ERROR! El archivo '{MODELO_PATH}' no se encontró. Asegúrate de que la carpeta 'modelos3d' existe y contiene 'tierra.glb'.")
else:
    st.info(f"Cargando modelo principal: {MODELO_PATH}")

    # --- Carga y Renderizado ---
    # st_3d_model maneja la renderización y la interactividad (zoom, rotación)
    st_3d_model(
        model=MODELO_PATH,
        key="tierra_gltf_viewer",
        # Parámetros para configurar el aspecto inicial
        camera_position=[0, 0, 5],
        # Ajusta el tamaño de la ventana de visualización
        height=600,
        width=800, 
        background_color="#f0f2f6"
    )

    st.markdown("""
    ---
    ### Interacciones
    * **Rotar:** Clic y arrastrar.
    * **Zoom:** Rueda del ratón.
    * **Modelo Cargado:** `tierra.glb`
    """)

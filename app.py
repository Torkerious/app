import streamlit as st
import pyvista as pv
from stpyvista import stpyvista
import os
import trimesh

# --- 1. Configuración de Streamlit y Rutas ---
st.set_page_config(layout="wide")
st.title("Visor 3D con stpyvista (Carga de GLB)")

MODELO_PATH = "modelos3d/tierra.glb"

# Crear el directorio si no existe (solo para propósito de prueba)
os.makedirs(os.path.dirname(MODELO_PATH), exist_ok=True)


# --- 2. Función de Carga y Visualización con PyVista ---

def load_and_render_model(model_path):
    """
    Carga el modelo 3D usando PyVista/Trimesh y lo renderiza.
    """
    if not os.path.exists(model_path):
        st.error(f"❌ ¡ERROR! El archivo '{model_path}' no se encontró. Por favor, crea la carpeta 'modelos3d' y coloca 'tierra.glb' dentro.")
        return None

    try:
        # 2.1 Cargar el modelo con trimesh (que soporta GLB) y convertirlo a PyVista
        # PyVista/VTK tiene mejor soporte para mallas simples, pero trimesh es mejor para GLB.
        # Luego convertimos a un objeto PyVista.
        mesh = trimesh.load_mesh(model_path, file_type='glb')
        
        # Si el modelo tiene múltiples partes, combinarlas
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(mesh.dump(cached=True))
        
        # Convertir la malla Trimesh a un objeto PyVista (PolyData)
        pv_mesh = pv.wrap(mesh)
        
        # 2.2 Crear el plotter (visor) de PyVista
        plotter = pv.Plotter(window_size=[800, 600], off_screen=True)
        plotter.add_mesh(pv_mesh, color='lightgray', show_edges=False)

        # Configuración de cámara y estilo
        plotter.background_color = 'white'
        plotter.camera_position = 'iso'
        plotter.show_axes()

        st.success(f"✅ Modelo '{os.path.basename(model_path)}' cargado exitosamente.")
        return plotter

    except Exception as e:
        st.error(f"❌ Error al cargar o procesar el archivo GLB: {e}")
        st.info("Sugerencia: El soporte para GLB depende de las librerías subyacentes. Si el error persiste, intenta con un archivo .stl o .obj simple.")
        return None

# --- 3. Renderizado en Streamlit ---

plotter = load_and_render_model(MODELO_PATH)

if plotter:
    # Renderizar el visor PyVista usando el componente stpyvista
    stpyvista(plotter, key="pyvista_tierra", panel_size=(25, 25))

    st.markdown("""
    ---
    ### Interacciones
    `stpyvista` proporciona interactividad completa de PyVista/VTK:
    * **Rotación:** Botón izquierdo del ratón.
    * **Zoom (Acercar/Alejar):** Rueda del ratón o botón derecho arrastrando.
    * **Panorámica (Mover):** Botón central (rueda presionada) o `Ctrl` + botón izquierdo.
    """)

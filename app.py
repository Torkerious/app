import streamlit as st
import numpy as np
import plotly.graph_objects as go
import trimesh
import os

# --- Configuración de Ruta de Archivo ---
MODELOS_DIR = "modelos3d"
# Cambiamos a Earth.stl
MODELO_PATH = os.path.join(MODELOS_DIR, "Earth.stl") 

# --- 1. Configuración de Streamlit y Estado ---
st.set_page_config(layout="wide")
st.title("Laboratorio 3D: Carga de Earth.stl y Experimentación con Plotly 🌎")

# Inicializar estado para trazas adicionales
if 'additional_traces' not in st.session_state:
    st.session_state.additional_traces = []

# --- 2. Funciones de Modelado (Elementos de Experimentación) ---

def crear_cubo(size=10, color='blue', center=(-20, 0, 0)):
    """Crea un cubo para añadir como elemento adicional."""
    h = size / 2.0
    x_base = np.array([-h, h, -h, h, -h, h, -h, h]) + center[0]
    y_base = np.array([-h, -h, h, h, -h, -h, h, h]) + center[1]
    z_base = np.array([-h, -h, -h, -h, h, h, h, h]) + center[2]
    
    # Definición de caras triangulares (índices)
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]; j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]; k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    
    return go.Mesh3d(
        x=x_base, y=y_base, z=z_base, i=i, j=k, k=j,
        color=color, opacity=0.8, name=f'Cubo {size}'
    )

def crear_esfera(radio=8, color='red', center=(20, 20, 20)):
    """Crea una esfera para añadir como elemento adicional (usando Surface)."""
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x = center[0] + radio * np.outer(np.cos(u), np.sin(v))
    y = center[1] + radio * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radio * np.outer(np.ones(np.size(u)), np.cos(v))
    
    return go.Surface(
        x=x, y=y, z=z,
        colorscale='Reds', showscale=False,
        opacity=0.9, name=f'Esfera {radio}'
    )

# --- 3. Función de Carga del Modelo STL ---

def load_stl_for_plotly(file_path):
    """Carga STL, lo convierte en una malla Plotly (go.Mesh3d)."""
    if not os.path.exists(file_path):
        st.error(f"❌ ¡ERROR! El archivo '{file_path}' no se encontró. Asegúrate de que la carpeta 'modelos3d' contiene 'Earth.stl'.")
        return None
    
    try:
        with st.spinner(f"Procesando {os.path.basename(file_path)}..."):
            # Cargar el modelo STL
            # No necesitamos especificar file_type, trimesh lo detecta
            mesh = trimesh.load_mesh(file_path)

            if isinstance(mesh, trimesh.Scene):
                # Combinar todas las mallas en una sola para Plotly
                mesh = trimesh.util.concatenate(mesh.dump(cached=True))

            # Crear la traza de Plotly (Mesh3d)
            trace = go.Mesh3d(
                x=mesh.vertices[:, 0], 
                y=mesh.vertices[:, 1], 
                z=mesh.vertices[:, 2],
                i=mesh.faces[:, 0], 
                j=mesh.faces[:, 1], 
                k=mesh.faces[:, 2],
                color='lightblue', # Color base para el STL
                opacity=0.7,
                name="Earth.stl",
            )
        return trace
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo STL con trimesh: {e}")
        return None

# --- 4. Carga del Modelo Principal y Creación de la Figura ---

main_trace = load_stl_for_plotly(MODELO_PATH)
fig = go.Figure()
model_loaded = False

if main_trace:
    fig.add_trace(main_trace)
    st.sidebar.success("Modelo principal 'Earth.stl' cargado.")
    model_loaded = True
else:
    st.sidebar.warning("Solo se mostrarán los elementos adicionales si los añades.")


# --- 5. Interfaz para Añadir Modelos de Experimentación ---

st.sidebar.header("Añadir Geometría para Experimentación")

model_options = {"Ninguno": None, "Esfera Roja": "esfera", "Cubo Azul": "cubo"}
selected_model = st.sidebar.selectbox("Selecciona un elemento:", list(model_options.keys()))

col_b1, col_b2 = st.sidebar.columns(2)

if col_b1.button("Añadir Elemento", key='add_geo'):
    if model_options[selected_model] == "esfera":
        st.session_state.additional_traces.append(crear_esfera())
    elif model_options[selected_model] == "cubo":
        st.session_state.additional_traces.append(crear_cubo())
    # Recarga para que la figura se actualice
    st.experimental_rerun() 

if col_b2.button("Limpiar Adicionales", key='clear_geo'):
    st.session_state.additional_traces = []
    st.experimental_rerun()

# --- 6. Renderizado Final ---

# Añadir todos los trazos adicionales
for trace in st.session_state.additional_traces:
    fig.add_trace(trace)

if model_loaded or st.session_state.additional_traces:
    # Obtener el rango de los ejes para centrar el modelo
    # Este paso es importante ya que los modelos STL/GLB pueden tener rangos muy grandes.
    # Si el modelo cargado es muy grande, Plotly lo centrará automáticamente.
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X'),
            yaxis=dict(title='Y'),
            zaxis=dict(title='Z'),
            # Mantiene las proporciones del mundo real
            aspectmode='data' 
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        template='plotly_white',
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    ---
    ### Interacciones
    * **Rotación:** Clic izquierdo y arrastrar.
    * **Zoom:** Rueda del ratón.
    * **Panorámica (Mover):** Clic derecho y arrastrar.
    """)
else:
    st.warning(f"No hay modelos para mostrar. Asegúrate de que el archivo 'Earth.stl' está en la carpeta '{MODELOS_DIR}'.")

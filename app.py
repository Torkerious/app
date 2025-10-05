import streamlit as st
import numpy as np
import plotly.graph_objects as go
import trimesh # Librería para cargar y manipular modelos 3D

# --- Configuración Inicial ---
st.set_page_config(layout="wide")
st.title("Visor 3D Interactivo con Importación de Modelo 🌍")

# Inicializar o recuperar el estado de los modelos adicionales
if 'show_sphere' not in st.session_state:
    st.session_state.show_sphere = False
if 'show_cube' not in st.session_state:
    st.session_state.show_cube = False

# --- Funciones de Modelado (Ya Vistas) ---

def crear_cubo(size=10):
    """Crea un modelo 3D de un cubo usando go.Mesh3d."""
    h = size / 2.0
    x = [-h, h, -h, h, -h, h, -h, h]
    y = [-h, -h, h, h, -h, -h, h, h]
    z = [-h, -h, -h, -h, h, h, h, h]
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

    return go.Mesh3d(
        x=x, y=y, z=z, i=i, j=k, k=j, # Ajuste de índices para Plotly
        color='blue', opacity=0.8, name='Cubo Adicional'
    )

def crear_esfera(radio=5, center=(30, 0, 0)):
    """Crea un modelo 3D de una esfera usando go.Surface."""
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x = center[0] + radio * np.outer(np.cos(u), np.sin(v))
    y = center[1] + radio * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radio * np.outer(np.ones(np.size(u)), np.cos(v))
    
    return go.Surface(
        x=x, y=y, z=z,
        colorscale='Hot', showscale=False,
        opacity=0.9, name='Esfera Adicional'
    )

# --- 1. Subida y Carga del Modelo 3D ---

st.sidebar.header("Cargar Modelo Principal")
uploaded_file = st.sidebar.file_uploader(
    "Sube tu archivo 3D (.obj, .stl, .ply)",
    type=['obj', 'stl', 'ply']
)

# Inicializar la figura de Plotly
fig = go.Figure()
model_loaded = False

if uploaded_file is not None:
    try:
        # Usar trimesh para cargar el archivo binario
        with st.spinner(f"Cargando {uploaded_file.name}..."):
            # Trimesh lee el archivo en memoria
            mesh = trimesh.load_mesh(uploaded_file, file_type=uploaded_file.type)

        # Si el modelo está compuesto por múltiples partes, combinarlas
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(mesh.dump(cached=True))

        # Extraer vértices y caras (triángulos)
        vertices = mesh.vertices
        faces = mesh.faces
        
        # Crear la traza de Plotly con los datos del modelo cargado
        main_model_trace = go.Mesh3d(
            x=vertices[:, 0], 
            y=vertices[:, 1], 
            z=vertices[:, 2],
            i=faces[:, 0], 
            j=faces[:, 1], 
            k=faces[:, 2],
            color='lightgreen', 
            opacity=0.5,
            name=uploaded_file.name
        )
        fig.add_trace(main_model_trace)
        model_loaded = True
        st.sidebar.success(f"Modelo '{uploaded_file.name}' cargado con éxito.")
        
    except Exception as e:
        st.sidebar.error(f"Error al cargar el archivo 3D: {e}")
        st.stop()
else:
    st.sidebar.info("Sube un archivo 3D para comenzar la visualización.")

# --- 2. Lógica para Añadir Elementos y Configuración ---

st.sidebar.header("Añadir Elementos a la Escena")
col_b1, col_b2 = st.sidebar.columns(2)

# Botón para añadir cubo
if col_b1.button('Añadir Cubo', key='btn_cube'):
    st.session_state.show_cube = not st.session_state.show_cube

# Botón para añadir esfera
if col_b2.button('Añadir Esfera', key='btn_sphere'):
    st.session_state.show_sphere = not st.session_state.show_sphere
    
# Añadir trazas adicionales si el estado lo indica
if st.session_state.show_cube:
    fig.add_trace(crear_cubo(size=15))

if st.session_state.show_sphere:
    fig.add_trace(crear_esfera(radio=8))

# Configuración del Layout (solo si hay modelos cargados)
if model_loaded or st.session_state.show_cube or st.session_state.show_sphere:
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X'),
            yaxis=dict(title='Y'),
            zaxis=dict(title='Z'),
            aspectmode='data'  # Mantiene las proporciones reales de los datos
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        template='plotly_white',
        height=700
    )

    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

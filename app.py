import streamlit as st
import numpy as np
import plotly.graph_objects as go
import trimesh
import os # Necesario para manejar rutas de archivos

# --- Configuración Inicial ---
st.set_page_config(layout="wide")
st.title("Laboratorio 3D con Modelos Pre-cargados 🧪")

# Define la ruta a la carpeta de tus modelos
MODELOS_DIR = "modelos3d/"

# Define el archivo 3D principal que se cargará por defecto
# ¡CAMBIA ESTO POR LA RUTA DE TU ARCHIVO!
RUTA_MODELO_PRINCIPAL = os.path.join("modelos3d/tierra.glb") 
# Asegúrate de que 'tu_modelo_principal.stl' exista en la carpeta 'modelos_3d'

# Inicializar o recuperar el estado de los modelos adicionales
if 'additional_traces' not in st.session_state:
    st.session_state.additional_traces = []

# --- Funciones de Modelado ---

def crear_cubo(size=10, color='blue', center=(-15, 0, 0)):
    """Crea un cubo para añadir como elemento adicional."""
    h = size / 2.0
    x_base = np.array([-h, h, -h, h, -h, h, -h, h]) + center[0]
    y_base = np.array([-h, -h, h, h, -h, -h, h, h]) + center[1]
    z_base = np.array([-h, -h, -h, -h, h, h, h, h]) + center[2]
    
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

    return go.Mesh3d(
        x=x_base, y=y_base, z=z_base, i=i, j=k, k=j,
        color=color, opacity=0.8, name=f'Cubo {size}'
    )

def crear_esfera(radio=8, color='red', center=(15, 15, 15)):
    """Crea una esfera para añadir como elemento adicional."""
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x = center[0] + radio * np.outer(np.cos(u), np.sin(v))
    y = center[1] + radio * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radio * np.outer(np.ones(np.size(u)), np.cos(v))
    
    return go.Surface(
        x=x, y=y, z=z,
        colorscale='Hot', showscale=False,
        opacity=0.9, name=f'Esfera {radio}'
    )

def load_mesh_from_path(file_path):
    """Carga un archivo 3D y devuelve la traza go.Mesh3d."""
    file_name = os.path.basename(file_path)
    if not os.path.exists(file_path):
        st.error(f"¡ERROR! El archivo '{file_name}' no se encontró en la ruta: {file_path}")
        return None
    
    try:
        # Determinar el tipo de archivo para trimesh
        file_type = file_name.split('.')[-1]
        
        # Cargar la malla
        mesh = trimesh.load_mesh(file_path, file_type=file_type)

        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(mesh.dump(cached=True))

        # Crear la traza de Plotly
        trace = go.Mesh3d(
            x=mesh.vertices[:, 0], 
            y=mesh.vertices[:, 1], 
            z=mesh.vertices[:, 2],
            i=mesh.faces[:, 0], 
            j=mesh.faces[:, 1], 
            k=mesh.faces[:, 2],
            color='lightgray', 
            opacity=0.7,
            name=file_name,
            legendgroup='principal'
        )
        return trace
    except Exception as e:
        st.error(f"Error al procesar el archivo '{file_name}': {e}")
        return None

# --- 2. Carga del Modelo Principal (Al inicio) ---

main_trace = load_mesh_from_path(modelos3d/tierra.glb)
fig = go.Figure()

if main_trace:
    fig.add_trace(main_trace)
    st.sidebar.success(f"Modelo principal '{main_trace.name}' cargado.")
else:
    st.info("No se pudo cargar el modelo principal. Por favor, revisa la ruta y el nombre del archivo.")


# --- 3. Interfaz para Añadir Modelos de Experimentación ---

st.sidebar.header("Añadir Geometría para Experimentación")

model_options = {
    "Ninguno": None,
    "Esfera Roja (Radio 8)": "esfera",
    "Cubo Azul (Tamaño 15)": "cubo",
}

selected_model = st.sidebar.selectbox("Selecciona un elemento para añadir:", list(model_options.keys()))

# Botón para añadir el elemento
if st.sidebar.button("Añadir Elemento Seleccionado", key='add_geo'):
    if model_options[selected_model] == "esfera":
        st.session_state.additional_traces.append(crear_esfera())
    elif model_options[selected_model] == "cubo":
        st.session_state.additional_traces.append(crear_cubo())
    st.experimental_rerun() # Rerun para actualizar el gráfico inmediatamente

# Botón para limpiar
if st.sidebar.button("Limpiar Elementos Adicionales", key='clear_geo'):
    st.session_state.additional_traces = []
    st.experimental_rerun()


# --- 4. Renderizado Final ---

# Añadir todos los trazos adicionales a la figura
for trace in st.session_state.additional_traces:
    fig.add_trace(trace)

if main_trace or st.session_state.additional_traces:
    # Configuración del Layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X'),
            yaxis=dict(title='Y'),
            zaxis=dict(title='Z'),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        template='plotly_white',
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No hay modelos para mostrar. Asegúrate de que el modelo principal exista o añade un elemento.")

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Configuración Inicial ---
st.set_page_config(layout="wide")
st.title("Visor 3D Interactivo con Plotly 🧊➕⚽")

# Inicializar o recuperar el estado del modelo
if 'show_sphere' not in st.session_state:
    st.session_state.show_sphere = False

# --- 1. Definición de Modelos 3D Básicos ---

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
        x=x, y=y, z=z, i=i, j=j, k=k,
        color='blue', opacity=0.8, name='Cubo Principal'
    )

def crear_esfera(radio=5, center=(15, 15, 15)):
    """Crea un modelo 3D de una esfera usando go.Surface."""
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    
    # Coordenadas esféricas
    x = center[0] + radio * np.outer(np.cos(u), np.sin(v))
    y = center[1] + radio * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radio * np.outer(np.ones(np.size(u)), np.cos(v))
    
    return go.Surface(
        x=x, y=y, z=z,
        colorscale=[[0, 'red'], [1, 'orange']], showscale=False,
        opacity=0.9, name='Esfera Adicional'
    )

# --- 2. Creación y Configuración de la Figura ---

# 2.1 Crear figura e iniciar con el cubo
fig = go.Figure(data=[crear_cubo(size=10)])

# 2.2 Configuración del Layout (Ejes y Relación de Aspecto)
fig.update_layout(
    scene=dict(
        xaxis=dict(range=[-20, 25], title='Eje X'),
        yaxis=dict(range=[-20, 25], title='Eje Y'),
        zaxis=dict(range=[-20, 25], title='Eje Z'),
        # Asegurar que los ejes tienen igual escala para mantener la forma
        aspectmode='manual',
        aspectratio=dict(x=1, y=1, z=1) 
    ),
    margin=dict(l=0, r=0, b=0, t=30),
    template='plotly_white', # Tema claro para mejor visibilidad del cubo
    height=600
)

# --- 3. Lógica para Añadir Elementos (Botón y Estado) ---

def add_sphere_callback():
    """Función para cambiar el estado y añadir la esfera."""
    st.session_state.show_sphere = True

# Columna para el control (botón)
col1, col2 = st.columns([1, 4])
with col1:
    if st.button('Añadir Elemento (Esfera)', on_click=add_sphere_callback):
        # El callback maneja el cambio de estado
        pass

# 3.1 Condición para añadir la esfera
if st.session_state.show_sphere:
    # Añadir la nueva traza al modelo
    fig.add_trace(crear_esfera())
    with col1:
        st.success("Esfera añadida al modelo ⚽")

# --- 4. Renderizado Final en Streamlit ---

st.markdown("""
**Instrucciones:**
1. **Zoom:** Usa la rueda del ratón.
2. **Rotación:** Mantén pulsado el botón izquierdo y arrastra.
3. **Panorámica (Pan):** Mantén pulsado el botón derecho y arrastra.
""")

st.plotly_chart(fig, use_container_width=True)

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import trimesh
import os
import imageio.v2 as imageio 

# --- Configuración de Rutas de Archivo ---
MODELOS_DIR = "modelos3d"
MODELO_STL_PATH = os.path.join(MODELOS_DIR, "Earth.stl") 
TEXTURA_PATH = os.path.join(MODELOS_DIR, "earth_texture.jpg") 

# --- 1. Configuración de Streamlit y Estado ---
st.set_page_config(layout="wide")
st.title("Laboratorio 3D: Aplicación de Textura con Plotly 🎨🌎 (Final Estable)")

if 'additional_traces' not in st.session_state:
    st.session_state.additional_traces = []

# --- 2. Funciones de Modelado (Elementos de Experimentación) ---

def crear_cubo(size=10, color='blue', center=(-20, 0, 0)):
    h = size / 2.0
    x_base = np.array([-h, h, -h, h, -h, h, -h, h]) + center[0]
    y_base = np.array([-h, -h, h, h, -h, -h, h, h]) + center[1]
    z_base = np.array([-h, -h, -h, -h, h, h, h, h]) + center[2]
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]; j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]; k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    return go.Mesh3d(x=x_base, y=y_base, z=z_base, i=i, j=k, k=j, color=color, opacity=0.8, name=f'Cubo {size}')

def crear_esfera(radio=8, color='red', center=(20, 20, 20)):
    u = np.linspace(0, 2 * np.pi, 50); v = np.linspace(0, np.pi, 50)
    x = center[0] + radio * np.outer(np.cos(u), np.sin(v))
    y = center[1] + radio * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radio * np.outer(np.ones(np.size(u)), np.cos(v))
    return go.Surface(x=x, y=y, z=z, colorscale='Reds', showscale=False, opacity=0.9, name=f'Esfera {radio}')

# --- 3. Función de Carga del Modelo STL con Textura Aplicada (Alternativa) ---

def load_stl_with_texture_for_plotly(stl_path, texture_path):
    """Carga STL, aplica la textura y devuelve la traza Plotly."""
    if not os.path.exists(stl_path):
        st.error(f"❌ ¡ERROR! El archivo STL '{stl_path}' no se encontró.")
        return None
    
    if not os.path.exists(texture_path):
        st.error(f"❌ ¡ERROR! El archivo de textura '{texture_path}' no se encontró.")
        return None
    
    try:
        with st.spinner(f"Cargando {os.path.basename(stl_path)} y aplicando textura..."):
            mesh = trimesh.load_mesh(stl_path)
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(mesh.dump(cached=True))

            # 1. Leer la imagen de textura
            image = imageio.imread(texture_path)

            # 2. Asignar la textura al objeto visual (Método más directo y fundamental)
            # Esto requiere que el STL tenga coordenadas UV válidas (lo cual es raro en STL, pero necesario para mapear)
            # Si el STL no tiene UVs, Trimesh intentará generarlos, lo cual puede fallar.
            mesh.visual = trimesh.visual.TextureVisuals(image=image)

            # 3. Forzar el cálculo de los colores de los vértices (si el mapeo fue exitoso)
            # Intentar acceder a los colores de los vértices calculados por Trimesh
            if hasattr(mesh.visual, 'vertex_colors') and mesh.visual.vertex_colors is not None:
                vertex_colors_int = mesh.visual.vertex_colors
            else:
                # Fallback: Si no hay colores de vértice, usar un color plano
                st.warning("⚠️ El modelo STL no contenía coordenadas UV válidas o Trimesh no pudo generarlas. Se mostrará un color sólido.")
                colors_hex = None 
                color_plano = 'lightblue'

            if 'colors_hex' not in locals():
                # Convertir el color [R, G, B, A] a '#RRGGBB'
                colors_hex = ['#%02x%02x%02x' % tuple(c[:3]) for c in vertex_colors_int]
                color_plano = None
            
            # 4. Crear la traza de Plotly
            trace = go.Mesh3d(
                x=mesh.vertices[:, 0], 
                y=mesh.vertices[:, 1], 
                z=mesh.vertices[:, 2],
                i=mesh.faces[:, 0], 
                j=mesh.faces[:, 1], 
                k=mesh.faces[:, 2],
                vertexcolor=colors_hex, 
                color=color_plano, # Se usa si vertexcolor es None (el fallback)
                opacity=1.0,
                name="Earth con Textura",
            )
        return trace
    except Exception as e:
        st.error(f"❌ Error interno al aplicar la textura: {e}")
        st.info("La aplicación de textura a un STL sin UVs es difícil. Intenta actualizar `trimesh` o usar un archivo con UVs.")
        return None

# --- 4. Carga del Modelo Principal y Creación de la Figura ---
# (El resto del código de la aplicación permanece igual)
main_trace = load_stl_with_texture_for_plotly(MODELO_STL_PATH, TEXTURA_PATH)
fig = go.Figure()
model_loaded = False

if main_trace:
    fig.add_trace(main_trace)
    st.sidebar.success("Modelo Earth.stl cargado con textura.")
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
    st.experimental_rerun() 

if col_b2.button("Limpiar Adicionales", key='clear_geo'):
    st.session_state.additional_traces = []
    st.experimental_rerun()

# --- 6. Renderizado Final ---

for trace in st.session_state.additional_traces:
    fig.add_trace(trace)

if model_loaded or st.session_state.additional_traces:
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
    
    st.markdown("""
    ---
    ### Interacciones
    * **Rotación:** Clic izquierdo y arrastrar.
    * **Zoom:** Rueda del ratón.
    * **Panorámica (Mover):** Clic derecho y arrastrar.
    """)

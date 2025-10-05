import streamlit as st
import numpy as np
import plotly.graph_objects as go
from PIL import Image

# --- Configuración Inicial ---
st.set_page_config(layout="wide")

# Cargar imagen de textura (asegúrate de que "earth_texture.jpg" esté en el mismo directorio)
try:
    # Redimensionar la imagen para que coincida con las dimensiones de la malla (200x100)
    img = Image.open("earth_texture.jpg").resize((200, 100))
    img_array = np.array(img) / 255.0

    # Invertir verticalmente la imagen para una orientación correcta en Plotly
    img_array = np.flipud(img_array)

    # Calcular el valor de color/brillo promedio para usar como surfacecolor
    # Se toma el promedio de los canales RGB (los 3 primeros)
    surfacecolor = np.mean(img_array[:, :, :3], axis=2)

    # Asegurarse de que surfacecolor tenga la forma correcta (100 filas, 200 columnas)
    # que es la misma que la de las coordenadas (theta.shape[0], phi.shape[1])
    surfacecolor = surfacecolor[:100, :200]

except FileNotFoundError:
    st.error("Error: No se encontró el archivo 'earth_texture.jpg'. Asegúrate de que esté en la misma carpeta.")
    st.stop()
except Exception as e:
    st.error(f"Ocurrió un error al cargar o procesar la imagen: {e}")
    st.stop()


# --- Coordenadas Esféricas de la Tierra ---
# Malla para la esfera
num_theta = 100
num_phi = 200
theta = np.linspace(0, np.pi, num_theta)
phi = np.linspace(0, 2 * np.pi, num_phi)
theta, phi = np.meshgrid(theta, phi)
r = 8000  # Radio visualizado de la Tierra

# Coordenadas cartesianas
xe = r * np.sin(theta) * np.cos(phi)
ye = r * np.sin(theta) * np.sin(phi)
ze = r * np.cos(theta)


# --- Crear Figura de Plotly ---
fig = go.Figure()

# **PASO CLAVE: AGREGAR LA TRAZA ANTES DE LLAMAR A st.plotly_chart**
fig.add_trace(go.Surface(
    x=xe, y=ye, z=ze,
    surfacecolor=surfacecolor,
    # El colorscale se usa para mapear valores a colores,
    # pero surfacecolor ya contiene los valores de brillo/color.
    # Usar 'Earth' aquí podría no ser la mejor idea si quieres la textura real,
    # pero lo mantengo por si Plotly requiere uno.
    # Nota: para color RGB verdadero, se usaría go.Mesh3d o go.Surface con surfacecolor
    # ajustado y mapeado a un colorscale apropiado, o usando el módulo `plotly.express`.
    # Para este enfoque, surfacecolor debe ser una matriz 2D de valores de brillo.
    colorscale='Earth', # Se usa un colorscale para mapear los valores de brillo (0 a 1)
    cmin=0, cmax=1,
    showscale=False,
    name='Tierra'
))

# --- Configuración del Diseño (Layout) ---
fig.update_layout(
    title='Modelo Esférico de la Tierra',
    scene=dict(
        xaxis=dict(range=[-9000, 9000], backgroundcolor="black", gridcolor="white"),
        yaxis=dict(range=[-9000, 9000], backgroundcolor="black", gridcolor="white"),
        zaxis=dict(range=[-9000, 9000], backgroundcolor="black", gridcolor="white"),
        aspectmode='manual',
        aspectratio=dict(x=1, y=1, z=1)
    ),
    margin=dict(l=0, r=0, b=0, t=30),
    template='plotly_dark' # Usar un tema oscuro
)

# --- Mostrar en Streamlit ---
st.header("Visualización 3D de la Tierra 🌎")

# Mostrar las formas para depuración
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Dimensiones del Modelo")
    st.write("x shape:", xe.shape)
    st.write("y shape:", ye.shape)
    st.write("z shape:", ze.shape)
with col2:
    st.markdown("### Textura")
    st.write("surfacecolor shape:", surfacecolor.shape)
    st.write(f"surfacecolor min/max: **{surfacecolor.min():.2f}** / **{surfacecolor.max():.2f}**")
    st.image(img, caption="Textura cargada (Redimensionada a 200x100)", use_column_width=True)

st.plotly_chart(fig, use_container_width=True) # Solo una llamada es suficiente

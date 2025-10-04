from PIL import Image
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(layout="wide")
st.title("🌍 Tierra con Textura Simulada Mejorada")

# Cargar imagen y ajustar orientación
img = Image.open("earth_texture.jpg").resize((100, 50))
img_array = np.array(img) / 255.0
img_array = np.flipud(img_array)  # Invertir vertical

# Usar canal azul como mapa de color
surfacecolor = img_array[:, :, 2].T  # Transponer para que coincida

# Coordenadas esféricas
theta = np.linspace(0, np.pi, surfacecolor.shape[0])
phi = np.linspace(0, 2 * np.pi, surfacecolor.shape[1])
theta, phi = np.meshgrid(theta, phi)
r = 6371

x = r * np.sin(theta) * np.cos(phi)
y = r * np.sin(theta) * np.sin(phi)
z = r * np.cos(theta)

# Visualización
fig = go.Figure(data=[go.Surface(
    x=x, y=y, z=z,
    surfacecolor=surfacecolor,
    colorscale='Blues',
    cmin=0, cmax=1,
    showscale=False
)])

fig.update_layout(
    title='🌍 Tierra con Textura Simulada Mejorada',
    scene=dict(
        xaxis_title='X (km)',
        yaxis_title='Y (km)',
        zaxis_title='Z (km)',
        aspectmode='data'
    )
)

st.plotly_chart(fig, use_container_width=True)

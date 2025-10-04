import streamlit as st
import numpy as np
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(layout="wide")
st.title("🌍 Modelo 3D de la Tierra con Textura Simulada")

# Cargar imagen de textura
img = Image.open("earth_texture.jpg").resize((100, 50))
img = np.array(img) / 255.0  # Normalizar

# Coordenadas esféricas
theta = np.linspace(0, np.pi, img.shape[0])
phi = np.linspace(0, 2 * np.pi, img.shape[1])
theta, phi = np.meshgrid(theta, phi)
r = 6371

x = r * np.sin(theta) * np.cos(phi)
y = r * np.sin(theta) * np.sin(phi)
z = r * np.cos(theta)

# Simular textura con promedio de RGB
surfacecolor = np.mean(img, axis=2).T  # Transponer para que coincida

fig = go.Figure(data=[go.Surface(
    x=x, y=y, z=z,
    surfacecolor=surfacecolor,
    colorscale='Earth',  # Usa una escala de color parecida
    cmin=0, cmax=1,
    showscale=False
)])

fig.update_layout(
    title='🌍 Tierra con Textura Simulada',
    scene=dict(
        xaxis_title='X (km)',
        yaxis_title='Y (km)',
        zaxis_title='Z (km)',
        aspectmode='data'
    )
)

st.plotly_chart(fig, use_container_width=True)

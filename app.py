import streamlit as st
import numpy as np
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(layout="wide")
st.title("🌍 Modelo 3D de la Tierra con Textura")

# Cargar textura
texture = Image.open("earth_texture.jpg")
texture = np.array(texture.resize((100, 50))) / 255.0  # Normalizar

# Coordenadas esféricas
theta = np.linspace(0, np.pi, 50)
phi = np.linspace(0, 2 * np.pi, 100)
theta, phi = np.meshgrid(theta, phi)
r = 6371

x = r * np.sin(theta) * np.cos(phi)
y = r * np.sin(theta) * np.sin(phi)
z = r * np.cos(theta)

# Mapear textura como colores
colors = texture[:, :, :3]  # RGB
colors = np.flipud(colors)  # Invertir vertical para que coincida

# Convertir a escala de color Plotly
surfacecolor = np.mean(colors, axis=2)

fig = go.Figure(data=[go.Surface(
    x=x, y=y, z=z,
    surfacecolor=surfacecolor,
    colorscale='gray',
    cmin=0, cmax=1,
    showscale=False,
    opacity=1.0
)])

fig.update_layout(
    title='🌍 Tierra con Textura Realista',
    scene=dict(
        xaxis_title='X (km)',
        yaxis_title='Y (km)',
        zaxis_title='Z (km)',
        aspectmode='data'
    )
)

st.plotly_chart(fig, use_container_width=True)

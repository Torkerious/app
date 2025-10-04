import streamlit as st
import numpy as np
import plotly.graph_objects as go
from PIL import Image  # ← esta línea es clave
# Cargar textura de alta resolución
img = Image.open("earth_texture.jpg").resize((200, 100))
img_array = np.array(img) / 255.0
img_array = np.flipud(img_array)  # Invertir vertical
surfacecolor = np.mean(img_array[:, :, :3], axis=2).T  # Promedio RGB

# Coordenadas esféricas
theta = np.linspace(0, np.pi, surfacecolor.shape[0])
phi = np.linspace(0, 2 * np.pi, surfacecolor.shape[1])
theta, phi = np.meshgrid(theta, phi)
r = 8000  # Aumentar radio para que se vea más grande

xe = r * np.sin(theta) * np.cos(phi)
ye = r * np.sin(theta) * np.sin(phi)
ze = r * np.cos(theta)

st.write("x shape:", x.shape)
st.write("y shape:", y.shape)
st.write("z shape:", z.shape)
st.write("surfacecolor shape:", surfacecolor.shape)
# Visualización de la Tierra
fig.add_trace(go.Surface(
    x=xe, y=ye, z=ze,
    surfacecolor=surfacecolor,
    colorscale='Earth',
    cmin=0, cmax=1,
    showscale=False,
    name='Tierra'
))

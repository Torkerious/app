import streamlit as st
import numpy as np
import plotly.graph_objects as go
from PIL import Image  # ← esta línea es clave
# Cargar textura de alta resolución

# Ajustar surfacecolor para que coincida con x, y, z
from scipy.ndimage import zoom

img = Image.open("earth_texture.jpg").resize((200, 100))
img_array = np.array(img) / 255.0
img_array = np.flipud(img_array)  # Invertir vertical
surfacecolor = np.mean(img_array[:, :, :3], axis=2).T  # Promedio RGB

# Escalar surfacecolor a (200, 100)
surfacecolor = zoom(surfacecolor, (2, 1))  # duplica filas, mantiene columnas

# Verifica forma final
#st.write("surfacecolor ajustado:", surfacecolor.shape)

img = Image.open("earth_texture.jpg").resize((200, 100))
img_array = np.array(img) / 255.0
img_array = np.flipud(img_array)  # Invertir vertical
surfacecolor = np.mean(img_array[:, :, :3], axis=2).T  # Promedio RGB

# Coordenadas esféricas
theta = np.linspace(0, np.pi, 100)
phi = np.linspace(0, 2 * np.pi, 200)
theta, phi = np.meshgrid(theta, phi)
r = 8000

x = r * np.sin(theta) * np.cos(phi)
y = r * np.sin(theta) * np.sin(phi)
z = r * np.cos(theta)

# Cargar imagen y ajustar
img = Image.open("earth_texture.jpg").resize((200, 100))
img_array = np.array(img) / 255.0
img_array = np.flipud(img_array)
surfacecolor = np.mean(img_array[:, :, :3], axis=2)

# Asegurar que surfacecolor tenga la misma forma que x, y, z
surfacecolor = surfacecolor[:theta.shape[0], :theta.shape[1]]

# Coordenadas esféricas para la Tierra
theta = np.linspace(0, np.pi, 100)
phi = np.linspace(0, 2 * np.pi, 200)
theta, phi = np.meshgrid(theta, phi)
r = 8000  # Radio visualizado de la Tierra

xe = r * np.sin(theta) * np.cos(phi)
ye = r * np.sin(theta) * np.sin(phi)
ze = r * np.cos(theta)


fig = go.Figure()

#st.write("x shape:", xe.shape)
#st.write("y shape:", ye.shape)
#st.write("z shape:", ze.shape)
#st.write("surfacecolor shape:", surfacecolor.shape)
#st.image(img, caption="Textura cargada")
#st.plotly_chart(fig, use_container_width=True)
# Visualización de la Tierra
fig.add_trace(go.Surface(
    x=xe, y=ye, z=ze,
    surfacecolor=surfacecolor,
    colorscale='Earth',
    cmin=0, cmax=1,
    showscale=False,
    name='Tierra'
))
st.plotly_chart(fig, use_container_width=True, key ='tierra1')
st.plotly_chart(fig, use_container_width=True, key ='tierra2')

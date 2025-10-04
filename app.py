import streamlit as st
import numpy as np
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(layout="wide")
st.title("☄️ Simulador Orbital con Tierra y Luna")

# Parámetros del usuario
st.sidebar.header("Asteroide")
diametro = st.sidebar.slider("Diámetro (m)", 10, 10000, 500)
velocidad = st.sidebar.slider("Velocidad inicial (km/s)", 1, 70, 30)
angulo = st.sidebar.slider("Ángulo de entrada (°)", 0, 90, 45)

# Constantes físicas
G = 6.67430e-20  # km^3/kg/s^2
M_tierra = 5.972e24  # kg
M_luna = 7.348e22    # kg
R_tierra = 6371      # km
R_luna = 1737        # km
pos_tierra = np.array([0, 0, 0])
pos_luna = np.array([384400, 0, 0])  # km

# Estado inicial
pos = np.array([0.01 * 149597870.7, 0, 0])  # 0.01 AU
angle_rad = np.radians(angulo)
vel = np.array([
    -velocidad * np.cos(angle_rad),
    0,
    -velocidad * np.sin(angle_rad)
])

# Simulación paso a paso
dt = 60  # segundos
steps = 180
positions = []

for _ in range(steps):
    # Vector hacia Tierra
    r_t = pos - pos_tierra
    dist_t = np.linalg.norm(r_t)
    a_t = -G * M_tierra / dist_t**3 * r_t

    # Vector hacia Luna
    r_l = pos - pos_luna
    dist_l = np.linalg.norm(r_l)
    a_l = -G * M_luna / dist_l**3 * r_l

    # Aceleración total
    acc = a_t + a_l

    # Integración (Euler)
    vel += acc * dt
    pos += vel * dt
    positions.append(pos.copy())

positions = np.array(positions)
x, y, z = positions[:,0], positions[:,1], positions[:,2]

# Cargar textura simulada
img = Image.open("earth_texture.jpg").resize((100, 50))
img_array = np.array(img) / 255.0
img_array = np.flipud(img_array)
surfacecolor = img_array[:, :, 2].T

# Coordenadas esféricas
theta = np.linspace(0, np.pi, surfacecolor.shape[0])
phi = np.linspace(0, 2 * np.pi, surfacecolor.shape[1])
theta, phi = np.meshgrid(theta, phi)

# Tierra
xe = R_tierra * np.sin(theta) * np.cos(phi)
ye = R_tierra * np.sin(theta) * np.sin(phi)
ze = R_tierra * np.cos(theta)

# Luna
xl = R_luna * np.sin(theta) * np.cos(phi) + pos_luna[0]
yl = R_luna * np.sin(theta) * np.sin(phi)
zl = R_luna * np.cos(theta)

# Visualización
fig = go.Figure()

fig.add_trace(go.Surface(
    x=xe, y=ye, z=ze,
    surfacecolor=surfacecolor,
    colorscale='Blues',
    cmin=0, cmax=1,
    showscale=False,
    name='Tierra'
))

fig.add_trace(go.Surface(
    x=xl, y=yl, z=zl,
    colorscale='Greys',
    opacity=0.5,
    showscale=False,
    name='Luna'
))

fig.add_trace(go.Scatter3d(
    x=x, y=y, z=z,
    mode='lines+markers',
    line=dict(color='orange', width=4),
    marker=dict(size=3, color='red'),
    name='Trayectoria Asteroide'
))

impact_index = np.argmin(np.linalg.norm(positions, axis=1))
impact_x, impact_y, impact_z = positions[impact_index]
fig.add_trace(go.Scatter3d(
    x=[impact_x], y=[impact_y], z=[impact_z],
    mode='markers',
    marker=dict(size=8, color='yellow'),
    name='Impacto'
))

fig.update_layout(
    title='Trayectoria Curvada con Influencia Lunar',
    scene=dict(
        xaxis_title='X (km)',
        yaxis_title='Y (km)',
        zaxis_title='Z (km)',
        aspectmode='data'
    ),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

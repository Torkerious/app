import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("☄️ Simulador de Impacto con Influencia Lunar")

# Parámetros del usuario
st.sidebar.header("Parámetros del Asteroide")
diametro = st.sidebar.slider("Diámetro (m)", 10, 10000, 500)
velocidad = st.sidebar.slider("Velocidad (km/s)", 1, 70, 30)
angulo = st.sidebar.slider("Ángulo de impacto (°)", 0, 90, 45)
distancia_luna = st.sidebar.slider("Distancia mínima a la Luna (km)", 10000, 400000, 50000)

# Constantes
AU_KM = 149597870.7
R_TIERRA = 6371
R_LUNA = 1737
DIST_TIERRA_LUNA = 384400

# Posiciones iniciales
initial_pos = np.array([0.01 * AU_KM, 0, 0])
angle_rad = np.radians(angulo)
v_vector = np.array([
    -velocidad * np.cos(angle_rad),
    0,
    -velocidad * np.sin(angle_rad)
])

# Trayectoria con perturbación lunar
positions = []
for i in range(180):
    t = i * 60
    pos = initial_pos + v_vector * t

    # Simular desviación gravitacional si cerca de la Luna
    luna_pos = np.array([DIST_TIERRA_LUNA, 0, 0])
    dist_to_luna = np.linalg.norm(pos - luna_pos)
    if dist_to_luna < distancia_luna:
        desviacion = 0.0001 * (distancia_luna - dist_to_luna)
        pos[1] += desviacion * 1e4  # desviación lateral

    positions.append(pos)

positions = np.array(positions)
x, y, z = positions[:,0], positions[:,1], positions[:,2]

# Esfera Tierra
theta, phi = np.meshgrid(np.linspace(0, np.pi, 50), np.linspace(0, 2*np.pi, 50))
xe = R_TIERRA * np.sin(theta) * np.cos(phi)
ye = R_TIERRA * np.sin(theta) * np.sin(phi)
ze = R_TIERRA * np.cos(theta)

# Esfera Luna
xl = R_LUNA * np.sin(theta) * np.cos(phi) + DIST_TIERRA_LUNA
yl = R_LUNA * np.sin(theta) * np.sin(phi)
zl = R_LUNA * np.cos(theta)

# Visualización
fig = go.Figure()

# Tierra
fig.add_trace(go.Surface(x=xe, y=ye, z=ze, colorscale='Blues', opacity=0.6, showscale=False, name='Tierra'))

# Luna
fig.add_trace(go.Surface(x=xl, y=yl, z=zl, colorscale='Greys', opacity=0.5, showscale=False, name='Luna'))

# Trayectoria
fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines+markers',
    line=dict(color='orange', width=4),
    marker=dict(size=3, color='red'),
    name='Trayectoria Asteroide'))

# Impacto
impact_index = np.argmin(np.linalg.norm(positions, axis=1))
impact_x, impact_y, impact_z = positions[impact_index]
fig.add_trace(go.Scatter3d(x=[impact_x], y=[impact_y], z=[impact_z],
    mode='markers',
    marker=dict(size=8, color='yellow'),
    name='Impacto'))

fig.update_layout(
    title='Trayectoria del Asteroide con Influencia Lunar',
    scene=dict(
        xaxis_title='X (km)',
        yaxis_title='Y (km)',
        zaxis_title='Z (km)',
        aspectmode='data'
    ),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

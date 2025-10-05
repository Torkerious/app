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



import numpy as np

# --- 1. Constantes Físicas ---
G = 6.674e-11  # Constante Gravitacional (No se usa directamente aquí, solo para referencia)
g = 9.81       # Aceleración de la gravedad (m/s^2)
DENSIDAD_ASTEROIDE = 3000  # Densidad típica de asteroide rocoso (kg/m^3)
DENSIDAD_ROCA = 2700       # Densidad de la corteza (kg/m^3)
DENSIDAD_BLANDA = 1800     # Densidad de suelo blando/sedimento (kg/m^3)
DENSIDAD_AGUA = 1000       # Densidad del agua (kg/m^3)

# --- 2. Parámetros del Asteroide (EJEMPLO) ---
radio_ast = 50.0  # Radio del asteroide (m). Diámetro total = 100m.
vel_impacto = 20000.0  # Velocidad de impacto típica (m/s), o 20 km/s.

# --- 3. Cálculo de la Energía Cinética ---
def calcular_energia(radio, velocidad, densidad_ast):
    """Calcula la masa y la energía cinética del asteroide."""
    volumen = (4/3) * np.pi * (radio**3)
    masa = densidad_ast * volumen
    # E_k = 0.5 * m * v^2
    energia_joules = 0.5 * masa * (velocidad**2)
    # Convertir a Megatones de TNT para mejor comprensión (1 Mt = 4.184e15 J)
    energia_megatones = energia_joules / 4.184e15
    return masa, energia_joules, energia_megatones

masa_ast, ek_joules, ek_megatones = calcular_energia(radio_ast, vel_impacto, DENSIDAD_ASTEROIDE)

# --- 4. Modelos Empíricos de Escalamiento ---

def impacto_roca_dura(ek):
    """Estima el diámetro del cráter en roca dura."""
    # K ~ 0.1, usando la fórmula de escalamiento
    K = 0.1
    # La fórmula es D_crater = K * (E_k / (rho * g))^(1/4)
    denominador = DENSIDAD_ROCA * g
    diametro_m = K * (ek / denominador)**(1/4)
    # Profundidad típica es ~1/5 del diámetro
    profundidad_m = diametro_m / 5
    return diametro_m, profundidad_m

def impacto_tierra_blanda(diam_roca, prof_roca):
    """Estima el cráter en tierra blanda/sedimentos (escalado empíricamente)."""
    # Se asume un cráter 15% más ancho y 30% menos profundo que en roca
    diam_blanda = diam_roca * 1.15
    prof_blanda = prof_roca * 0.70
    return diam_blanda, prof_blanda

def impacto_agua(ek, radio_ast):
    """Estima la altura inicial de la columna de agua (H) en el punto de impacto."""
    # Fórmula: H_agua ~ C * (E_k / (rho * g))^(1/3) * (1/R)
    C = 0.1
    denominador = DENSIDAD_AGUA * g
    # Calcular radio del hemisferio de agua desplazada (similar al "radio del cráter" virtual)
    radio_desplazamiento = C * (ek / denominador)**(1/3)
    
    # La altura real de la columna de agua cerca del impacto es compleja,
    # Simplificamos asumiendo una relación directa con la energía de desplazamiento y el radio del asteroide.
    # Esta es una gran simplificación del fenómeno real de tsunami.
    altura_inicial_m = radio_desplazamiento * 2 / radio_ast  # Factor de escalamiento simple
    return altura_inicial_m


# --- 5. Ejecutar y Mostrar Resultados ---

# Cálculos Base
diam_roca, prof_roca = impacto_roca_dura(ek_joules)
diam_blanda, prof_blanda = impacto_tierra_blanda(diam_roca, prof_roca)
alt_agua_inicial = impacto_agua(ek_joules, radio_ast)

st.title("Impacto de Asteroide: Simulación Empírica ☄️")

st.markdown(f"""
El asteroide de **{radio_ast*2:.0f} metros de diámetro** y **{masa_ast/1e9:.2f} mil millones de kg** impacta a **{vel_impacto/1000:.0f} km/s**.

Esta energía se traduce en **{ek_megatones:.2f} Megatones** de TNT (varias veces más potente que la bomba más grande jamás probada).
""")

## Escenario 1: Impacto en Roca Dura ⛰️
st.header("Escenario 1: Impacto en Roca Dura")
st.markdown(f"""
* **Diámetro del Cráter Estimado:** **{diam_roca/1000:.2f} km**
* **Profundidad del Cráter Estimada:** **{prof_roca/1000:.2f} km**
* **Efecto Primario:** Enorme onda de choque, explosión y terremoto. La eyección de material rocoso (vaporizado) a la atmósfera es máxima, contribuyendo a un potencial **invierno de impacto**.
""")

## Escenario 2: Impacto en Tierra Blanda/Sedimento 🏜️
st.header("Escenario 2: Impacto en Tierra Blanda/Sedimento")
st.markdown(f"""
* **Diámetro del Cráter Estimado:** **{diam_blanda/1000:.2f} km** (más ancho que en roca)
* **Profundidad del Cráter Estimada:** **{prof_blanda/1000:.2f} km** (menos profundo que en roca)
* **Efecto Primario:** Similar a la roca, pero el cráter es menos definido y se genera más **vapor de agua o gases volátiles** (como CO₂) si el suelo es rico en ellos, con mayor riesgo de afectar al clima a largo plazo.
""")

## Escenario 3: Impacto en Océano Profundo 🌊
st.header("Escenario 3: Impacto en Océano Profundo")
st.markdown(f"""
* **Altura Inicial de la Columna de Agua:** **{alt_agua_inicial:.0f} metros**
* **Efecto Primario:**
    * No hay cráter permanente.
    * Generación de un **enorme tsunami** (que se reduce con la distancia) y una columna masiva de vapor de agua.
    * La inyección de **vapor de agua** a la atmósfera superior es el mayor riesgo global, actuando como un potente gas de efecto invernadero y alterando el clima.
""")

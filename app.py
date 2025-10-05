# app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Circle, Rectangle, Polygon, Ellipse
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import time
from PIL import Image
import io
import os

# --- Page config ---
st.set_page_config(
    page_title="Impact Simulator - China",
    page_icon="🗺️",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .city-description {
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 3px solid #4A90E2;
    }
    .impact-warning {
        background: linear-gradient(45deg, #ff4444, #ff6b6b);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #ff0000;
        font-size: 1.1rem;
    }
    .mitigation-success {
        background: linear-gradient(45deg, #44ff44, #66ff66);
        color: black;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #00ff00;
        font-size: 1.1rem;
    }
    .energy-section {
        background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        border: 3px solid #ff4757;
    }
    .energy-metric {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .district-card {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #f1c40f;
    }
    .results-table {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<h1 class="main-header">Impact Simulator - China</h1>', unsafe_allow_html=True)

# Asset file expected in the project directory
MAPA_CHINA_FILE = "mapa_china.png"

# --- Provinces population (thousands) ---
poblacion_china = {
    'guangdong': {
        'nombre': 'Guangdong',
        'poblacion': 126012,  # thousands (126M)
        'coordenadas': {'x_min': 80, 'x_max': 95, 'y_min': 15, 'y_max': 25},
        'descripcion': 'Most populous province in China'
    },
    'shandong': {
        'nombre': 'Shandong',
        'poblacion': 101527,
        'coordenadas': {'x_min': 90, 'x_max': 105, 'y_min': 25, 'y_max': 35},
        'descripcion': 'Eastern coastal province'
    },
    'henan': {
        'nombre': 'Henan',
        'poblacion': 99365,
        'coordenadas': {'x_min': 75, 'x_max': 90, 'y_min': 25, 'y_max': 35},
        'descripcion': 'Heart of Central China'
    },
    'jiangsu': {
        'nombre': 'Jiangsu',
        'poblacion': 84748,
        'coordenadas': {'x_min': 95, 'x_max': 110, 'y_min': 10, 'y_max': 20},
        'descripcion': 'Developed economic zone'
    },
    'sichuan': {
        'nombre': 'Sichuan',
        'poblacion': 83675,
        'coordenadas': {'x_min': 55, 'x_max': 75, 'y_min': 20, 'y_max': 35},
        'descripcion': 'Southwestern province'
    },
    'hebei': {
        'nombre': 'Hebei',
        'poblacion': 75919,
        'coordenadas': {'x_min': 80, 'x_max': 95, 'y_min': 40, 'y_max': 50},
        'descripcion': 'Surrounds Beijing'
    },
    'hunan': {
        'nombre': 'Hunan',
        'poblacion': 69185,
        'coordenadas': {'x_min': 70, 'x_max': 85, 'y_min': 20, 'y_max': 30},
        'descripcion': 'Central province'
    },
    'anhui': {
        'nombre': 'Anhui',
        'poblacion': 63236,
        'coordenadas': {'x_min': 90, 'x_max': 105, 'y_min': 10, 'y_max': 20},
        'descripcion': 'Eastern China'
    },
    'hubei': {
        'nombre': 'Hubei',
        'poblacion': 59172,
        'coordenadas': {'x_min': 75, 'x_max': 90, 'y_min': 20, 'y_max': 30},
        'descripcion': 'Central China'
    },
    'zhejiang': {
        'nombre': 'Zhejiang',
        'poblacion': 58500,
        'coordenadas': {'x_min': 100, 'x_max': 115, 'y_min': 30, 'y_max': 40},
        'descripcion': 'Developed east coast'
    }
}

# --- Critical points (labels in English) ---
puntos_criticos_china = {
    'beijing': {'x': 92, 'y': 45, 'nombre': 'Beijing', 'tipo': 'capital'},
    'shanghai': {'x': 102, 'y': 28, 'nombre': 'Shanghai', 'tipo': 'economic'},
    'guangzhou': {'x': 87, 'y': 20, 'nombre': 'Guangzhou', 'tipo': 'economic'},
    'shenzhen': {'x': 90, 'y': 18, 'nombre': 'Shenzhen', 'tipo': 'technology'},
    'wuhan': {'x': 82, 'y': 30, 'nombre': 'Wuhan', 'tipo': 'industrial'},
    'xian': {'x': 70, 'y': 38, 'nombre': "Xi'an", 'tipo': 'cultural'}
}

def load_china_image() -> Image.Image:
    """Load China map image or fallback to a generated sketch (user-facing messages in English)."""
    try:
        if os.path.exists(MAPA_CHINA_FILE):
            imagen_china = Image.open(MAPA_CHINA_FILE)
            st.success(f"China map loaded: {MAPA_CHINA_FILE}")
            return imagen_china
        else:
            st.warning(f"File {MAPA_CHINA_FILE} not found. Using a fallback map.")
            return generate_fallback_map()
    except Exception as e:
        st.error(f"Error loading China map: {e}")
        return generate_fallback_map()

def generate_fallback_map() -> Image.Image:
    """Generate a simplified China-like map as an image (why: ensures app works without external asset)."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_facecolor('#1a1a2e')

    china_outline = np.array([
        [50, 10], [60, 15], [70, 20], [80, 25], [90, 30], [100, 35],
        [110, 30], [115, 25], [120, 20], [115, 15], [105, 10],
        [95, 5], [85, 10], [75, 15], [65, 20], [55, 15], [50, 10]
    ])

    polygon = Polygon(china_outline, closed=True, facecolor='#2c3e50',
                      edgecolor='white', alpha=0.8, linewidth=2)
    ax.add_patch(polygon)

    # Rivers (decorative)
    ax.plot([65, 85, 100], [35, 30, 25], 'b-', linewidth=3, alpha=0.6, label='Yangtze River')
    ax.plot([55, 75, 90], [40, 35, 30], 'b-', linewidth=2, alpha=0.6, label='Yellow River')

    ax.set_xlim(50, 120)
    ax.set_ylim(5, 45)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('China Map - Impact Simulator', fontsize=16, color='white', pad=20)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    return Image.open(buf)

def create_meteor(size: float) -> io.BytesIO:
    """Create a small meteor image with gradient (why: better visual cue)."""
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.add_patch(Circle((0.5, 0.5), 0.4, facecolor='#2F4F4F', edgecolor='#000000', linewidth=2, alpha=0.9))
    ax.add_patch(Circle((0.5, 0.5), 0.3, facecolor='#654321', edgecolor='none', alpha=0.8))
    ax.add_patch(Circle((0.5, 0.5), 0.2, facecolor='#8B4500', edgecolor='none', alpha=0.9))
    ax.add_patch(Circle((0.5, 0.5), 0.1, facecolor='#8B0000', edgecolor='none', alpha=1.0))
    ax.add_patch(Circle((0.35, 0.35), 0.05, facecolor='#FF4500', alpha=0.7))
    for i in range(3):
        ax.add_patch(Ellipse((0.8 - i*0.1, 0.5), 0.15, 0.08, angle=30, facecolor='#FF8C00', alpha=0.4 - i*0.1))

    ax.set_aspect('equal')
    ax.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0,
                facecolor='none', transparent=True)
    buf.seek(0)
    plt.close(fig)
    return buf

def create_china_map(imagen_china: Image.Image, show_meteor: bool=False,
                     impact_pos: tuple|None=None, meteor_size: float=1.0):
    """Draw provinces, critical points, and optional meteor."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(imagen_china, extent=[50, 120, 5, 45], alpha=0.8)

    for provincia_id, provincia in poblacion_china.items():
        coords = provincia['coordenadas']
        ancho = coords['x_max'] - coords['x_min']
        alto = coords['y_max'] - coords['y_min']

        poblacion = provincia['poblacion']
        if poblacion > 100000:
            color, alpha = '#e74c3c', 0.4
        elif poblacion > 80000:
            color, alpha = '#e67e22', 0.35
        elif poblacion > 60000:
            color, alpha = '#f1c40f', 0.3
        else:
            color, alpha = '#27ae60', 0.25

        rect = Rectangle((coords['x_min'], coords['y_min']), ancho, alto,
                         facecolor=color, alpha=alpha, edgecolor=color, linewidth=2)
        ax.add_patch(rect)

        cx = (coords['x_min'] + coords['x_max']) / 2
        cy = (coords['y_min'] + coords['y_max']) / 2

        ax.text(cx, cy,
                f"{provincia['nombre']}\n{provincia['poblacion']:,} thousand",
                ha='center', va='center', fontsize=7, weight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))

    for punto_id, punto in puntos_criticos_china.items():
        if punto['tipo'] == 'capital':
            marker, color = 's', 'red'
        elif punto['tipo'] == 'economic':
            marker, color = 'o', 'blue'
        elif punto['tipo'] == 'technology':
            marker, color = 'D', 'green'
        elif punto['tipo'] == 'industrial':
            marker, color = '^', 'orange'
        else:
            marker, color = 'v', 'purple'

        ax.plot(punto['x'], punto['y'], marker=marker, color=color,
                markersize=10, markeredgecolor='white', linewidth=2)
        ax.text(punto['x'], punto['y'] + 2, punto['nombre'],
                ha='center', va='bottom', fontsize=7, weight='bold',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

    if show_meteor and impact_pos:
        mx = impact_pos[0]
        my = min(45, impact_pos[1] + 20)

        meteor_img = create_meteor(meteor_size)
        img = plt.imread(meteor_img)
        imagebox = OffsetImage(img, zoom=meteor_size * 0.08)
        ab = AnnotationBbox(imagebox, (mx, my), frameon=False, pad=0)
        ax.add_artist(ab)

        ax.plot([mx, impact_pos[0]], [my, impact_pos[1]], 'r--', alpha=0.7, linewidth=2, label='Meteor Path')
        ax.plot(impact_pos[0], impact_pos[1], 'X', color='red',
                markersize=15, markeredgecolor='white', linewidth=2, label='Impact Point')

    ax.set_xlim(50, 120)
    ax.set_ylim(5, 45)
    ax.set_aspect('equal')
    ax.set_title('China Map - Impact Simulator\n(Provinces by population)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('East Longitude')
    ax.set_ylabel('North Latitude')
    ax.grid(False)

    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#e74c3c', markersize=10, label='>100M people', alpha=0.7),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#e67e22', markersize=10, label='80–100M people', alpha=0.7),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#f1c40f', markersize=10, label='60–80M people', alpha=0.7),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#27ae60', markersize=10, label='<60M people', alpha=0.7),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=8, label='Capital'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Economic Center'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1), title="Legend")
    return fig

def format_energy(energia_megatones: float) -> tuple[str, str]:
    """Return (value_str, unit)."""
    if energia_megatones >= 1000:
        return f"{energia_megatones/1000:.1f}", "GT"
    elif energia_megatones >= 100:
        return f"{energia_megatones:.0f}", "MT"
    elif energia_megatones >= 10:
        return f"{energia_megatones:.0f}", "MT"
    elif energia_megatones >= 1:
        return f"{energia_megatones:.1f}", "MT"
    else:
        return f"{energia_megatones:.2f}", "MT"

def simulate_impact_china(diameter: float, speed_kms: float, ix: float, iy: float, defenses: dict):
    """Simple param model; reduction combines defenses (why: quick interactive demo, not physics-accurate)."""
    masa = diameter ** 3 * 800
    energia_joules = 0.5 * masa * (speed_kms * 1000) ** 2
    energia_megatones = energia_joules / (4.184e15)

    r_total = diameter * 20 / 1000
    r_partial = r_total * 3

    reduccion = 0
    if defenses.get("laser"): reduccion += 0.3
    if defenses.get("nuclear"): reduccion += 0.4
    if defenses.get("tractor"): reduccion += 0.2
    if defenses.get("shield"): reduccion += 0.1
    reduccion = min(reduccion, 0.95)  # cap (why: avoid negative/zero edge cases)

    r_total *= (1 - reduccion)
    r_partial *= (1 - reduccion)
    energia_final = energia_megatones * (1 - reduccion)
    energia_mitigada = energia_megatones - energia_final

    provincias_afectadas = {}
    poblacion_total_afectada = 0

    for provincia_id, provincia in poblacion_china.items():
        coords = provincia['coordenadas']
        cx = (coords['x_min'] + coords['x_max']) / 2
        cy = (coords['y_min'] + coords['y_max']) / 2

        distancia = float(np.sqrt((cx - ix) ** 2 + (cy - iy) ** 2))
        if distancia <= r_total:
            factor = 0.8
        elif distancia <= r_partial:
            factor = 0.4
        else:
            factor = 0.1

        poblacion_real = int(provincia['poblacion'] * 1000)
        afectada = int(poblacion_real * factor)

        provincias_afectadas[provincia_id] = {
            'province': provincia['nombre'],
            'affected_population': afectada,
            'impact_share_%': round(factor * 100, 1),
            'distance_to_impact': round(distancia, 2),
            'total_population': poblacion_real,
            'description': provincia['descripcion'],
        }
        poblacion_total_afectada += afectada

    return {
        "energia_megatones": energia_megatones,
        "energia_final": energia_final,
        "energia_mitigada": energia_mitigada,
        "reduccion": reduccion * 100,
        "radio_destruccion_total": r_total,
        "radio_destruccion_parcial": r_partial,
        "poblacion_total_afectada": poblacion_total_afectada,
        "provincias_afectadas": provincias_afectadas,
        "punto_impacto": (ix, iy),
    }

# --- Load map image ---
imagen_china = load_china_image()

# --- Sidebar controls ---
with st.sidebar:
    st.header("Simulation Controls")

    st.subheader("Meteor")
    diametro = st.slider("Diameter (meters)", 100, 5000, 1000)
    velocidad = st.slider("Speed (km/s)", 10, 100, 50)

    st.subheader("Impact Point in China")
    punto_impacto_x = st.slider("East Longitude", 50, 120, 85)
    punto_impacto_y = st.slider("North Latitude", 5, 45, 25)

    nearest_province = "Sea / Unpopulated Area"
    min_dist = float('inf')
    for provincia_id, provincia in poblacion_china.items():
        coords = provincia['coordenadas']
        cx = (coords['x_min'] + coords['x_max']) / 2
        cy = (coords['y_min'] + coords['y_max']) / 2
        dist = float(np.sqrt((cx - punto_impacto_x)**2 + (cy - punto_impacto_y)**2))
        if dist < min_dist:
            min_dist = dist
            nearest_province = provincia['nombre']

    st.info(f"Nearest province: {nearest_province}")

    st.subheader("Defense Systems")
    col1, col2 = st.columns(2)
    with col1:
        defensa_laser = st.checkbox("Laser")
        desviacion_nuclear = st.checkbox("Nuclear")
    with col2:
        tractor_gravitatorio = st.checkbox("Tractor")
        escudo_atmosferico = st.checkbox("Shield")

# --- Provinces info ---
st.subheader("China Provinces – Population Data")
cols = st.columns(3)
for i, (provincia_id, provincia) in enumerate(poblacion_china.items()):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="district-card">
            <h4>{provincia['nombre']}</h4>
            <p>{provincia['poblacion']:,} thousand inhabitants</p>
            <p>{provincia['poblacion'] * 1000:,} people</p>
            <p>{provincia['descripcion']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- Base map ---
st.subheader("China Map – Provinces & Critical Points")
fig_base = create_china_map(imagen_china)
st.pyplot(fig_base, use_container_width=True)

# --- Simulate button ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("SIMULATE IMPACT IN CHINA", use_container_width=True, type="primary"):
        with st.spinner("Calculating trajectory and impact..."):
            time.sleep(1.5)

        defensas = {
            "laser": defensa_laser,
            "nuclear": desviacion_nuclear,
            "tractor": tractor_gravitatorio,
            "shield": escudo_atmosferico
        }

        result = simulate_impact_china(
            diameter=diametro,
            speed_kms=velocidad,
            ix=punto_impacto_x,
            iy=punto_impacto_y,
            defenses=defensas
        )

        # Energy summary
        val_ini, unit_ini = format_energy(result["energia_megatones"])
        val_fin, unit_fin = format_energy(result["energia_final"])
        val_mit, unit_mit = format_energy(result["energia_mitigada"])

        st.markdown(f"""
        <div class="energy-section">
            <div><b>Initial Impact Energy</b></div>
            <div class="energy-metric">{val_ini} {unit_ini}</div>
            <div><b>Mitigated</b>: {val_mit} {unit_mit} &nbsp; | &nbsp; <b>Reduction</b>: {result["reduccion"]:.0f}%</div>
            <div><b>Final Energy</b>: {val_fin} {unit_fin}</div>
        </div>
        """, unsafe_allow_html=True)

        if result["reduccion"] >= 50:
            st.markdown(
                f'<div class="mitigation-success">✅ Significant mitigation achieved. '
                f'Destruction radii reduced to '
                f'<b>{result["radio_destruccion_total"]:.2f}</b> (total) and '
                f'<b>{result["radio_destruccion_parcial"]:.2f}</b> (partial) map units.</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="impact-warning">⚠️ High impact risk. '
                f'Destruction radii estimated at '
                f'<b>{result["radio_destruccion_total"]:.2f}</b> (total) and '
                f'<b>{result["radio_destruccion_parcial"]:.2f}</b> (partial) map units.</div>',
                unsafe_allow_html=True
            )

        # Impact map with radii
        fig = create_china_map(imagen_china, show_meteor=True,
                               impact_pos=result["punto_impacto"], meteor_size=1.2)
        ax = fig.axes[0]
        ix, iy = result["punto_impacto"]

        circ_total = Circle((ix, iy), radius=result["radio_destruccion_total"],
                            facecolor='red', alpha=0.15, edgecolor='red', linewidth=1)
        circ_partial = Circle((ix, iy), radius=result["radio_destruccion_parcial"],
                              facecolor='orange', alpha=0.12, edgecolor='orange', linewidth=1)
        ax.add_patch(circ_partial)
        ax.add_patch(circ_total)
        ax.text(ix, iy - 2, "Impact", ha='center', va='top',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8), fontsize=8)
        st.pyplot(fig, use_container_width=True)

       # Results table
        df = pd.DataFrame.from_dict(result["provincias_afectadas"], orient='index')
        df_sorted = df.sort_values(by="affected_population", ascending=False)

        st.markdown("### Impact Results by Province")
        st.dataframe(
            df_sorted[["province", "affected_population", "impact_share_%", "distance_to_impact", "total_population", "description"]],
            use_container_width=True
        )

        # Top 5 affected
        top5 = df_sorted.head(5)[["province", "affected_population", "impact_share_%", "distance_to_impact"]]
        st.markdown("### Top 5 Most Affected Provinces")
        st.table(top5.style.format({'affected_population': '{:,}', 'distance_to_impact': '{:.2f}', 'impact_share_%': '{:.1f}'}))

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

# Configuración de la página
st.set_page_config(
    page_title="Simulador de Impacto - China",
    page_icon="🗺️",
    layout="wide"
)

# CSS personalizado
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
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">Simulador de Impacto - China</h1>', unsafe_allow_html=True)

# Nombres de archivos que deben estar en la carpeta del proyecto
MAPA_CHINA_FILE = "mapa_china.png"

# Datos de población real de China por provincias (en miles de habitantes)
poblacion_china = {
    'guangdong': {
        'nombre': 'Guangdong',
        'poblacion': 126012,  # en miles (126 millones)
        'coordenadas': {'x_min': 75, 'x_max': 90, 'y_min': 25, 'y_max': 35},
        'descripcion': 'Provincia más poblada de China'
    },
    'shandong': {
        'nombre': 'Shandong',
        'poblacion': 101527,
        'coordenadas': {'x_min': 85, 'x_max': 100, 'y_min': 40, 'y_max': 50},
        'descripcion': 'Provincia costera del este'
    },
    'henan': {
        'nombre': 'Henan',
        'poblacion': 99365,
        'coordenadas': {'x_min': 70, 'x_max': 85, 'y_min': 45, 'y_max': 55},
        'descripcion': 'Corazón de China central'
    },
    'jiangsu': {
        'nombre': 'Jiangsu',
        'poblacion': 84748,
        'coordenadas': {'x_min': 90, 'x_max': 105, 'y_min': 35, 'y_max': 45},
        'descripcion': 'Zona económica desarrollada'
    },
    'sichuan': {
        'nombre': 'Sichuan',
        'poblacion': 83675,
        'coordenadas': {'x_min': 50, 'x_max': 70, 'y_min': 40, 'y_max': 55},
        'descripcion': 'Provincia del suroeste'
    },
    'hebei': {
        'nombre': 'Hebei',
        'poblacion': 75919,
        'coordenadas': {'x_min': 80, 'x_max': 95, 'y_min': 50, 'y_max': 60},
        'descripcion': 'Rodeando Beijing'
    },
    'hunan': {
        'nombre': 'Hunan',
        'poblacion': 69185,
        'coordenadas': {'x_min': 65, 'x_max': 80, 'y_min': 30, 'y_max': 40},
        'descripcion': 'Provincia central'
    },
    'anhui': {
        'nombre': 'Anhui',
        'poblacion': 63236,
        'coordenadas': {'x_min': 85, 'x_max': 100, 'y_min': 30, 'y_max': 40},
        'descripcion': 'Este de China'
    },
    'hubei': {
        'nombre': 'Hubei',
        'poblacion': 59172,
        'coordenadas': {'x_min': 70, 'x_max': 85, 'y_min': 35, 'y_max': 45},
        'descripcion': 'China central'
    },
    'zhejiang': {
        'nombre': 'Zhejiang',
        'poblacion': 58500,
        'coordenadas': {'x_min': 95, 'x_max': 110, 'y_min': 25, 'y_max': 35},
        'descripcion': 'Costa este desarrollada'
    }
}

# Puntos de interés críticos en China
puntos_criticos_china = {
    'beijing': {'x': 88, 'y': 55, 'nombre': 'Beijing', 'tipo': 'capital'},
    'shanghai': {'x': 100, 'y': 35, 'nombre': 'Shanghai', 'tipo': 'economico'},
    'guangzhou': {'x': 82, 'y': 28, 'nombre': 'Guangzhou', 'tipo': 'economico'},
    'shenzhen': {'x': 85, 'y': 25, 'nombre': 'Shenzhen', 'tipo': 'tecnologico'},
    'wuhan': {'x': 78, 'y': 40, 'nombre': 'Wuhan', 'tipo': 'industrial'},
    'xian': {'x': 65, 'y': 48, 'nombre': 'Xi\'an', 'tipo': 'cultural'}
}

# Función para cargar imagen de China
def cargar_imagen_china():
    """Carga la imagen del mapa de China"""
    try:
        if os.path.exists(MAPA_CHINA_FILE):
            imagen_china = Image.open(MAPA_CHINA_FILE)
            st.success(f"Mapa de China cargado: {MAPA_CHINA_FILE}")
            return imagen_china
        else:
            st.warning(f"Archivo {MAPA_CHINA_FILE} no encontrado. Usando mapa por defecto.")
            return generar_mapa_china_por_defecto()
    except Exception as e:
        st.error(f"Error cargando mapa de China: {e}")
        return generar_mapa_china_por_defecto()

def generar_mapa_china_por_defecto():
    """Genera un mapa simplificado de China si no hay imagen"""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Fondo del mapa
    ax.set_facecolor('#1a1a2e')
    
    # Contorno aproximado de China
    china_outline = np.array([
        [40, 20], [50, 25], [60, 30], [70, 35], [80, 40], [90, 45],
        [100, 40], [110, 35], [115, 30], [120, 25], [115, 20],
        [105, 15], [95, 10], [85, 15], [75, 20], [65, 25], [55, 20],
        [45, 15], [40, 20]
    ])
    
    polygon = Polygon(china_outline, closed=True, facecolor='#2c3e50', 
                     edgecolor='white', alpha=0.8, linewidth=2)
    ax.add_patch(polygon)
    
    # Ríos principales (simplificados)
    ax.plot([60, 80, 95], [45, 40, 35], 'b-', linewidth=3, alpha=0.6, label='Río Yangtsé')
    ax.plot([50, 70, 85], [50, 45, 40], 'b-', linewidth=2, alpha=0.6, label='Río Amarillo')
    
    ax.set_xlim(30, 125)
    ax.set_ylim(5, 65)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Mapa de China - Simulador de Impacto', fontsize=16, color='white', pad=20)
    
    # Convertir a imagen
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                facecolor='#1a1a2e', edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    return Image.open(buf)

# Función para crear el asteroide
def crear_asteroide():
    """Crea una imagen de asteroide simple"""
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # Dibujar asteroide
    asteroid = Ellipse((0.5, 0.5), 0.8, 0.6, angle=45, 
                      facecolor='#8B7355', edgecolor='#654321', linewidth=2)
    ax.add_patch(asteroid)
    
    # Detalles de crateres
    for i in range(5):
        x, y = np.random.uniform(0.2, 0.8, 2)
        size = np.random.uniform(0.05, 0.15)
        crater = Circle((x, y), size, facecolor='#6B5B45', alpha=0.7)
        ax.add_patch(crater)
    
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Convertir a imagen
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)
    return buf

# Función para crear mapa de China
def crear_mapa_china(imagen_china, mostrar_asteroide=False, pos_asteroide=None, tamaño_asteroide=1):
    """Crea un mapa de China con provincias y puntos críticos"""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Mostrar imagen de fondo de China
    ax.imshow(imagen_china, extent=[30, 125, 5, 65], alpha=0.8)
    
    # Dibujar provincias (semi-transparentes)
    for provincia_id, provincia in poblacion_china.items():
        coords = provincia['coordenadas']
        ancho = coords['x_max'] - coords['x_min']
        alto = coords['y_max'] - coords['y_min']
        
        # Color basado en densidad poblacional
        poblacion = provincia['poblacion']
        if poblacion > 100000:  # Más de 100 millones
            color = '#e74c3c'
            alpha = 0.4
        elif poblacion > 80000:
            color = '#e67e22'
            alpha = 0.35
        elif poblacion > 60000:
            color = '#f1c40f'
            alpha = 0.3
        else:
            color = '#27ae60'
            alpha = 0.25
        
        rect = Rectangle((coords['x_min'], coords['y_min']), ancho, alto,
                        facecolor=color, alpha=alpha, edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        
        # Etiqueta de la provincia
        centro_x = (coords['x_min'] + coords['x_max']) / 2
        centro_y = (coords['y_min'] + coords['y_max']) / 2
        
        ax.text(centro_x, centro_y, 
               f"{provincia['nombre']}\n{provincia['poblacion']:,} mil hab.", 
               ha='center', va='center', fontsize=7, weight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
    
    # Dibujar puntos críticos
    for punto_id, punto in puntos_criticos_china.items():
        if punto['tipo'] == 'capital':
            marker, color = 's', 'red'
        elif punto['tipo'] == 'economico':
            marker, color = 'o', 'blue'
        elif punto['tipo'] == 'tecnologico':
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
    
    # Mostrar asteroide si está activado
    if mostrar_asteroide and pos_asteroide:
        asteroid_img = crear_asteroide()
        img = plt.imread(asteroid_img)
        
        imagebox = OffsetImage(img, zoom=tamaño_asteroide * 0.1)
        ab = AnnotationBbox(imagebox, (pos_asteroide[0], pos_asteroide[1]), 
                           frameon=False, pad=0)
        ax.add_artist(ab)
        
        # Trayectoria del asteroide
        ax.plot([pos_asteroide[0], pos_asteroide[0]], 
               [65, pos_asteroide[1]], 'r--', alpha=0.7, linewidth=2,
               label='Trayectoria Asteroide')
    
    # Configuración del mapa
    ax.set_xlim(30, 125)
    ax.set_ylim(5, 65)
    ax.set_aspect('equal')
    ax.set_title('Mapa de China - Simulador de Impacto\n(Provincias por densidad poblacional)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Longitud Este')
    ax.set_ylabel('Latitud Norte')
    ax.grid(False)
    
    # Leyenda
    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#e74c3c', 
                  markersize=10, label='>100M hab.', alpha=0.7),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#e67e22', 
                  markersize=10, label='80-100M hab.', alpha=0.7),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#f1c40f', 
                  markersize=10, label='60-80M hab.', alpha=0.7),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#27ae60', 
                  markersize=10, label='<60M hab.', alpha=0.7),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='red', 
                  markersize=8, label='Capital'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
                  markersize=8, label='Centro Económico'),
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', 
             bbox_to_anchor=(1.15, 1), title="Leyenda")
    
    return fig

# Función para formatear energía
def formatear_energia(energia_megatones):
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

# Función de simulación para China
def simular_impacto_china(diametro, velocidad, punto_impacto_x, punto_impacto_y, defensas):
    # Cálculos del impacto
    masa = diametro ** 3 * 800
    energia_joules = 0.5 * masa * (velocidad * 1000) ** 2
    energia_megatones = energia_joules / (4.184e15)
    
    # Radio de destrucción (ajustado para escala de China)
    radio_destruccion_total = diametro * 20 / 1000  # en unidades del mapa
    radio_destruccion_parcial = radio_destruccion_total * 3
    
    # Efecto de las defensas
    reduccion = 0
    if defensas["laser"]:
        reduccion += 0.3
    if defensas["nuclear"]:
        reduccion += 0.4
    if defensas["tractor"]:
        reduccion += 0.2
    if defensas["escudo"]:
        reduccion += 0.1
    
    # Aplicar reducción
    radio_destruccion_total *= (1 - reduccion)
    radio_destruccion_parcial *= (1 - reduccion)
    energia_final = energia_megatones * (1 - reduccion)
    energia_mitigada = energia_megatones - energia_final
    
    # Calcular población afectada en China
    provincias_afectadas = {}
    poblacion_total_afectada = 0
    
    for provincia_id, provincia in poblacion_china.items():
        coords = provincia['coordenadas']
        centro_x = (coords['x_min'] + coords['x_max']) / 2
        centro_y = (coords['y_min'] + coords['y_max']) / 2
        
        distancia = np.sqrt((centro_x - punto_impacto_x)**2 + (centro_y - punto_impacto_y)**2)
        
        # Calcular afectación basada en distancia
        if distancia <= radio_destruccion_total:
            factor_afectacion = 0.8  # 80% en zona de destrucción total
        elif distancia <= radio_destruccion_parcial:
            factor_afectacion = 0.4  # 40% en zona parcial
        else:
            factor_afectacion = 0.1  # 10% efectos secundarios
        
        # Convertir población de miles a número real
        poblacion_real = provincia['poblacion'] * 1000
        poblacion_afectada = int(poblacion_real * factor_afectacion)
        
        provincias_afectadas[provincia_id] = {
            'poblacion_afectada': poblacion_afectada,
            'porcentaje_afectacion': factor_afectacion * 100,
            'distancia_impacto': distancia,
            'poblacion_total': poblacion_real
        }
        poblacion_total_afectada += poblacion_afectada
    
    return {
        "energia_megatones": energia_megatones,
        "energia_final": energia_final,
        "energia_mitigada": energia_mitigada,
        "reduccion": reduccion * 100,
        "radio_destruccion_total": radio_destruccion_total,
        "radio_destruccion_parcial": radio_destruccion_parcial,
        "poblacion_total_afectada": poblacion_total_afectada,
        "provincias_afectadas": provincias_afectadas,
        "punto_impacto": (punto_impacto_x, punto_impacto_y)
    }

# Cargar imagen de China
imagen_china = cargar_imagen_china()

# Sidebar para controles
with st.sidebar:
    st.header("Controles de Simulación")
    
    st.subheader("Asteroide")
    diametro = st.slider("Diámetro (metros)", 100, 5000, 1000)
    velocidad = st.slider("Velocidad (km/s)", 10, 100, 50)
    
    st.subheader("Punto de Impacto en China")
    punto_impacto_x = st.slider("Longitud Este", 30, 125, 80)
    punto_impacto_y = st.slider("Latitud Norte", 5, 65, 35)
    
    # Mostrar provincia de impacto
    provincia_impacto = "Mar/Área despoblada"
    min_dist = float('inf')
    for provincia_id, provincia in poblacion_china.items():
        coords = provincia['coordenadas']
        centro_x = (coords['x_min'] + coords['x_max']) / 2
        centro_y = (coords['y_min'] + coords['y_max']) / 2
        distancia = np.sqrt((centro_x - punto_impacto_x)**2 + (centro_y - punto_impacto_y)**2)
        if distancia < min_dist:
            min_dist = distancia
            provincia_impacto = provincia['nombre']
    
    st.info(f"Provincia más cercana: {provincia_impacto}")
    
    st.subheader("Sistemas de Defensa")
    col1, col2 = st.columns(2)
    with col1:
        defensa_laser = st.checkbox("Láser")
        desviacion_nuclear = st.checkbox("Nuclear")
    with col2:
        tractor_gravitatorio = st.checkbox("Tractor")
        escudo_atmosferico = st.checkbox("Escudo")

# Mostrar información de provincias
st.subheader("Provincias de China - Datos Poblacionales")

cols = st.columns(3)
for i, (provincia_id, provincia) in enumerate(poblacion_china.items()):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="district-card">
        <h4>{provincia['nombre']}</h4>
        <p>{provincia['poblacion']:,} mil habitantes</p>
        <p>{provincia['poblacion'] * 1000:,} personas</p>
        <p>{provincia['descripcion']}</p>
        </div>
        """, unsafe_allow_html=True)

# Mostrar mapa base de China
st.subheader("Mapa de China - Provincias y Puntos Críticos")
fig_base = crear_mapa_china(imagen_china)
st.pyplot(fig_base)

# Botón de simulación
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("SIMULAR IMPACTO EN CHINA", use_container_width=True, type="primary"):
        
        with st.spinner("Calculando trayectoria y impacto..."):
            time.sleep(3)
        
        # Ejecutar simulación
        defensas = {
            "laser": defensa_laser,
            "nuclear": desviacion_nuclear,
            "tractor": tractor_gravitatorio,
            "escudo": escudo_atmosferico
        }
        
        resultado = simular_impacto_china(diametro, velocidad, punto_impacto_x, punto_impacto_y, defensas)
        
        # Mostrar resultados
        st.markdown("---")
        st.subheader("Resultados del Impacto en China")
        
        # SECCIÓN DE ENERGÍA
        st.markdown('<div class="energy-section">', unsafe_allow_html=True)
        
        valor_original, unidad_original = formatear_energia(resultado['energia_megatones'])
        valor_impacto, unidad_impacto = formatear_energia(resultado['energia_final'])
        valor_mitigada, unidad_mitigada = formatear_energia(resultado['energia_mitigada'])
        
        col_energia1, col_energia2, col_energia3 = st.columns(3)
        
        with col_energia1:
            st.markdown(f'<div class="energy-metric">ENERGÍA ORIGINAL</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 3rem; font-weight: bold; color: #ff6b6b;">{valor_original} {unidad_original}</div>', unsafe_allow_html=True)
            
        with col_energia2:
            st.markdown(f'<div class="energy-metric">ENERGÍA MITIGADA</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 3rem; font-weight: bold; color: #0be881;">{valor_mitigada} {unidad_mitigada}</div>', unsafe_allow_html=True)
            st.metric("Reducción", f"{resultado['reduccion']:.0f}%")
            
        with col_energia3:
            st.markdown(f'<div class="energy-metric">ENERGÍA DE IMPACTO</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 3rem; font-weight: bold; color: #ffa502;">{valor_impacto} {unidad_impacto}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mapa con impacto y asteroide
        st.subheader("Mapa con Simulación de Impacto")
        
        # Calcular tamaño del asteroide para visualización
        tamaño_asteroide_visual = min(3.0, diametro / 500)
        
        fig_impacto = crear_mapa_china(
            imagen_china,
            mostrar_asteroide=True,
            pos_asteroide=resultado['punto_impacto'],
            tamaño_asteroide=tamaño_asteroide_visual
        )
        
        # Dibujar zonas de impacto en el mapa
        ax_impacto = fig_impacto.axes[0]
        
        # Zona de destrucción total
        impacto_total = Circle(resultado['punto_impacto'], 
                              resultado['radio_destruccion_total'],
                              fill=False, color='red', linewidth=3, linestyle='--',
                              label='Zona Destrucción Total')
        ax_impacto.add_patch(impacto_total)
        
        # Zona de daños parciales
        impacto_parcial = Circle(resultado['punto_impacto'],
                                resultado['radio_destruccion_parcial'],
                                fill=False, color='orange', linewidth=2, linestyle=':',
                                label='Zona Daños Parciales')
        ax_impacto.add_patch(impacto_parcial)
        
        ax_impacto.legend(loc='upper right', bbox_to_anchor=(1.15, 0.8))
        
        st.pyplot(fig_impacto)
        
        # Población afectada por provincia
        st.subheader("Población Afectada por Provincia")
        
        # Crear tabla de resultados
        datos_tabla = []
        for provincia_id, datos in resultado['provincias_afectadas'].items():
            provincia = poblacion_china[provincia_id]
            datos_tabla.append({
                'Provincia': provincia['nombre'],
                'Población Total': f"{provincia['poblacion'] * 1000:,}",
                'Población Afectada': f"{datos['poblacion_afectada']:,}",
                '% Afectado': f"{datos['porcentaje_afectacion']:.1f}%",
                'Distancia (km)': f"{datos['distancia_impacto'] * 100:.0f}"
            })
        
        # Mostrar tabla
        df_resultados = pd.DataFrame(datos_tabla)
        st.dataframe(df_resultados, use_container_width=True)
        
        # Evaluación general
        st.subheader("Evaluación del Impacto en China")
        
        poblacion_total_china = sum([provincia['poblacion'] * 1000 for provincia in poblacion_china.values()])
        porcentaje_poblacion_afectada = (resultado['poblacion_total_afectada'] / poblacion_total_china) * 100
        
        if porcentaje_poblacion_afectada > 20:
            st.markdown(f"""
            <div class="impact-warning">
            <h3>CATASTROFE NACIONAL COMPLETA</h3>
            <p>Impacto: Apocalíptico - Más del 20% de la población afectada</p>
            <p>Población afectada: {resultado['poblacion_total_afectada']:,} personas</p>
            <p>Consecuencias: Colapso total de infraestructura y servicios a nivel nacional</p>
            <p>Acción: Respuesta internacional masiva requerida</p>
            </div>
            """, unsafe_allow_html=True)
            
        elif porcentaje_poblacion_afectada > 10:
            st.markdown(f"""
            <div class="impact-warning">
            <h3>CATASTROFE REGIONAL MAYOR</h3>
            <p>Impacto: Devastador - Entre 10-20% de la población afectada</p>
            <p>Población afectada: {resultado['poblacion_total_afectada']:,} personas</p>
            <p>Consecuencias: Daños severos en múltiples provincias</p>
            <p>Acción: Respuesta nacional de emergencia total</p>
            </div>
            """, unsafe_allow_html=True)
            
        elif porcentaje_poblacion_afectada > 5:
            st.markdown(f"""
            <div class="impact-warning">
            <h3>DESASTRE REGIONAL</h3>
            <p>Impacto: Grave - Entre 5-10% de la población afectada</p>
            <p>Población afectada: {resultado['poblacion_total_afectada']:,} personas</p>
            <p>Consecuencias: Daños significativos en regiones específicas</p>
            <p>Acción: Respuesta regional coordinada</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
            <div class="mitigation-success">
            <h3>IMPACTO CONTROLADO</h3>
            <p>Impacto: Limitado - Menos del 5% de la población afectada</p>
            <p>Población afectada: {resultado['poblacion_total_afectada']:,} personas</p>
            <p>Efectividad defensas: {resultado['reduccion']:.1f}% de reducción</p>
            <p>Acción: Respuesta local y recuperación</p>
            </div>
            """, unsafe_allow_html=True)

# Información adicional
st.markdown("---")
st.info("""
**Acerca de esta simulación:**
- Sistema basado en datos reales de población de China
- Las provincias se muestran con colores según densidad poblacional
- Los cálculos consideran población real y distancia al impacto
- El asteroide es visible en el mapa durante la simulación
- Coordenadas representan posición aproximada en el mapa de China
- Población total considerada: ~847 millones (10 provincias principales)
""")

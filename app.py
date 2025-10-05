import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Circle, Rectangle, Polygon, Ellipse
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import time
from PIL import Image
import io
import base64

# Configuración de la página
st.set_page_config(
    page_title="Simulador de Impacto - Mapa con Imagen",
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
    .upload-section {
        background: linear-gradient(45deg, #00b09b, #96c93d);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🌍 Simulador de Impacto - Mapa con Imagen</h1>', unsafe_allow_html=True)

# Sección de carga de imagen
st.markdown("""
<div class="upload-section">
<h2>🗺️ Cargar Mapa de Ciudad</h2>
<p>Sube una imagen de tu ciudad o usa el mapa por defecto. El sistema detectará automáticamente las zonas de densidad poblacional.</p>
</div>
""", unsafe_allow_html=True)

# Cargar imagen de fondo
col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader("Subir imagen de mapa (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
    
with col2:
    use_default = st.checkbox("Usar mapa por defecto", value=True)

# Función para cargar imagen
def cargar_imagen_fondo(uploaded_file, use_default):
    if uploaded_file is not None and not use_default:
        image = Image.open(uploaded_file)
        st.success(f"✅ Imagen cargada: {uploaded_file.name} ({image.size[0]}x{image.size[1]})")
        return image
    else:
        # Crear un mapa por defecto simulado
        st.info("🗺️ Usando mapa de ciudad por defecto")
        return generar_mapa_por_defecto()

def generar_mapa_por_defecto():
    """Genera un mapa de ciudad por defecto si no hay imagen"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Fondo de ciudad simulado
    ax.set_facecolor('#1a1a2e')
    
    # Crear calles principales
    for i in range(0, 101, 15):
        ax.plot([i, i], [0, 100], 'w-', alpha=0.4, linewidth=1)
        ax.plot([0, 100], [i, i], 'w-', alpha=0.4, linewidth=1)
    
    # Avenidas principales
    ax.plot([33, 33], [0, 100], 'y-', alpha=0.6, linewidth=3, label='Av. Principal')
    ax.plot([66, 66], [0, 100], 'y-', alpha=0.6, linewidth=3)
    ax.plot([0, 100], [33, 33], 'y-', alpha=0.6, linewidth=3)
    ax.plot([0, 100], [66, 66], 'y-', alpha=0.6, linewidth=3)
    
    # Zonas verdes (parques)
    parques = [
        {'x': 20, 'y': 20, 'ancho': 15, 'alto': 15},
        {'x': 70, 'y': 70, 'ancho': 20, 'alto': 20},
        {'x': 25, 'y': 70, 'ancho': 12, 'alto': 12}
    ]
    
    for parque in parques:
        rect = Rectangle((parque['x'], parque['y']), parque['ancho'], parque['alto'],
                        facecolor='#2e8b57', alpha=0.6, edgecolor='green')
        ax.add_patch(rect)
    
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Mapa de Ciudad por Defecto', fontsize=14, color='white', pad=20)
    
    # Convertir a imagen
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                facecolor='#1a1a2e', edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    return Image.open(buf)

# Cargar imagen
imagen_fondo = cargar_imagen_fondo(uploaded_file, use_default)

# Datos de densidad poblacional simulados (basados en coordenadas del mapa)
datos_densidad = {
    'centro_urbano': {
        'nombre': 'Centro Urbano',
        'poblacion': 350000,
        'densidad': 'Muy Alta',
        'coordenadas': {'x_min': 40, 'x_max': 60, 'y_min': 40, 'y_max': 60},
        'descripcion': 'Zona central de negocios y comercios'
    },
    'norte_residencial': {
        'nombre': 'Norte Residencial',
        'poblacion': 280000,
        'densidad': 'Alta',
        'coordenadas': {'x_min': 30, 'x_max': 50, 'y_min': 65, 'y_max': 85},
        'descripcion': 'Área residencial consolidada'
    },
    'sur_industrial': {
        'nombre': 'Sur Industrial',
        'poblacion': 120000,
        'densidad': 'Media',
        'coordenadas': {'x_min': 20, 'x_max': 40, 'y_min': 10, 'y_max': 30},
        'descripcion': 'Zona industrial y manufacturera'
    },
    'este_comercial': {
        'nombre': 'Este Comercial',
        'poblacion': 190000,
        'densidad': 'Alta',
        'coordenadas': {'x_min': 60, 'x_max': 80, 'y_min': 50, 'y_max': 70},
        'descripcion': 'Centros comerciales y servicios'
    },
    'oeste_residencial': {
        'nombre': 'Oeste Residencial',
        'poblacion': 220000,
        'densidad': 'Media',
        'coordenadas': {'x_min': 10, 'x_max': 30, 'y_min': 40, 'y_max': 60},
        'descripcion': 'Zona residencial media'
    },
    'distrito_universitario': {
        'nombre': 'Distrito Universitario',
        'poblacion': 80000,
        'densidad': 'Media',
        'coordenadas': {'x_min': 65, 'x_max': 85, 'y_min': 75, 'y_max': 90},
        'descripcion': 'Campus y áreas académicas'
    },
    'zona_verde_central': {
        'nombre': 'Parque Central',
        'poblacion': 5000,
        'densidad': 'Muy Baja',
        'coordenadas': {'x_min': 45, 'x_max': 55, 'y_min': 20, 'y_max': 35},
        'descripcion': 'Área verde metropolitana'
    }
}

# Puntos de interés críticos
puntos_criticos = {
    'hospital_central': {'x': 52, 'y': 52, 'nombre': 'Hospital Central', 'tipo': 'hospital'},
    'ayuntamiento': {'x': 48, 'y': 48, 'nombre': 'Ayuntamiento', 'tipo': 'gobierno'},
    'estacion_central': {'x': 55, 'y': 45, 'nombre': 'Estación Central', 'tipo': 'transporte'},
    'centro_comercial': {'x': 62, 'y': 58, 'nombre': 'Mega Centro', 'tipo': 'comercio'},
    'universidad': {'x': 72, 'y': 80, 'nombre': 'Universidad', 'tipo': 'educacion'}
}

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
    
    # Detalles de cráteres
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

# Función para crear mapa con imagen de fondo
def crear_mapa_con_imagen(imagen_fondo, mostrar_asteroide=False, pos_asteroide=None, tamaño_asteroide=1):
    """Crea un mapa con imagen de fondo y datos de densidad"""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Mostrar imagen de fondo
    ax.imshow(imagen_fondo, extent=[0, 100, 0, 100], alpha=0.7)
    
    # Dibujar zonas de densidad poblacional (semi-transparentes)
    for zona_id, zona in datos_densidad.items():
        coords = zona['coordenadas']
        ancho = coords['x_max'] - coords['x_min']
        alto = coords['y_max'] - coords['y_min']
        
        # Color basado en densidad
        if zona['densidad'] == 'Muy Alta':
            color = '#e74c3c'
            alpha = 0.3
        elif zona['densidad'] == 'Alta':
            color = '#e67e22'
            alpha = 0.25
        elif zona['densidad'] == 'Media':
            color = '#f1c40f'
            alpha = 0.2
        else:
            color = '#27ae60'
            alpha = 0.15
        
        rect = Rectangle((coords['x_min'], coords['y_min']), ancho, alto,
                        facecolor=color, alpha=alpha, edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        
        # Etiqueta de la zona
        centro_x = (coords['x_min'] + coords['x_max']) / 2
        centro_y = (coords['y_min'] + coords['y_max']) / 2
        
        ax.text(centro_x, centro_y, f"{zona['nombre']}\n{zona['poblacion']:,} hab.", 
               ha='center', va='center', fontsize=8, weight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
    
    # Dibujar puntos críticos
    for punto_id, punto in puntos_criticos.items():
        if punto['tipo'] == 'hospital':
            marker, color = 'H', 'red'
        elif punto['tipo'] == 'gobierno':
            marker, color = 's', 'blue'
        elif punto['tipo'] == 'transporte':
            marker, color = '^', 'green'
        elif punto['tipo'] == 'comercio':
            marker, color = 'o', 'orange'
        else:
            marker, color = 'D', 'purple'
        
        ax.plot(punto['x'], punto['y'], marker=marker, color=color, 
               markersize=12, markeredgecolor='white', linewidth=2)
        ax.text(punto['x'], punto['y'] + 4, punto['nombre'],
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
               [100, pos_asteroide[1]], 'r--', alpha=0.7, linewidth=2,
               label='Trayectoria Asteroide')
    
    # Configuración del mapa
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.set_title('Mapa de Ciudad - Simulador de Impacto\n(Zonas de densidad poblacional superpuestas)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Coordenada X')
    ax.set_ylabel('Coordenada Y')
    ax.grid(False)
    
    # Leyenda
    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#e74c3c', 
                  markersize=10, label='Densidad Muy Alta', alpha=0.7),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#e67e22', 
                  markersize=10, label='Densidad Alta', alpha=0.7),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#f1c40f', 
                  markersize=10, label='Densidad Media', alpha=0.7),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#27ae60', 
                  markersize=10, label='Densidad Baja', alpha=0.7),
        plt.Line2D([0], [0], marker='H', color='w', markerfacecolor='red', 
                  markersize=8, label='Hospital'),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='blue', 
                  markersize=8, label='Gobierno'),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='green', 
                  markersize=8, label='Transporte'),
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

# Función de simulación
def simular_impacto_ciudad(diametro, velocidad, punto_impacto_x, punto_impacto_y, defensas):
    # Cálculos del impacto
    masa = diametro ** 3 * 800
    energia_joules = 0.5 * masa * (velocidad * 1000) ** 2
    energia_megatones = energia_joules / (4.184e15)
    
    # Radio de destrucción
    radio_destruccion_total = diametro * 25
    radio_destruccion_parcial = radio_destruccion_total * 2
    
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
    
    # Calcular población afectada
    zonas_afectadas = {}
    poblacion_total_afectada = 0
    
    for zona_id, zona in datos_densidad.items():
        coords = zona['coordenadas']
        centro_x = (coords['x_min'] + coords['x_max']) / 2
        centro_y = (coords['y_min'] + coords['y_max']) / 2
        
        distancia = np.sqrt((centro_x - punto_impacto_x)**2 + (centro_y - punto_impacto_y)**2)
        
        # Calcular afectación basada en distancia
        if distancia <= radio_destruccion_total / 10:
            factor_afectacion = 0.9  # 90% en zona de destrucción total
        elif distancia <= radio_destruccion_parcial / 10:
            factor_afectacion = 0.6  # 60% en zona parcial
        else:
            factor_afectacion = 0.2  # 20% efectos secundarios
        
        poblacion_afectada = int(zona['poblacion'] * factor_afectacion)
        zonas_afectadas[zona_id] = {
            'poblacion_afectada': poblacion_afectada,
            'porcentaje_afectacion': factor_afectacion * 100,
            'distancia_impacto': distancia
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
        "zonas_afectadas": zonas_afectadas,
        "punto_impacto": (punto_impacto_x, punto_impacto_y)
    }

# Sidebar para controles
with st.sidebar:
    st.header("🎮 Controles de Simulación")
    
    st.subheader("🌠 Asteroide")
    diametro = st.slider("Diámetro (metros)", 100, 5000, 1000)
    velocidad = st.slider("Velocidad (km/s)", 10, 100, 50)
    
    st.subheader("🎯 Punto de Impacto")
    punto_impacto_x = st.slider("Coordenada X", 0, 100, 50)
    punto_impacto_y = st.slider("Coordenada Y", 0, 100, 50)
    
    # Mostrar zona de impacto
    zona_impacto = "Fuera de zonas pobladas"
    min_dist = float('inf')
    for zona_id, zona in datos_densidad.items():
        coords = zona['coordenadas']
        centro_x = (coords['x_min'] + coords['x_max']) / 2
        centro_y = (coords['y_min'] + coords['y_max']) / 2
        distancia = np.sqrt((centro_x - punto_impacto_x)**2 + (centro_y - punto_impacto_y)**2)
        if distancia < min_dist:
            min_dist = distancia
            zona_impacto = zona['nombre']
    
    st.info(f"**Zona más cercana:** {zona_impacto}")
    
    st.subheader("🛡️ Sistemas de Defensa")
    col1, col2 = st.columns(2)
    with col1:
        defensa_laser = st.checkbox("Láser")
        desviacion_nuclear = st.checkbox("Nuclear")
    with col2:
        tractor_gravitatorio = st.checkbox("Tractor")
        escudo_atmosferico = st.checkbox("Escudo")

# Mostrar información de zonas
st.subheader("🏘️ Zonas de Densidad Poblacional")

cols = st.columns(3)
for i, (zona_id, zona) in enumerate(datos_densidad.items()):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="district-card">
        <h4>📍 {zona['nombre']}</h4>
        <p>👥 {zona['poblacion']:,} habitantes</p>
        <p>📊 Densidad: {zona['densidad']}</p>
        <p>{zona['descripcion']}</p>
        </div>
        """, unsafe_allow_html=True)

# Mostrar mapa base con imagen de fondo
st.subheader("🗺️ Mapa con Imagen de Fondo y Densidad Poblacional")
fig_base = crear_mapa_con_imagen(imagen_fondo)
st.pyplot(fig_base)

# Botón de simulación
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🌠 SIMULAR IMPACTO DE ASTEROIDE", use_container_width=True, type="primary"):
        
        with st.spinner("Calculando trayectoria y impacto..."):
            time.sleep(3)
        
        # Ejecutar simulación
        defensas = {
            "laser": defensa_laser,
            "nuclear": desviacion_nuclear,
            "tractor": tractor_gravitatorio,
            "escudo": escudo_atmosferico
        }
        
        resultado = simular_impacto_ciudad(diametro, velocidad, punto_impacto_x, punto_impacto_y, defensas)
        
        # Mostrar resultados
        st.markdown("---")
        st.subheader("💥 Resultados del Impacto")
        
        # SECCIÓN DE ENERGÍA
        st.markdown('<div class="energy-section">', unsafe_allow_html=True)
        
        valor_original, unidad_original = formatear_energia(resultado['energia_megatones'])
        valor_impacto, unidad_impacto = formatear_energia(resultado['energia_final'])
        valor_mitigada, unidad_mitigada = formatear_energia(resultado['energia_mitigada'])
        
        col_energia1, col_energia2, col_energia3 = st.columns(3)
        
        with col_energia1:
            st.markdown(f'<div class="energy-metric">💥 ENERGÍA ORIGINAL</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 3rem; font-weight: bold; color: #ff6b6b;">{valor_original} {unidad_original}</div>', unsafe_allow_html=True)
            
        with col_energia2:
            st.markdown(f'<div class="energy-metric">🛡️ ENERGÍA MITIGADA</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 3rem; font-weight: bold; color: #0be881;">{valor_mitigada} {unidad_mitigada}</div>', unsafe_allow_html=True)
            st.metric("Reducción", f"{resultado['reduccion']:.0f}%")
            
        with col_energia3:
            st.markdown(f'<div class="energy-metric">⚡ ENERGÍA DE IMPACTO</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 3rem; font-weight: bold; color: #ffa502;">{valor_impacto} {unidad_impacto}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mapa con impacto y asteroide
        st.subheader("🌍 Mapa con Simulación de Impacto")
        
        # Calcular tamaño del asteroide para visualización
        tamaño_asteroide_visual = min(3.0, diametro / 500)
        
        fig_impacto = crear_mapa_con_imagen(
            imagen_fondo,
            mostrar_asteroide=True,
            pos_asteroide=resultado['punto_impacto'],
            tamaño_asteroide=tamaño_asteroide_visual
        )
        
        # Dibujar zonas de impacto en el mapa
        ax_impacto = fig_impacto.axes[0]
        
        # Zona de destrucción total
        impacto_total = Circle(resultado['punto_impacto'], 
                              resultado['radio_destruccion_total'] / 10,
                              fill=False, color='red', linewidth=3, linestyle='--',
                              label='Zona Destrucción Total')
        ax_impacto.add_patch(impacto_total)
        
        # Zona de daños parciales
        impacto_parcial = Circle(resultado['punto_impacto'],
                                resultado['radio_destruccion_parcial'] / 10,
                                fill=False, color='orange', linewidth=2, linestyle=':',
                                label='Zona Daños Parciales')
        ax_impacto.add_patch(impacto_parcial)
        
        ax_impacto.legend(loc='upper right', bbox_to_anchor=(1.15, 0.8))
        
        st.pyplot(fig_impacto)
        
        # Población afectada por zona
        st.subheader("👥 Población Afectada por Zona")
        
        cols_afectados = st.columns(3)
        for i, (zona_id, datos) in enumerate(resultado['zonas_afectadas'].items()):
            zona = datos_densidad[zona_id]
            with cols_afectados[i % 3]:
                st.metric(
                    f"📍 {zona['nombre']}",
                    f"{datos['poblacion_afectada']:,} hab.",
                    f"{datos['porcentaje_afectacion']:.1f}% afectado"
                )
        
        # Evaluación general
        st.subheader("📈 Evaluación del Impacto")
        
        poblacion_total = sum([zona['poblacion'] for zona in datos_densidad.values()])
        porcentaje_poblacion_afectada = (resultado['poblacion_total_afectada'] / poblacion_total) * 100
        
        if porcentaje_poblacion_afectada > 40:
            st.markdown("""
            <div class="impact-warning">
            <h3>💥 CATASTROFE CIVIL COMPLETA</h3>
            <p><strong>Impacto:</strong> Apocalíptico - Más del 40% de la población afectada</p>
            <p><strong>Población afectada:</strong> {:,} personas</p>
            <p><strong>Consecuencias:</strong> Colapso total de infraestructura y servicios</p>
            <p><strong>Acción:</strong> Evacuación total y respuesta internacional</p>
            </div>
            """.format(resultado['poblacion_total_afectada']), unsafe_allow_html=True)
            
        elif porcentaje_poblacion_afectada > 20:
            st.markdown("""
            <div class="impact-warning">
            <h3>⚠️ CATASTROFE REGIONAL</h3>
            <p><strong>Impacto:</strong> Devastador - Entre 20-40% de la población afectada</p>
            <p><strong>Población afectada:</strong> {:,} personas</p>
            <p><strong>Consecuencias:</strong> Daños severos en infraestructura crítica</p>
            <p><strong>Acción:</strong> Respuesta nacional de emergencia</p>
            </div>
            """.format(resultado['poblacion_total_afectada']), unsafe_allow_html=True)
            
        elif porcentaje_poblacion_afectada > 10:
            st.markdown("""
            <div class="impact-warning">
            <h3>🔶 DESASTRE URBANO MAYOR</h3>
            <p><strong>Impacto:</strong> Grave - Entre 10-20% de la población afectada</p>
            <p><strong>Población afectada:</strong> {:,} personas</p>
            <p><strong>Consecuencias:</strong> Daños significativos en áreas específicas</p>
            <p><strong>Acción:</strong> Respuesta regional coordinada</p>
            </div>
            """.format(resultado['poblacion_total_afectada']), unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="mitigation-success">
            <h3>✅ IMPACTO CONTROLADO</h3>
            <p><strong>Impacto:</strong> Limitado - Menos del 10% de la población afectada</p>
            <p><strong>Población afectada:</strong> {:,} personas</p>
            <p><strong>Efectividad defensas:</strong> {:.1f}% de reducción</p>
            <p><strong>Acción:</strong> Respuesta local y recuperación</p>
            </div>
            """.format(resultado['poblacion_total_afectada'], resultado['reduccion']), unsafe_allow_html=True)

# Información adicional
st.markdown("---")
st.info("""
**ℹ️ Acerca de esta simulación:**
- Sistema permite cargar cualquier imagen de mapa como fondo
- Las zonas de densidad poblacional se superponen sobre la imagen
- Los cálculos consideran densidad poblacional y distancia al impacto
- El asteroide es visible en el mapa durante la simulación
- Coordenadas van de 0 a 100 en ambos ejes para facilitar posicionamiento
""")

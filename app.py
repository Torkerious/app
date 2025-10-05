import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Circle, Rectangle, Polygon, Ellipse
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import time
import requests
from PIL import Image
import io

# Configuración de la página
st.set_page_config(
    page_title="Simulador de Impacto - Mapa Urbano",
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
st.markdown('<h1 class="main-header">🌍 Simulador de Impacto - Mapa Urbano Real</h1>', unsafe_allow_html=True)

# Descripción
st.markdown("""
<div class="city-description">
<h2>🏙️ Mapa de Ciudad Metropolitana</h2>
<p><strong>Población total:</strong> 2,500,000 habitantes • <strong>Área:</strong> 680 km²</p>
<p>Simulador de impacto de asteroides sobre una ciudad metropolitana realista con datos de población detallados.</p>
</div>
""", unsafe_allow_html=True)

# Datos de población por zonas (capa interna)
datos_poblacion = {
    'centro_historico': {
        'nombre': 'Centro Histórico',
        'poblacion': 180000,
        'densidad': 'Muy Alta',
        'coordenadas': {'x': 45, 'y': 55, 'radio': 8},
        'descripcion': 'Zona de edificios históricos y gobierno'
    },
    'distrito_financiero': {
        'nombre': 'Distrito Financiero',
        'poblacion': 220000,
        'densidad': 'Muy Alta', 
        'coordenadas': {'x': 60, 'y': 50, 'radio': 7},
        'descripcion': 'Rascacielos y oficinas corporativas'
    },
    'zona_residencial_norte': {
        'nombre': 'Residencial Norte',
        'poblacion': 450000,
        'densidad': 'Alta',
        'coordenadas': {'x': 50, 'y': 75, 'radio': 12},
        'descripcion': 'Área residencial de alta densidad'
    },
    'zona_residencial_sur': {
        'nombre': 'Residencial Sur',
        'poblacion': 380000,
        'densidad': 'Media',
        'coordenadas': {'x': 50, 'y': 25, 'radio': 10},
        'descripcion': 'Zona residencial media'
    },
    'distrito_industrial': {
        'nombre': 'Distrito Industrial',
        'poblacion': 120000,
        'densidad': 'Baja',
        'coordenadas': {'x': 75, 'y': 30, 'radio': 9},
        'descripcion': 'Área industrial y manufacturera'
    },
    'centro_comercial': {
        'nombre': 'Centro Comercial Este',
        'poblacion': 95000,
        'densidad': 'Alta',
        'coordenadas': {'x': 70, 'y': 60, 'radio': 6},
        'descripcion': 'Comercios y centros comerciales'
    },
    'universidad': {
        'nombre': 'Campus Universitario',
        'poblacion': 65000,
        'densidad': 'Media',
        'coordenadas': {'x': 35, 'y': 65, 'radio': 5},
        'descripcion': 'Área universitaria y de investigación'
    },
    'parque_metropolitano': {
        'nombre': 'Parque Metropolitano',
        'poblacion': 15000,
        'densidad': 'Muy Baja',
        'coordenadas': {'x': 40, 'y': 40, 'radio': 8},
        'descripcion': 'Área verde y recreativa'
    },
    'aeropuerto': {
        'nombre': 'Zona Aeroportuaria',
        'poblacion': 25000,
        'densidad': 'Baja',
        'coordenadas': {'x': 80, 'y': 70, 'radio': 6},
        'descripcion': 'Aeropuerto y logística'
    }
}

# Puntos de interés críticos
puntos_criticos = {
    'hospital_central': {'x': 52, 'y': 52, 'nombre': 'Hospital Central', 'tipo': 'hospital'},
    'ayuntamiento': {'x': 48, 'y': 58, 'nombre': 'Ayuntamiento', 'tipo': 'gobierno'},
    'estacion_central': {'x': 55, 'y': 48, 'nombre': 'Estación Central', 'tipo': 'transporte'},
    'plaza_mayor': {'x': 46, 'y': 53, 'nombre': 'Plaza Mayor', 'tipo': 'publico'},
    'centro_investigacion': {'x': 58, 'y': 62, 'nombre': 'Centro Investigación', 'tipo': 'ciencia'}
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

# Función para crear mapa de ciudad
def crear_mapa_ciudad(mostrar_asteroide=False, pos_asteroide=None, tamaño_asteroide=1):
    """Crea un mapa de ciudad realista"""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Fondo de ciudad (simulado)
    ax.set_facecolor('#2c3e50')
    
    # Dibujar calles principales
    for i in range(0, 101, 10):
        ax.plot([i, i], [0, 100], 'w-', alpha=0.3, linewidth=0.5)
        ax.plot([0, 100], [i, i], 'w-', alpha=0.3, linewidth=0.5)
    
    # Calles principales más anchas
    ax.plot([50, 50], [0, 100], 'y-', alpha=0.5, linewidth=2, label='Avenida Principal')
    ax.plot([0, 100], [50, 50], 'y-', alpha=0.5, linewidth=2)
    
    # Dibujar zonas de población
    for zona_id, zona in datos_poblacion.items():
        coord = zona['coordenadas']
        
        # Color basado en densidad
        if zona['densidad'] == 'Muy Alta':
            color = '#e74c3c'
            alpha = 0.7
        elif zona['densidad'] == 'Alta':
            color = '#e67e22'
            alpha = 0.6
        elif zona['densidad'] == 'Media':
            color = '#f1c40f'
            alpha = 0.5
        else:
            color = '#27ae60'
            alpha = 0.4
        
        circle = Circle((coord['x'], coord['y']), coord['radio'],
                       facecolor=color, alpha=alpha, edgecolor='white', linewidth=1)
        ax.add_patch(circle)
        
        # Etiqueta de la zona
        ax.text(coord['x'], coord['y'], zona['nombre'], 
               ha='center', va='center', fontsize=8, weight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        # Población
        ax.text(coord['x'], coord['y'] - 2, f"{zona['poblacion']:,} hab.", 
               ha='center', va='center', fontsize=7, color='white')
    
    # Dibujar puntos críticos
    for punto_id, punto in puntos_criticos.items():
        if punto['tipo'] == 'hospital':
            marker, color = 'H', 'red'
        elif punto['tipo'] == 'gobierno':
            marker, color = 's', 'blue'
        elif punto['tipo'] == 'transporte':
            marker, color = '^', 'green'
        elif punto['tipo'] == 'ciencia':
            marker, color = 'D', 'purple'
        else:
            marker, color = 'o', 'orange'
        
        ax.plot(punto['x'], punto['y'], marker=marker, color=color, 
               markersize=10, markeredgecolor='white', linewidth=1.5)
        ax.text(punto['x'], punto['y'] + 3, punto['nombre'],
               ha='center', va='bottom', fontsize=7, weight='bold', color='white')
    
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
    ax.set_title('Mapa de Ciudad Metropolitana - Simulador de Impacto', 
                fontsize=16, fontweight='bold', pad=20, color='white')
    ax.set_xlabel('Coordenada X', color='white')
    ax.set_ylabel('Coordenada Y', color='white')
    ax.tick_params(colors='white')
    
    # Leyenda
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#e74c3c', 
                  markersize=8, label='Densidad Muy Alta'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#e67e22', 
                  markersize=8, label='Densidad Alta'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#f1c40f', 
                  markersize=8, label='Densidad Media'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#27ae60', 
                  markersize=8, label='Densidad Baja'),
        plt.Line2D([0], [0], marker='H', color='w', markerfacecolor='red', 
                  markersize=8, label='Hospital'),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='blue', 
                  markersize=8, label='Gobierno'),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='green', 
                  markersize=8, label='Transporte'),
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', 
             bbox_to_anchor=(1.15, 1), facecolor='#34495e', edgecolor='white',
             labelcolor='white')
    
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
    
    for zona_id, zona in datos_poblacion.items():
        coord = zona['coordenadas']
        distancia = np.sqrt((coord['x'] - punto_impacto_x)**2 + (coord['y'] - punto_impacto_y)**2)
        
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
    for zona_id, zona in datos_poblacion.items():
        coord = zona['coordenadas']
        distancia = np.sqrt((coord['x'] - punto_impacto_x)**2 + (coord['y'] - punto_impacto_y)**2)
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
st.subheader("🏘️ Zonas de la Ciudad")

cols = st.columns(3)
for i, (zona_id, zona) in enumerate(datos_poblacion.items()):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="district-card">
        <h4>📍 {zona['nombre']}</h4>
        <p>👥 {zona['poblacion']:,} habitantes</p>
        <p>📊 Densidad: {zona['densidad']}</p>
        <p>{zona['descripcion']}</p>
        </div>
        """, unsafe_allow_html=True)

# Mostrar mapa base
st.subheader("🗺️ Mapa de la Ciudad")
fig_base = crear_mapa_ciudad()
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
        
        fig_impacto = crear_mapa_ciudad(
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
        
        ax_impacto.legend(loc='upper right', bbox_to_anchor=(1.15, 0.8),
                         facecolor='#34495e', edgecolor='white', labelcolor='white')
        
        st.pyplot(fig_impacto)
        
        # Población afectada por zona
        st.subheader("👥 Población Afectada por Zona")
        
        cols_afectados = st.columns(3)
        for i, (zona_id, datos) in enumerate(resultado['zonas_afectados'].items()):
            zona = datos_poblacion[zona_id]
            with cols_afectados[i % 3]:
                st.metric(
                    f"📍 {zona['nombre']}",
                    f"{datos['poblacion_afectada']:,} hab.",
                    f"{datos['porcentaje_afectacion']:.1f}% afectado"
                )
        
        # Evaluación general
        st.subheader("📈 Evaluación del Impacto")
        
        porcentaje_poblacion_afectada = (resultado['poblacion_total_afectada'] / 2500000) * 100
        
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
- Mapa muestra distribución realista de población en zonas urbanas
- Los cálculos consideran densidad poblacional y distancia al impacto
- El asteroide es visible en el mapa durante la simulación
- Los sistemas de defensa reducen energía entre 10-100% según combinación
""")

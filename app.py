import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Circle, Rectangle, Polygon
import time

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
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🗺️ Simulador de Impacto - Mapa Urbano</h1>', unsafe_allow_html=True)

# Descripción
st.markdown("""
<div class="city-description">
<h2>🏙️ Mapa Urbano de Referencia</h2>
<p><strong>Población total:</strong> 1,200,000 habitantes • <strong>Área:</strong> 450 km²</p>
<p>Este mapa representa una ciudad típica con distritos definidos y datos de población realistas para simular impactos de meteoritos.</p>
</div>
""", unsafe_allow_html=True)

# Mapa fijo de la ciudad - DISTRITOS DEFINIDOS
distritos_ciudad = {
    'centro': {
        'nombre': 'Centro Urbano',
        'color': '#FF6B6B',
        'poblacion': 250000,
        'area': 'Zona de rascacielos y comercios',
        'coordenadas': [(30, 30), (70, 30), (70, 70), (30, 70)]
    },
    'norte': {
        'nombre': 'Zona Norte Residencial',
        'color': '#4ECDC4',
        'poblacion': 300000,
        'area': 'Área residencial de alta densidad',
        'coordenadas': [(20, 70), (80, 70), (80, 95), (20, 95)]
    },
    'sur': {
        'nombre': 'Distrito Sur Industrial',
        'color': '#45B7D1',
        'poblacion': 150000,
        'area': 'Zona industrial y logística',
        'coordenadas': [(10, 5), (90, 5), (90, 30), (10, 30)]
    },
    'este': {
        'nombre': 'Este Comercial',
        'color': '#96CEB4',
        'poblacion': 200000,
        'area': 'Centros comerciales y oficinas',
        'coordenadas': [(70, 30), (95, 30), (95, 70), (70, 70)]
    },
    'oeste': {
        'nombre': 'Oeste Residencial',
        'color': '#FFEAA7',
        'poblacion': 200000,
        'area': 'Zona residencial media',
        'coordenadas': [(5, 30), (30, 30), (30, 70), (5, 70)]
    },
    'parque_central': {
        'nombre': 'Parque Central',
        'color': '#55EFC4',
        'poblacion': 5000,
        'area': 'Área verde recreativa',
        'coordenadas': [(40, 40), (60, 40), (60, 60), (40, 60)]
    }
}

# Puntos de interés fijos
puntos_interes = [
    {'nombre': 'Ayuntamiento', 'x': 50, 'y': 50, 'tipo': 'gobierno'},
    {'nombre': 'Hospital Central', 'x': 60, 'y': 45, 'tipo': 'salud'},
    {'nombre': 'Estación Central', 'x': 45, 'y': 55, 'tipo': 'transporte'},
    {'nombre': 'Universidad', 'x': 35, 'y': 65, 'tipo': 'educacion'},
    {'nombre': 'Centro Comercial', 'x': 65, 'y': 35, 'tipo': 'comercio'},
    {'nombre': 'Plaza Principal', 'x': 50, 'y': 50, 'tipo': 'publico'},
]

# Función para crear el mapa base
def crear_mapa_base():
    """Crea el mapa base fijo de la ciudad"""
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Dibujar distritos
    for distrito_id, distrito in distritos_ciudad.items():
        coordenadas = distrito['coordenadas']
        poly = Polygon(coordenadas, closed=True, 
                      facecolor=distrito['color'], alpha=0.6,
                      edgecolor='black', linewidth=2)
        ax.add_patch(poly)
        
        # Calcular centro para la etiqueta
        x_centro = np.mean([p[0] for p in coordenadas])
        y_centro = np.mean([p[1] for p in coordenadas])
        
        ax.text(x_centro, y_centro, 
               f"{distrito['nombre']}\n{distrito['poblacion']:,} hab.",
               ha='center', va='center', fontsize=9, weight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Dibujar puntos de interés
    for punto in puntos_interes:
        if punto['tipo'] == 'gobierno':
            marker, color, size = 's', '#8B0000', 80
        elif punto['tipo'] == 'salud':
            marker, color, size = 'H', '#FF0000', 70
        elif punto['tipo'] == 'transporte':
            marker, color, size = '^', '#000080', 70
        elif punto['tipo'] == 'educacion':
            marker, color, size = 'D', '#800080', 70
        elif punto['tipo'] == 'comercio':
            marker, color, size = 'o', '#FF8C00', 70
        else:
            marker, color, size = 'p', '#228B22', 60
            
        ax.scatter(punto['x'], punto['y'], marker=marker, 
                  c=color, s=size, edgecolors='black', linewidth=1.5)
        ax.text(punto['x'], punto['y'] + 3, punto['nombre'],
               ha='center', va='bottom', fontsize=7, weight='bold')
    
    # Configuración del mapa
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.set_title('Mapa Urbano - Distribución de Población', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Coordenada X')
    ax.set_ylabel('Coordenada Y')
    ax.grid(True, alpha=0.3)
    
    # Leyenda de puntos de interés
    leyenda_elements = [
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#8B0000', 
                  markersize=8, label='Gobierno'),
        plt.Line2D([0], [0], marker='H', color='w', markerfacecolor='#FF0000', 
                  markersize=8, label='Salud'),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='#000080', 
                  markersize=8, label='Transporte'),
        plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='#800080', 
                  markersize=8, label='Educación'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF8C00', 
                  markersize=8, label='Comercio'),
        plt.Line2D([0], [0], marker='p', color='w', markerfacecolor='#228B22', 
                  markersize=8, label='Espacio Público'),
    ]
    
    ax.legend(handles=leyenda_elements, loc='upper right', 
             bbox_to_anchor=(1.15, 1), title="Puntos de Interés")
    
    return fig, ax

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

# Función de simulación SIMPLIFICADA
def simular_impacto_mapa(diametro, velocidad, punto_impacto_x, punto_impacto_y, defensas):
    # Cálculos básicos del impacto
    masa = diametro ** 3 * 800
    energia_joules = 0.5 * masa * (velocidad * 1000) ** 2
    energia_megatones = energia_joules / (4.184e15)
    
    # Radio de destrucción
    radio_destruccion_total = diametro * 20  # metros
    radio_destruccion_parcial = radio_destruccion_total * 1.5
    
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
    
    # Calcular población afectada por distrito
    distritos_afectados = {}
    poblacion_total_afectada = 0
    
    for distrito_id, distrito in distritos_ciudad.items():
        # Calcular distancia del impacto al centro del distrito
        coordenadas = distrito['coordenadas']
        centro_x = np.mean([p[0] for p in coordenadas])
        centro_y = np.mean([p[1] for p in coordenadas])
        
        distancia = np.sqrt((centro_x - punto_impacto_x)**2 + (centro_y - punto_impacto_y)**2)
        
        # Calcular porcentaje de afectación basado en distancia
        if distancia <= radio_destruccion_total / 50:  # Escalado para el mapa
            porcentaje_afectacion = 0.8  # 80% de afectación en zona de destrucción total
        elif distancia <= radio_destruccion_parcial / 50:
            porcentaje_afectacion = 0.4  # 40% en zona parcial
        else:
            porcentaje_afectacion = 0.1  # 10% efectos menores
        
        poblacion_afectada = int(distrito['poblacion'] * porcentaje_afectacion)
        distritos_afectados[distrito_id] = {
            'poblacion_afectada': poblacion_afectada,
            'porcentaje_afectacion': porcentaje_afectacion * 100,
            'distancia_centro': distancia
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
        "distritos_afectados": distritos_afectados,
        "punto_impacto": (punto_impacto_x, punto_impacto_y)
    }

# Sidebar para controles
with st.sidebar:
    st.header("🎮 Controles de Simulación")
    
    st.subheader("🌠 Características del Meteorito")
    diametro = st.slider("Diámetro (metros)", 50, 2000, 500)
    velocidad = st.slider("Velocidad (km/s)", 10, 70, 30)
    
    st.subheader("🎯 Punto de Impacto")
    punto_impacto_x = st.slider("Coordenada X", 0, 100, 50)
    punto_impacto_y = st.slider("Coordenada Y", 0, 100, 50)
    
    # Mostrar área de impacto
    area_impacto = "Centro Urbano"
    for distrito_id, distrito in distritos_ciudad.items():
        coordenadas = distrito['coordenadas']
        x_min = min(p[0] for p in coordenadas)
        x_max = max(p[0] for p in coordenadas)
        y_min = min(p[1] for p in coordenadas)
        y_max = max(p[1] for p in coordenadas)
        
        if x_min <= punto_impacto_x <= x_max and y_min <= punto_impacto_y <= y_max:
            area_impacto = distrito['nombre']
            break
    
    st.info(f"**Área seleccionada:** {area_impacto}")
    
    st.subheader("🛡️ Sistemas de Defensa")
    defensa_laser = st.checkbox("Defensa Láser")
    desviacion_nuclear = st.checkbox("Desviación Nuclear")
    tractor_gravitatorio = st.checkbox("Tractor Gravitatorio")
    escudo_atmosferico = st.checkbox("Escudo Atmosférico")

# Mostrar mapa base
st.subheader("🗺️ Mapa Urbano de Referencia")
fig_base, ax_base = crear_mapa_base()
st.pyplot(fig_base)

# Información de distritos
st.subheader("📊 Datos de Población por Distrito")

cols = st.columns(3)
for i, (distrito_id, distrito) in enumerate(distritos_ciudad.items()):
    with cols[i % 3]:
        st.metric(
            f"📍 {distrito['nombre']}",
            f"{distrito['poblacion']:,} hab.",
            distrito['area']
        )

# Botón de simulación
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🌠 SIMULAR IMPACTO", use_container_width=True, type="primary"):
        
        with st.spinner("Calculando impacto..."):
            time.sleep(2)
        
        # Ejecutar simulación
        defensas = {
            "laser": defensa_laser,
            "nuclear": desviacion_nuclear,
            "tractor": tractor_gravitatorio,
            "escudo": escudo_atmosferico
        }
        
        resultado = simular_impacto_mapa(diametro, velocidad, punto_impacto_x, punto_impacto_y, defensas)
        
        # Mostrar resultados
        st.markdown("---")
        st.subheader("📊 Resultados del Impacto")
        
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
        
        # Mapa con impacto
        st.subheader("🗺️ Mapa con Simulación de Impacto")
        fig_impacto, ax_impacto = crear_mapa_base()
        
        # Dibujar zonas de impacto
        impacto_total = Circle(resultado['punto_impacto'], 
                              resultado['radio_destruccion_total'] / 50,
                              fill=False, color='red', linewidth=3, linestyle='--',
                              label='Zona Destrucción Total')
        ax_impacto.add_patch(impacto_total)
        
        impacto_parcial = Circle(resultado['punto_impacto'],
                                resultado['radio_destruccion_parcial'] / 50,
                                fill=False, color='orange', linewidth=2, linestyle=':',
                                label='Zona Daños Parciales')
        ax_impacto.add_patch(impacto_parcial)
        
        # Punto de impacto
        ax_impacto.plot(resultado['punto_impacto'][0], resultado['punto_impacto'][1], 
                       'ro', markersize=15, label='Punto de Impacto', 
                       markeredgecolor='black')
        
        ax_impacto.set_title('Mapa Urbano - Simulación de Impacto', 
                            fontsize=16, fontweight='bold', pad=20)
        ax_impacto.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        
        st.pyplot(fig_impacto)
        
        # Población afectada por distrito
        st.subheader("👥 Población Afectada por Distrito")
        
        cols_afectados = st.columns(3)
        for i, (distrito_id, datos) in enumerate(resultado['distritos_afectados'].items()):
            distrito = distritos_ciudad[distrito_id]
            with cols_afectados[i % 3]:
                st.metric(
                    f"📍 {distrito['nombre']}",
                    f"{datos['poblacion_afectada']:,} hab.",
                    f"{datos['porcentaje_afectacion']:.1f}% afectado"
                )
        
        # Evaluación general
        st.subheader("📈 Evaluación del Impacto")
        
        porcentaje_poblacion_afectada = (resultado['poblacion_total_afectada'] / 1200000) * 100
        
        if porcentaje_poblacion_afectada > 50:
            st.markdown("""
            <div class="impact-warning">
            <h3>💥 CATASTROFE URBANA</h3>
            <p><strong>Impacto:</strong> Devastador - Más del 50% de la población afectada</p>
            <p><strong>Población afectada:</strong> {:,} personas</p>
            <p><strong>Recomendación:</strong> Evacuación total y respuesta de emergencia nacional</p>
            </div>
            """.format(resultado['poblacion_total_afectada']), unsafe_allow_html=True)
            
        elif porcentaje_poblacion_afectada > 20:
            st.markdown("""
            <div class="impact-warning">
            <h3>⚠️ IMPACTO GRAVE</h3>
            <p><strong>Impacto:</strong> Severo - Entre 20-50% de la población afectada</p>
            <p><strong>Población afectada:</strong> {:,} personas</p>
            <p><strong>Recomendación:</strong> Respuesta regional de emergencia</p>
            </div>
            """.format(resultado['poblacion_total_afectada']), unsafe_allow_html=True)
            
        elif porcentaje_poblacion_afectada > 5:
            st.markdown("""
            <div class="impact-warning">
            <h3>🔶 IMPACTO MODERADO</h3>
            <p><strong>Impacto:</strong> Moderado - Entre 5-20% de la población afectada</p>
            <p><strong>Población afectada:</strong> {:,} personas</p>
            <p><strong>Recomendación:</strong> Respuesta local coordinada</p>
            </div>
            """.format(resultado['poblacion_total_afectada']), unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="mitigation-success">
            <h3>✅ IMPACTO CONTROLADO</h3>
            <p><strong>Impacto:</strong> Menor - Menos del 5% de la población afectada</p>
            <p><strong>Población afectada:</strong> {:,} personas</p>
            <p><strong>Efectividad defensas:</strong> {:.1f}% de reducción</p>
            </div>
            """.format(resultado['poblacion_total_afectada'], resultado['reduccion']), unsafe_allow_html=True)

# Información adicional
st.markdown("---")
st.info("""
**ℹ️ Acerca de esta simulación:**
- El mapa muestra distritos urbanos con datos de población realistas
- Los cálculos de impacto consideran la distancia desde el punto de impacto
- Los sistemas de defensa reducen la energía del impacto entre 10-100%
- La población afectada se calcula basándose en la proximidad al impacto
""")

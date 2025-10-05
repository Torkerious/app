import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Circle, Rectangle, Polygon
import time
import random

# Configuración de la página
st.set_page_config(
    page_title="Simulador de Impacto Urbano",
    page_icon="🌆",
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
    .impact-warning {
        background: linear-gradient(45deg, #ff4444, #ff6b6b);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #ff0000;
    }
    .mitigation-success {
        background: linear-gradient(45deg, #44ff44, #66ff66);
        color: black;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #00ff00;
    }
    .city-stats {
        background: linear-gradient(45deg, #4A90E2, #357ABD);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🌆 Simulador de Impacto en Ciudad</h1>', unsafe_allow_html=True)

# Definir colores de edificios (CORREGIDO)
colores_edificios = {
    'residencial': 'blue',
    'comercial': 'orange', 
    'industrial': 'red',
    'rascacielos': 'purple'
}

# Generar mapa de ciudad
def generar_ciudad():
    """Genera una ciudad aleatoria con diferentes tipos de edificios"""
    ciudad = {
        'edificios': [],
        'parques': [],
        'carreteras': [],
        'zonas_residenciales': []
    }
    
    # Generar edificios (posición x, posición y, tipo, altura)
    for _ in range(30):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        tipo = random.choice(['residencial', 'comercial', 'industrial', 'rascacielos'])
        altura = random.uniform(1, 3) if tipo == 'residencial' else random.uniform(2, 4) if tipo == 'comercial' else random.uniform(3, 6) if tipo == 'industrial' else random.uniform(5, 8)
        ciudad['edificios'].append({'x': x, 'y': y, 'tipo': tipo, 'altura': altura})
    
    # Generar parques
    for _ in range(4):
        x = random.uniform(10, 90)
        y = random.uniform(10, 90)
        tamaño = random.uniform(5, 15)
        ciudad['parques'].append({'x': x, 'y': y, 'tamaño': tamaño})
    
    # Generar carreteras principales
    ciudad['carreteras'] = [
        {'x1': 0, 'y1': 25, 'x2': 100, 'y2': 25, 'ancho': 2},
        {'x1': 0, 'y1': 50, 'x2': 100, 'y2': 50, 'ancho': 2},
        {'x1': 0, 'y1': 75, 'x2': 100, 'y2': 75, 'ancho': 2},
        {'x1': 25, 'y1': 0, 'x2': 25, 'y2': 100, 'ancho': 2},
        {'x1': 50, 'y1': 0, 'x2': 50, 'y2': 100, 'ancho': 2},
        {'x1': 75, 'y1': 0, 'x2': 75, 'y2': 100, 'ancho': 2}
    ]
    
    return ciudad

# Función de simulación mejorada
def simular_impacto_ciudad(diametro, velocidad, angulo, punto_impacto_x, punto_impacto_y, defensas):
    # Cálculos del impacto
    masa = diametro ** 3 * 800  # kg/m³ promedio
    energia_joules = 0.5 * masa * (velocidad * 1000) ** 2
    energia_megatones = energia_joules / (4.184e15)
    
    # Radio de destrucción basado en energía
    radio_destruccion_total = diametro * 15  # Radio en metros escalado
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
    
    # Calcular daños a la ciudad
    ciudad = generar_ciudad()
    edificios_destruidos = 0
    edificios_danados = 0
    
    for edificio in ciudad['edificios']:
        distancia = np.sqrt((edificio['x'] - punto_impacto_x)**2 + (edificio['y'] - punto_impacto_y)**2)
        
        if distancia <= radio_destruccion_total / 100:  # Escalar a coordenadas de ciudad
            edificios_destruidos += 1
        elif distancia <= radio_destruccion_parcial / 100:
            edificios_danados += 1
    
    poblacion_afectada = (edificios_destruidos * 50 + edificios_danados * 10)  # Estimación simple
    
    return {
        "energia_megatones": energia_megatones,
        "energia_final": energia_final,
        "reduccion": reduccion * 100,
        "radio_destruccion_total": radio_destruccion_total,
        "radio_destruccion_parcial": radio_destruccion_parcial,
        "edificios_destruidos": edificios_destruidos,
        "edificios_danados": edificios_danados,
        "poblacion_afectada": poblacion_afectada,
        "ciudad": ciudad
    }

# Sidebar para controles
with st.sidebar:
    st.header("🎮 Controles de Simulación")
    
    # Parámetros del meteorito
    st.subheader("🌠 Meteorito")
    diametro = st.slider("Diámetro (metros)", 10, 1000, 100)
    velocidad = st.slider("Velocidad (km/s)", 5, 70, 20)
    angulo_impacto = st.slider("Ángulo de impacto", 0, 90, 45)
    
    st.subheader("🎯 Punto de Impacto")
    punto_impacto_x = st.slider("Coordenada X", 0, 100, 50)
    punto_impacto_y = st.slider("Coordenada Y", 0, 100, 50)
    
    # Estrategias de mitigación
    st.header("🛡️ Estrategias de Mitigación")
    defensa_laser = st.checkbox("Sistema de Defensa Láser", help="Láseres orbitales que vaporizan parte del meteorito")
    desviacion_nuclear = st.checkbox("Desviación Nuclear", help="Explosiones nucleares para alterar trayectoria")
    tractor_gravitatorio = st.checkbox("Tractor Gravitatorio", help="Nave que usa gravedad para desviación suave")
    escudo_atmosferico = st.checkbox("Escudo Atmosférico", help="Refuerzo de defensas atmosféricas")

# Inicializar variable resultado
resultado = None

# Botón de simulación principal
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🌠 SIMULAR IMPACTO URBANO", use_container_width=True, type="primary"):
        
        # Animación de carga
        with st.spinner("Calculando trayectoria y evaluando daños..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
        
        # Ejecutar simulación
        defensas = {
            "laser": defensa_laser,
            "nuclear": desviacion_nuclear,
            "tractor": tractor_gravitatorio,
            "escudo": escudo_atmosferico
        }
        
        resultado = simular_impacto_ciudad(diametro, velocidad, angulo_impacto, 
                                         punto_impacto_x, punto_impacto_y, defensas)
        
        # Mostrar resultados
        st.subheader("📊 Reporte de Impacto Urbano")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Energía del Impacto", f"{resultado['energia_megatones']:.2f} MT")
        with col2:
            st.metric("Edificios Destruidos", f"{resultado['edificios_destruidos']}")
        with col3:
            st.metric("Edificios Dañados", f"{resultado['edificios_danados']}")
        with col4:
            st.metric("Población Afectada", f"{resultado['poblacion_afectada']}")
        
        # Visualización del mapa de impacto
        st.subheader("🗺️ Mapa de Impacto Urbano")
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Dibujar ciudad
        ciudad = resultado['ciudad']
        
        # Dibujar parques (áreas verdes)
        for parque in ciudad['parques']:
            circle = Circle((parque['x'], parque['y']), parque['tamaño']/10, 
                          color='green', alpha=0.4, label='Parque' if parque == ciudad['parques'][0] else "")
            ax.add_patch(circle)
        
        # Dibujar carreteras
        for carretera in ciudad['carreteras']:
            ax.plot([carretera['x1'], carretera['x2']], 
                   [carretera['y1'], carretera['y2']], 
                   'gray', linewidth=carretera['ancho'], alpha=0.7)
        
        # Dibujar edificios (CORREGIDO - usando colores_edificios)
        for edificio in ciudad['edificios']:
            distancia = np.sqrt((edificio['x'] - punto_impacto_x)**2 + (edificio['y'] - punto_impacto_y)**2)
            
            # Determinar estado del edificio
            if distancia <= resultado['radio_destruccion_total'] / 100:
                color = 'black'  # Destruido
                alpha = 0.3
            elif distancia <= resultado['radio_destruccion_parcial'] / 100:
                color = 'red'  # Dañado
                alpha = 0.6
            else:
                color = colores_edificios[edificio['tipo']]  # CORREGIDO
                alpha = 0.8
            
            rect = Rectangle((edificio['x']-0.5, edificio['y']-0.5), 1, edificio['altura'],
                           facecolor=color, alpha=alpha,
                           edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
        
        # Dibujar zona de impacto
        impacto = Circle((punto_impacto_x, punto_impacto_y), 
                        resultado['radio_destruccion_total'] / 100,
                        fill=False, color='red', linewidth=3, linestyle='--',
                        label='Zona de Destrucción Total')
        ax.add_patch(impacto)
        
        # Zona de daños parciales
        danos_parciales = Circle((punto_impacto_x, punto_impacto_y),
                               resultado['radio_destruccion_parcial'] / 100,
                               fill=False, color='orange', linewidth=2, linestyle=':',
                               label='Zona de Daños Parciales')
        ax.add_patch(danos_parciales)
        
        # Punto de impacto
        ax.plot(punto_impacto_x, punto_impacto_y, 'ro', markersize=10, label='Punto de Impacto')
        
        # Configuración del gráfico
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')
        ax.set_title('Mapa de la Ciudad - Simulación de Impacto', fontsize=16, fontweight='bold')
        ax.set_xlabel('Coordenada X')
        ax.set_ylabel('Coordenada Y')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        st.pyplot(fig)
        
        # Evaluación de resultados
        st.subheader("📈 Evaluación de Daños")
        
        if resultado['edificios_destruidos'] > 20:
            st.markdown('<div class="impact-warning">💥 CATASTROFE URBANA: Impacto devastador con destrucción masiva</div>', unsafe_allow_html=True)
            st.error(f"🚨 Se estiman {resultado['poblacion_afectada']} personas afectadas. Evacuación inmediata requerida.")
        elif resultado['edificios_destruidos'] > 10:
            st.warning("⚠️ IMPACTO GRAVE: Daños extensos en el área urbana")
            st.info(f"🏥 {resultado['poblacion_afectada']} personas requieren asistencia")
        elif resultado['edificios_destruidos'] > 5:
            st.info("🔶 IMPACTO MODERADO: Daños localizados pero manejables")
        else:
            st.markdown('<div class="mitigation-success">✅ IMPACTO CONTROLADO: Las estrategias de mitigación han funcionado efectivamente</div>', unsafe_allow_html=True)
            st.success(f"🎉 Solo daños menores reportados. {resultado['reduccion']:.1f}% de reducción gracias a las defensas.")

# Información educativa
st.markdown("---")
st.header("🏗️ Leyenda del Mapa Urbano")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**🔵 Edificios Residenciales**")
    st.write("Viviendas y apartamentos")
    
with col2:
    st.markdown("**🟠 Edificios Comerciales**")
    st.write("Oficinas y comercios")
    
with col3:
    st.markdown("**🔴 Edificios Industriales**")
    st.write("Fábricas y almacenes")
    
with col4:
    st.markdown("**🟣 Rascacielos**")
    st.write("Edificios de gran altura")

# Mostrar ciudad de ejemplo si no hay simulación
if resultado is None:
    st.info("🎯 **Instrucciones:** Ajusta los parámetros en el panel lateral y haz clic en 'SIMULAR IMPACTO URBANO' para ver los efectos en la ciudad.")
    
    # Mostrar ciudad de ejemplo
    ciudad_ejemplo = generar_ciudad()
    fig_ejemplo, ax_ejemplo = plt.subplots(figsize=(10, 8))
    
    # Dibujar ciudad de ejemplo
    for parque in ciudad_ejemplo['parques']:
        circle = Circle((parque['x'], parque['y']), parque['tamaño']/10, color='green', alpha=0.4)
        ax_ejemplo.add_patch(circle)
    
    for carretera in ciudad_ejemplo['carreteras']:
        ax_ejemplo.plot([carretera['x1'], carretera['x2']], 
                       [carretera['y1'], carretera['y2']], 
                       'gray', linewidth=carretera['ancho'], alpha=0.7)
    
    for edificio in ciudad_ejemplo['edificios']:
        color = colores_edificios[edificio['tipo']]  # CORREGIDO
        rect = Rectangle((edificio['x']-0.5, edificio['y']-0.5), 1, edificio['altura'],
                       facecolor=color, alpha=0.8, edgecolor='black', linewidth=0.5)
        ax_ejemplo.add_patch(rect)
    
    ax_ejemplo.set_xlim(0, 100)
    ax_ejemplo.set_ylim(0, 100)
    ax_ejemplo.set_aspect('equal')
    ax_ejemplo.set_title('Mapa de la Ciudad - Vista Previa', fontsize=14)
    ax_ejemplo.grid(True, alpha=0.3)
    
    st.pyplot(fig_ejemplo)

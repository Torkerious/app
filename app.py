import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Circle, Rectangle, Polygon, Wedge
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
    .config-section {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .density-section {
        background: linear-gradient(45deg, #ff7e5f, #feb47b);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🌆 Simulador de Impacto en Ciudad</h1>', unsafe_allow_html=True)

# SECCIÓN DE DENSIDAD DE POBLACIÓN
st.markdown('<div class="density-section">', unsafe_allow_html=True)
st.subheader("👥 Densidad de Población")

col1, col2 = st.columns(2)

with col1:
    densidad_poblacion = st.slider(
        "Nivel de Densidad Poblacional", 
        min_value=10, 
        max_value=100, 
        value=50, 
        step=5,
        help="Controla cuántos edificios aparecen en la ciudad. Mayor densidad = más edificios"
    )

with col2:
    # Mostrar descripción de la densidad
    if densidad_poblacion <= 25:
        st.metric("Tipo de Ciudad", "Zona Rural", delta="Baja densidad")
        st.info("🏡 Pocos edificios, áreas extensas abiertas")
    elif densidad_poblacion <= 50:
        st.metric("Tipo de Ciudad", "Zona Suburbana", delta="Densidad media")
        st.info("🏘️ Mezcla de edificios y espacios abiertos")
    elif densidad_poblacion <= 75:
        st.metric("Tipo de Ciudad", "Zona Urbana", delta="Alta densidad")
        st.info("🏢 Muchos edificios, ciudad desarrollada")
    else:
        st.metric("Tipo de Ciudad", "Metrópolis", delta="Máxima densidad")
        st.info("🏙️ Ciudad muy densa, muchos rascacielos")

st.markdown('</div>', unsafe_allow_html=True)

# SECCIÓN DE CONFIGURACIÓN - MULTIPLICADORES DE ESCALA
st.markdown('<div class="config-section">', unsafe_allow_html=True)
st.subheader("⚙️ Configuración de Escala de Edificios")

col1, col2 = st.columns(2)

with col1:
    multiplicador_ancho = st.slider(
        "Multiplicador de Ancho de Edificios", 
        min_value=0.5, 
        max_value=5.0, 
        value=2.5, 
        step=0.1,
        help="Ajusta qué tan anchos se ven los edificios en el mapa"
    )

with col2:
    multiplicador_altura = st.slider(
        "Multiplicador de Altura de Edificios", 
        min_value=0.5, 
        max_value=3.0, 
        value=1.0, 
        step=0.1,
        help="Ajusta qué tan altos se ven los edificios en el mapa"
    )

# Mostrar preview de cómo se verán los edificios
st.info(f"📐 **Vista previa de escala:** Ancho × {multiplicador_ancho:.1f}, Altura × {multiplicador_altura:.1f}")
st.markdown('</div>', unsafe_allow_html=True)

# Definir colores de edificios
colores_edificios = {
    'residencial': 'blue',
    'comercial': 'orange', 
    'industrial': 'red',
    'rascacielos': 'purple'
}

# Posiciones predefinidas para los iconos de defensa
posiciones_defensa = [
    {'x': 10, 'y': 90, 'tipo': 'laser'},
    {'x': 90, 'y': 90, 'tipo': 'nuclear'},
    {'x': 10, 'y': 10, 'tipo': 'tractor'},
    {'x': 90, 'y': 10, 'tipo': 'escudo'}
]

# Generar mapa de ciudad CON DENSIDAD
def generar_ciudad(densidad):
    """Genera una ciudad aleatoria con densidad controlada"""
    ciudad = {
        'edificios': [],
        'parques': [],
        'carreteras': [],
        'zonas_residenciales': [],
        'defensas': posiciones_defensa,
        'densidad': densidad
    }
    
    # Calcular número de edificios basado en densidad (10 a 100 edificios)
    num_edificios = int(densidad * 1.2)  # 10-80 edificios según densidad
    num_edificios = max(10, min(80, num_edificios))  # Limitar entre 10 y 80
    
    # Calcular número de parques (inversamente proporcional a densidad)
    num_parques = max(1, 6 - int(densidad / 20))  # 5 parques en baja densidad, 1 en alta
    
    # Generar edificios (posición x, posición y, tipo, altura)
    for _ in range(num_edificios):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        
        # Distribución de tipos según densidad
        if densidad <= 25:  # Rural
            tipos = ['residencial'] * 70 + ['comercial'] * 20 + ['industrial'] * 10
        elif densidad <= 50:  # Suburbana
            tipos = ['residencial'] * 60 + ['comercial'] * 25 + ['industrial'] * 10 + ['rascacielos'] * 5
        elif densidad <= 75:  # Urbana
            tipos = ['residencial'] * 50 + ['comercial'] * 30 + ['industrial'] * 10 + ['rascacielos'] * 10
        else:  # Metrópolis
            tipos = ['residencial'] * 40 + ['comercial'] * 30 + ['industrial'] * 10 + ['rascacielos'] * 20
        
        tipo = random.choice(tipos)
        
        # Alturas según densidad (ciudades densas tienen edificios más altos)
        factor_altura = 1 + (densidad / 100)  # 1x a 2x según densidad
        
        if tipo == 'residencial':
            altura_base = random.uniform(1, 3) * factor_altura
        elif tipo == 'comercial':
            altura_base = random.uniform(2, 4) * factor_altura
        elif tipo == 'industrial':
            altura_base = random.uniform(3, 6) * factor_altura
        else:  # rascacielos
            altura_base = random.uniform(5, 10) * factor_altura  # Más altos en ciudades densas
        
        ciudad['edificios'].append({'x': x, 'y': y, 'tipo': tipo, 'altura_base': altura_base})
    
    # Generar parques (menos parques en alta densidad)
    for _ in range(num_parques):
        x = random.uniform(10, 90)
        y = random.uniform(10, 90)
        tamaño_base = random.uniform(5, 15)
        # Parques más pequeños en alta densidad
        tamaño = tamaño_base * (1 - (densidad / 200))  
        ciudad['parques'].append({'x': x, 'y': y, 'tamaño': tamaño})
    
    # Generar carreteras principales (más carreteras en alta densidad)
    ciudad['carreteras'] = [
        {'x1': 0, 'y1': 25, 'x2': 100, 'y2': 25, 'ancho': 2},
        {'x1': 0, 'y1': 50, 'x2': 100, 'y2': 50, 'ancho': 2},
        {'x1': 0, 'y1': 75, 'x2': 100, 'y2': 75, 'ancho': 2},
        {'x1': 25, 'y1': 0, 'x2': 25, 'y2': 100, 'ancho': 2},
        {'x1': 50, 'y1': 0, 'x2': 50, 'y2': 100, 'ancho': 2},
        {'x1': 75, 'y1': 0, 'x2': 75, 'y2': 100, 'ancho': 2}
    ]
    
    # Agregar carreteras adicionales en alta densidad
    if densidad > 75:
        ciudad['carreteras'].extend([
            {'x1': 0, 'y1': 10, 'x2': 100, 'y2': 10, 'ancho': 1.5},
            {'x1': 0, 'y1': 90, 'x2': 100, 'y2': 90, 'ancho': 1.5},
            {'x1': 10, 'y1': 0, 'x2': 10, 'y2': 100, 'ancho': 1.5},
            {'x1': 90, 'y1': 0, 'x2': 90, 'y2': 100, 'ancho': 1.5}
        ])
    
    return ciudad

# Función para dibujar iconos de defensa
def dibujar_icono_defensa(ax, x, y, tipo_defensa, activa):
    """Dibuja un icono de defensa en el mapa"""
    color = 'green' if activa else 'red'
    alpha = 0.8 if activa else 0.3
    tamaño = 3
    
    if tipo_defensa == 'laser':
        # Icono de láser (rayo)
        puntos_laser = np.array([
            [x, y + tamaño],
            [x - tamaño/2, y - tamaño/2],
            [x - tamaño/4, y - tamaño/4],
            [x + tamaño/4, y - tamaño/4],
            [x + tamaño/2, y - tamaño/2]
        ])
        poligono = Polygon(puntos_laser, closed=True, facecolor=color, alpha=alpha, edgecolor='black')
        ax.add_patch(poligono)
        ax.text(x, y - tamaño*0.8, '🔫', fontsize=12, ha='center', va='center')
        
    elif tipo_defensa == 'nuclear':
        # Icono nuclear (explosión)
        for i in range(8):
            angulo = i * 45
            radio = tamaño * 0.8
            x1 = x + radio * np.cos(np.radians(angulo))
            y1 = y + radio * np.sin(np.radians(angulo))
            ax.plot([x, x1], [y, y1], color=color, linewidth=2, alpha=alpha)
        circulo = Circle((x, y), tamaño*0.3, facecolor=color, alpha=alpha, edgecolor='black')
        ax.add_patch(circulo)
        ax.text(x, y, '☢️', fontsize=10, ha='center', va='center')
        
    elif tipo_defensa == 'tractor':
        # Icono de tractor gravitatorio (campo de fuerza)
        circulo = Circle((x, y), tamaño, fill=False, linewidth=2, 
                        edgecolor=color, alpha=alpha, linestyle='--')
        ax.add_patch(circulo)
        circulo_pequeño = Circle((x, y), tamaño*0.3, facecolor=color, alpha=alpha, edgecolor='black')
        ax.add_patch(circulo_pequeño)
        ax.text(x, y, '🛰️', fontsize=10, ha='center', va='center')
        
    elif tipo_defensa == 'escudo':
        # Icono de escudo (protección)
        puntos_escudo = np.array([
            [x, y + tamaño],
            [x - tamaño, y - tamaño/2],
            [x + tamaño, y - tamaño/2]
        ])
        poligono = Polygon(puntos_escudo, closed=True, facecolor=color, alpha=alpha, edgecolor='black')
        ax.add_patch(poligono)
        ax.text(x, y, '🛡️', fontsize=10, ha='center', va='center')
    
    # Etiqueta del sistema
    nombres = {
        'laser': 'Láser',
        'nuclear': 'Nuclear', 
        'tractor': 'Tractor',
        'escudo': 'Escudo'
    }
    ax.text(x, y - tamaño*1.5, nombres[tipo_defensa], 
            fontsize=8, ha='center', va='center', 
            color=color, weight='bold' if activa else 'normal')

# Función de simulación mejorada CON DENSIDAD
def simular_impacto_ciudad(diametro, velocidad, angulo, punto_impacto_x, punto_impacto_y, defensas, densidad):
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
    ciudad = generar_ciudad(densidad)
    edificios_destruidos = 0
    edificios_danados = 0
    
    for edificio in ciudad['edificios']:
        distancia = np.sqrt((edificio['x'] - punto_impacto_x)**2 + (edificio['y'] - punto_impacto_y)**2)
        
        if distancia <= radio_destruccion_total / 100:  # Escalar a coordenadas de ciudad
            edificios_destruidos += 1
        elif distancia <= radio_destruccion_parcial / 100:
            edificios_danados += 1
    
    # Población afectada basada en densidad
    factor_poblacion = densidad / 50.0  # 0.2x a 2x según densidad
    poblacion_afectada = int((edificios_destruidos * 50 + edificios_danados * 100) * factor_poblacion)
    
    return {
        "energia_megatones": energia_megatones,
        "energia_final": energia_final,
        "reduccion": reduccion * 100,
        "radio_destruccion_total": radio_destruccion_total,
        "radio_destruccion_parcial": radio_destruccion_parcial,
        "edificios_destruidos": edificios_destruidos,
        "edificios_danados": edificios_danados,
        "poblacion_afectada": poblacion_afectada,
        "ciudad": ciudad,
        "defensas_activas": defensas,
        "densidad_utilizada": densidad
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
                                         punto_impacto_x, punto_impacto_y, defensas, densidad_poblacion)
        
        # Mostrar resultados
        st.subheader("📊 Reporte de Impacto Urbano")
        
        # Información de densidad
        col_dens, col_edif, col_pob = st.columns(3)
        with col_dens:
            tipo_ciudad = "Rural" if densidad_poblacion <= 25 else "Suburbana" if densidad_poblacion <= 50 else "Urbana" if densidad_poblacion <= 75 else "Metrópolis"
            st.metric("Tipo de Ciudad", tipo_ciudad)
        with col_edif:
            st.metric("Total de Edificios", f"{len(resultado['ciudad']['edificios'])}")
        with col_pob:
            st.metric("Densidad Aplicada", f"{densidad_poblacion}%")
        
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
        
        # Dibujar edificios - USANDO LOS MULTIPLICADORES DE ESCALA
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
                color = colores_edificios[edificio['tipo']]
                alpha = 0.8
            
            # APLICAR MULTIPLICADORES DE ESCALA
            ancho_edificio = 1.0 * multiplicador_ancho  # Ancho base × multiplicador
            altura_edificio = edificio['altura_base'] * multiplicador_altura  # Altura base × multiplicador
            
            rect = Rectangle((edificio['x']-ancho_edificio/2, edificio['y']-0.5), 
                           ancho_edificio, altura_edificio,
                           facecolor=color, alpha=alpha,
                           edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
        
        # DIBUJAR ICONOS DE DEFENSA
        for defensa in ciudad['defensas']:
            activa = resultado['defensas_activas'][defensa['tipo']]
            dibujar_icono_defensa(ax, defensa['x'], defensa['y'], defensa['tipo'], activa)
        
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
        ax.set_title(f'Mapa de la Ciudad - Densidad: {densidad_poblacion}% - Simulación de Impacto', fontsize=16, fontweight='bold')
        ax.set_xlabel('Coordenada X')
        ax.set_ylabel('Coordenada Y')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        st.pyplot(fig)
        
        # Mostrar configuración aplicada
        col_conf1, col_conf2 = st.columns(2)
        with col_conf1:
            st.info(f"⚙️ **Configuración aplicada:** Ancho × {multiplicador_ancho:.1f}, Altura × {multiplicador_altura:.1f}")
        with col_conf2:
            st.info(f"👥 **Densidad aplicada:** {densidad_poblacion}% - {tipo_ciudad}")
        
        # Evaluación de resultados
        st.subheader("📈 Evaluación de Daños")
        
        # Umbrales ajustados por densidad
        umbral_catastrofe = 15 + (densidad_poblacion / 10)  # 17 a 25 según densidad
        umbral_grave = 8 + (densidad_poblacion / 15)        # 9 a 15 según densidad
        umbral_moderado = 4 + (densidad_poblacion / 20)     # 5 a 9 según densidad
        
        if resultado['edificios_destruidos'] > umbral_catastrofe:
            st.markdown('<div class="impact-warning">💥 CATASTROFE URBANA: Impacto devastador con destrucción masiva</div>', unsafe_allow_html=True)
            st.error(f"🚨 Se estiman {resultado['poblacion_afectada']} personas afectadas. Evacuación inmediata requerida.")
        elif resultado['edificios_destruidos'] > umbral_grave:
            st.warning("⚠️ IMPACTO GRAVE: Daños extensos en el área urbana")
            st.info(f"🏥 {resultado['poblacion_afectada']} personas requieren asistencia")
        elif resultado['edificios_destruidos'] > umbral_moderado:
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
    ciudad_ejemplo = generar_ciudad(densidad_poblacion)
    fig_ejemplo, ax_ejemplo = plt.subplots(figsize=(10, 8))
    
    # Dibujar ciudad de ejemplo
    for parque in ciudad_ejemplo['parques']:
        circle = Circle((parque['x'], parque['y']), parque['tamaño']/10, color='green', alpha=0.4)
        ax_ejemplo.add_patch(circle)
    
    for carretera in ciudad_ejemplo['carreteras']:
        ax_ejemplo.plot([carretera['x1'], carretera['x2']], 
                       [carretera['y1'], carretera['y2']], 
                       'gray', linewidth=carretera['ancho'], alpha=0.7)
    
    # EDIFICIOS CON MULTIPLICADORES DE ESCALA en la vista previa también
    for edificio in ciudad_ejemplo['edificios']:
        color = colores_edificios[edificio['tipo']]
        
        # APLICAR MULTIPLICADORES DE ESCALA
        ancho_edificio = 1.0 * multiplicador_ancho
        altura_edificio = edificio['altura_base'] * multiplicador_altura
        
        rect = Rectangle((edificio['x']-ancho_edificio/2, edificio['y']-0.5), 
                       ancho_edificio, altura_edificio,
                       facecolor=color, alpha=0.8, edgecolor='black', linewidth=0.5)
        ax_ejemplo.add_patch(rect)
    
    # DIBUJAR ICONOS DE DEFENSA EN VISTA PREVIA (mostrar todos como disponibles)
    defensas_previa = {
        "laser": defensa_laser,
        "nuclear": desviacion_nuclear,
        "tractor": tractor_gravitatorio,
        "escudo": escudo_atmosferico
    }
    
    for defensa in ciudad_ejemplo['defensas']:
        activa = defensas_previa[defensa['tipo']]
        dibujar_icono_defensa(ax_ejemplo, defensa['x'], defensa['y'], defensa['tipo'], activa)
    
    ax_ejemplo.set_xlim(0, 100)
    ax_ejemplo.set_ylim(0, 100)
    ax_ejemplo.set_aspect('equal')
    tipo_ciudad_ejemplo = "Rural" if densidad_poblacion <= 25 else "Suburbana" if densidad_poblacion <= 50 else "Urbana" if densidad_poblacion <= 75 else "Metrópolis"
    ax_ejemplo.set_title(f'Vista Previa - Ciudad {tipo_ciudad_ejemplo} (Densidad: {densidad_poblacion}%)', fontsize=14)
    ax_ejemplo.grid(True, alpha=0.3)
    
    st.pyplot(fig_ejemplo)

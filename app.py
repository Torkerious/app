import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Circle, Rectangle, Polygon, Wedge
import time
import random

# Configuración de la página
st.set_page_config(
    page_title="Simulador de Impacto - Ciudad Aurora",
    page_icon="🏙️",
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
    .district-info {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
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
    .impact-moderate {
        background: linear-gradient(45deg, #ffa500, #ffb347);
        color: black;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #ff8c00;
        font-size: 1.1rem;
    }
    .impact-serious {
        background: linear-gradient(45deg, #ff8c00, #ffa54f);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #ff4500;
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
    .energy-comparison {
        background: linear-gradient(45deg, #3742fa, #5352ed);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .saved-energy {
        background: linear-gradient(45deg, #00d2d3, #54a0ff);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 2px solid #00b894;
    }
    .recommendation-box {
        background: linear-gradient(45deg, #8e44ad, #9b59b6);
        color: white;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        border-left: 5px solid #f1c40f;
    }
    .evaluation-section {
        background: linear-gradient(45deg, #2c3e50, #34495e);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🏙️ Simulador de Impacto - Ciudad Aurora</h1>', unsafe_allow_html=True)

# Descripción de la ciudad
st.markdown("""
<div class="city-description">
<h2>🌆 Acerca de Ciudad Aurora</h2>
<p><strong>Población:</strong> 850,000 habitantes • <strong>Área:</strong> 320 km² • <strong>Fundación:</strong> 1892</p>
<p>Ciudad Aurora es una metrópolis moderna conocida por su arquitectura innovadora y planificación urbana sostenible. 
La ciudad cuenta con 6 distritos principales, cada uno con características únicas y población específica.</p>
</div>
""", unsafe_allow_html=True)

# SECCIÓN DE CONFIGURACIÓN
st.subheader("⚙️ Configuración de Simulación")

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

# Definir distritos de Ciudad Aurora
distritos_aurora = {
    'centro': {
        'nombre': 'Centro Financiero',
        'color': 'red',
        'edificios': 45,
        'poblacion': 120000,
        'descripcion': 'Rascacielos corporativos y centros comerciales',
        'x_range': (40, 60),
        'y_range': (40, 60)
    },
    'norte': {
        'nombre': 'Distrito Norte Residencial',
        'color': 'blue',
        'edificios': 35,
        'poblacion': 180000,
        'descripcion': 'Zona residencial de alta densidad',
        'x_range': (30, 70),
        'y_range': (70, 90)
    },
    'sur': {
        'nombre': 'Zona Sur Industrial',
        'color': 'orange',
        'edificios': 25,
        'poblacion': 90000,
        'descripcion': 'Área industrial y logística',
        'x_range': (20, 80),
        'y_range': (10, 30)
    },
    'este': {
        'nombre': 'Este Comercial',
        'color': 'green',
        'edificios': 30,
        'poblacion': 150000,
        'descripcion': 'Centros comerciales y oficinas',
        'x_range': (70, 90),
        'y_range': (30, 70)
    },
    'oeste': {
        'nombre': 'Oeste Histórico',
        'color': 'purple',
        'edificios': 20,
        'poblacion': 80000,
        'descripcion': 'Edificios históricos y culturales',
        'x_range': (10, 30),
        'y_range': (30, 70)
    },
    'rio': {
        'nombre': 'Zona Río',
        'color': 'cyan',
        'edificios': 15,
        'poblacion': 60000,
        'descripcion': 'Área recreativa y parques junto al río',
        'x_range': (50, 80),
        'y_range': (80, 95)
    }
}

# Puntos de interés específicos
puntos_interes = [
    {'nombre': 'Torre Aurora', 'x': 50, 'y': 50, 'tipo': 'rascacielos', 'altura': 12},
    {'nombre': 'Ayuntamiento', 'x': 45, 'y': 45, 'tipo': 'comercial', 'altura': 6},
    {'nombre': 'Hospital Central', 'x': 55, 'y': 55, 'tipo': 'comercial', 'altura': 8},
    {'nombre': 'Estación Central', 'x': 48, 'y': 52, 'tipo': 'comercial', 'altura': 5},
    {'nombre': 'Universidad', 'x': 35, 'y': 65, 'tipo': 'comercial', 'altura': 7},
    {'nombre': 'Parque Central', 'x': 52, 'y': 58, 'tipo': 'parque', 'tamaño': 8},
    {'nombre': 'Plaza Histórica', 'x': 25, 'y': 50, 'tipo': 'parque', 'tamaño': 6},
    {'nombre': 'Puente Río', 'x': 65, 'y': 85, 'tipo': 'carretera', 'ancho': 3},
]

# Posiciones predefinidas para los iconos de defensa
posiciones_defensa = [
    {'x': 15, 'y': 85, 'tipo': 'laser', 'nombre': 'Base Norte'},
    {'x': 85, 'y': 85, 'tipo': 'nuclear', 'nombre': 'Base Este'},
    {'x': 15, 'y': 15, 'tipo': 'tractor', 'nombre': 'Base Sur'},
    {'x': 85, 'y': 15, 'tipo': 'escudo', 'nombre': 'Base Oeste'}
]

# Función para formatear energía en formato legible
def formatear_energia(energia_megatones):
    """Convierte la energía a formato legible con comparaciones"""
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

# Función para obtener comparación histórica
def obtener_comparacion_historica(energia_megatones):
    """Devuelve una comparación con eventos históricos"""
    if energia_megatones >= 10000:
        return "💥 MÁS QUE EL ASTEROIDE QUE EXTINGUIÓ A LOS DINOSAURIOS", "10,000 MT"
    elif energia_megatones >= 1000:
        return "☄️ Comparable al Evento de Tunguska multiplicado x50", "1,000 MT"
    elif energia_megatones >= 100:
        return "💣 5 veces la bomba Tsar (la más poderosa jamás detonada)", "100 MT"
    elif energia_megatones >= 50:
        return "💣 Similar a la bomba Tsar (50 MT)", "50 MT"
    elif energia_megatones >= 10:
        return "💣 Como 500 bombas de Hiroshima", "10 MT"
    elif energia_megatones >= 1:
        return "💣 Como 50 bombas de Hiroshima", "1 MT"
    elif energia_megatones >= 0.5:
        return "💣 Similar a la bomba de Hiroshima", "0.5 MT"
    else:
        return "💣 Menor que una bomba nuclear típica", "0.1 MT"

# Generar mapa de Ciudad Aurora
def generar_ciudad_aurora():
    """Genera el mapa específico de Ciudad Aurora"""
    ciudad = {
        'edificios': [],
        'parques': [],
        'carreteras': [],
        'distritos': distritos_aurora,
        'defensas': posiciones_defensa,
        'puntos_interes': puntos_interes
    }
    
    # Generar carreteras principales
    ciudad['carreteras'] = [
        # Carreteras horizontales
        {'x1': 0, 'y1': 50, 'x2': 100, 'y2': 50, 'ancho': 3, 'nombre': 'Avenida Central'},
        {'x1': 0, 'y1': 25, 'x2': 100, 'y2': 25, 'ancho': 2, 'nombre': 'Avenida Sur'},
        {'x1': 0, 'y1': 75, 'x2': 100, 'y2': 75, 'ancho': 2, 'nombre': 'Avenida Norte'},
        # Carreteras verticales
        {'x1': 50, 'y1': 0, 'x2': 50, 'y2': 100, 'ancho': 3, 'nombre': 'Bulevar Principal'},
        {'x1': 25, 'y1': 0, 'x2': 25, 'y2': 100, 'ancho': 2, 'nombre': 'Calle Oeste'},
        {'x1': 75, 'y1': 0, 'x2': 75, 'y2': 100, 'ancho': 2, 'nombre': 'Calle Este'},
        # Anillo periférico
        {'x1': 10, 'y1': 10, 'x2': 90, 'y2': 10, 'ancho': 2, 'nombre': 'Periférico Sur'},
        {'x1': 10, 'y1': 90, 'x2': 90, 'y2': 90, 'ancho': 2, 'nombre': 'Periférico Norte'},
        {'x1': 10, 'y1': 10, 'x2': 10, 'y2': 90, 'ancho': 2, 'nombre': 'Periférico Oeste'},
        {'x1': 90, 'y1': 10, 'x2': 90, 'y2': 90, 'ancho': 2, 'nombre': 'Periférico Este'},
    ]
    
    # Generar edificios por distrito
    for distrito_id, distrito in distritos_aurora.items():
        x_min, x_max = distrito['x_range']
        y_min, y_max = distrito['y_range']
        
        for i in range(distrito['edificios']):
            x = random.uniform(x_min, x_max)
            y = random.uniform(y_min, y_max)
            
            # Determinar tipo de edificio basado en el distrito
            if distrito_id == 'centro':
                tipos = ['rascacielos'] * 50 + ['comercial'] * 30 + ['residencial'] * 20
                altura_base = random.uniform(6, 12)
            elif distrito_id == 'norte':
                tipos = ['residencial'] * 60 + ['comercial'] * 30 + ['rascacielos'] * 10
                altura_base = random.uniform(4, 8)
            elif distrito_id == 'sur':
                tipos = ['industrial'] * 60 + ['comercial'] * 30 + ['residencial'] * 10
                altura_base = random.uniform(3, 6)
            elif distrito_id == 'este':
                tipos = ['comercial'] * 50 + ['residencial'] * 30 + ['rascacielos'] * 20
                altura_base = random.uniform(5, 9)
            elif distrito_id == 'oeste':
                tipos = ['residencial'] * 70 + ['comercial'] * 20 + ['industrial'] * 10
                altura_base = random.uniform(2, 5)
            else:  # rio
                tipos = ['residencial'] * 80 + ['comercial'] * 20
                altura_base = random.uniform(2, 4)
            
            tipo = random.choice(tipos)
            ciudad['edificios'].append({
                'x': x, 'y': y, 'tipo': tipo, 'altura_base': altura_base,
                'distrito': distrito_id
            })
    
    # Agregar puntos de interés como edificios especiales
    for punto in puntos_interes:
        if punto['tipo'] == 'parque':
            ciudad['parques'].append({
                'x': punto['x'], 'y': punto['y'], 'tamaño': punto['tamaño'],
                'nombre': punto['nombre']
            })
        elif punto['tipo'] == 'carretera':
            # Ya están incluidas en carreteras principales
            pass
        else:
            ciudad['edificios'].append({
                'x': punto['x'], 'y': punto['y'], 'tipo': punto['tipo'],
                'altura_base': punto['altura'], 'es_punto_interes': True,
                'nombre': punto['nombre']
            })
    
    return ciudad

# Función para dibujar iconos de defensa
def dibujar_icono_defensa(ax, x, y, tipo_defensa, activa, nombre):
    """Dibuja un icono de defensa en el mapa"""
    color = 'green' if activa else 'red'
    alpha = 0.8 if activa else 0.3
    tamaño = 3
    
    if tipo_defensa == 'laser':
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
        circulo = Circle((x, y), tamaño, fill=False, linewidth=2, 
                        edgecolor=color, alpha=alpha, linestyle='--')
        ax.add_patch(circulo)
        circulo_pequeño = Circle((x, y), tamaño*0.3, facecolor=color, alpha=alpha, edgecolor='black')
        ax.add_patch(circulo_pequeño)
        ax.text(x, y, '🛰️', fontsize=10, ha='center', va='center')
        
    elif tipo_defensa == 'escudo':
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
    ax.text(x, y - tamaño*1.5, f"{nombres[tipo_defensa]}\n{nombre}", 
            fontsize=7, ha='center', va='center', 
            color=color, weight='bold' if activa else 'normal')

# Función de simulación para Ciudad Aurora
def simular_impacto_aurora(diametro, velocidad, angulo, punto_impacto_x, punto_impacto_y, defensas):
    # Cálculos del impacto
    masa = diametro ** 3 * 800
    energia_joules = 0.5 * masa * (velocidad * 1000) ** 2
    energia_megatones = energia_joules / (4.184e15)
    
    # Radio de destrucción
    radio_destruccion_total = diametro * 15
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
    
    # Calcular daños a la ciudad
    ciudad = generar_ciudad_aurora()
    edificios_destruidos = 0
    edificios_danados = 0
    distritos_afectados = {}
    
    for edificio in ciudad['edificios']:
        distancia = np.sqrt((edificio['x'] - punto_impacto_x)**2 + (edificio['y'] - punto_impacto_y)**2)
        distrito = edificio['distrito']
        
        if distrito not in distritos_afectados:
            distritos_afectados[distrito] = {'destruidos': 0, 'danados': 0}
        
        if distancia <= radio_destruccion_total / 100:
            edificios_destruidos += 1
            distritos_afectados[distrito]['destruidos'] += 1
        elif distancia <= radio_destruccion_parcial / 100:
            edificios_danados += 1
            distritos_afectados[distrito]['danados'] += 1
    
    # Calcular población afectada basada en distritos
    poblacion_afectada = 0
    for distrito_id, datos in distritos_afectados.items():
        distrito = distritos_aurora[distrito_id]
        porcentaje_afectado = (datos['destruidos'] + datos['danados'] * 0.3) / distrito['edificios']
        poblacion_afectada += int(distrito['poblacion'] * porcentaje_afectado)
    
    return {
        "energia_megatones": energia_megatones,
        "energia_final": energia_final,
        "energia_mitigada": energia_mitigada,
        "reduccion": reduccion * 100,
        "radio_destruccion_total": radio_destruccion_total,
        "radio_destruccion_parcial": radio_destruccion_parcial,
        "edificios_destruidos": edificios_destruidos,
        "edificios_danados": edificios_danados,
        "poblacion_afectada": poblacion_afectada,
        "distritos_afectados": distritos_afectados,
        "ciudad": ciudad,
        "defensas_activas": defensas
    }

# Sidebar para controles
with st.sidebar:
    st.header("🎮 Controles de Simulación")
    
    # Parámetros del meteorito
    st.subheader("🌠 Meteorito")
    diametro = st.slider("Diámetro (metros)", 10, 2000, 500)
    velocidad = st.slider("Velocidad (km/s)", 5, 70, 25)
    angulo_impacto = st.slider("Ángulo de impacto", 0, 90, 45)
    
    st.subheader("🎯 Punto de Impacto en Ciudad Aurora")
    punto_impacto_x = st.slider("Coordenada X", 0, 100, 50)
    punto_impacto_y = st.slider("Coordenada Y", 0, 100, 50)
    
    # Mostrar información del área seleccionada
    distrito_impacto = "Área no designada"
    for distrito_id, distrito in distritos_aurora.items():
        x_min, x_max = distrito['x_range']
        y_min, y_max = distrito['y_range']
        if x_min <= punto_impacto_x <= x_max and y_min <= punto_impacto_y <= y_max:
            distrito_impacto = distrito['nombre']
            break
    
    st.info(f"**Área seleccionada:** {distrito_impacto}")
    
    # Estrategias de mitigación
    st.header("🛡️ Estrategias de Mitigación")
    defensa_laser = st.checkbox("Sistema de Defensa Láser", help="Láseres orbitales que vaporizan parte del meteorito")
    desviacion_nuclear = st.checkbox("Desviación Nuclear", help="Explosiones nucleares para alterar trayectoria")
    tractor_gravitatorio = st.checkbox("Tractor Gravitatorio", help="Nave que usa gravedad para desviación suave")
    escudo_atmosferico = st.checkbox("Escudo Atmosférico", help="Refuerzo de defensas atmosféricas")

# Información de los distritos
st.subheader("🗺️ Distritos de Ciudad Aurora")

cols = st.columns(3)
for i, (distrito_id, distrito) in enumerate(distritos_aurora.items()):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="district-info">
        <h4>📍 {distrito['nombre']}</h4>
        <p>🏢 {distrito['edificios']} edificios</p>
        <p>👥 {distrito['poblacion']:,} habitantes</p>
        <p>{distrito['descripcion']}</p>
        </div>
        """, unsafe_allow_html=True)

# Inicializar variable resultado
resultado = None

# Botón de simulación principal
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🌠 SIMULAR IMPACTO EN CIUDAD AURORA", use_container_width=True, type="primary"):
        
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
        
        resultado = simular_impacto_aurora(diametro, velocidad, angulo_impacto, 
                                         punto_impacto_x, punto_impacto_y, defensas)
        
        # Mostrar resultados
        st.subheader("📊 Reporte de Impacto - Ciudad Aurora")
        
        # SECCIÓN DE ENERGÍA
        st.markdown('<div class="energy-section">', unsafe_allow_html=True)
        
        valor_original, unidad_original = formatear_energia(resultado['energia_megatones'])
        valor_impacto, unidad_impacto = formatear_energia(resultado['energia_final'])
        valor_mitigada, unidad_mitigada = formatear_energia(resultado['energia_mitigada'])
        comparacion, referencia = obtener_comparacion_historica(resultado['energia_megatones'])
        
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
        
        st.markdown(f"""
        <div class="saved-energy">
        <h4>🎯 EFECTO DE LAS DEFENSAS:</h4>
        <p>Se <strong>evitaron {valor_mitigada} {unidad_mitigada}</strong> de energía destructiva.</p>
        <p>Esto representa una <strong>reducción del {resultado['reduccion']:.1f}%</strong> en la energía del impacto.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="energy-comparison">', unsafe_allow_html=True)
        st.markdown(f"**📊 COMPARACIÓN HISTÓRICA:** {comparacion}")
        st.markdown(f"*Referencia: {referencia}*")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Edificios Destruidos", f"{resultado['edificios_destruidos']}")
        with col2:
            st.metric("Edificios Dañados", f"{resultado['edificios_danados']}")
        with col3:
            st.metric("Población Afectada", f"{resultado['poblacion_afectada']:,}")
        with col4:
            st.metric("Radio Destrucción", f"{resultado['radio_destruccion_total']:.0f}m")
        
        # Visualización del mapa de impacto
        st.subheader("🗺️ Mapa de Impacto - Ciudad Aurora")
        
        fig, ax = plt.subplots(figsize=(14, 12))
        
        # Dibujar distritos con colores de fondo
        for distrito_id, distrito in distritos_aurora.items():
            x_min, x_max = distrito['x_range']
            y_min, y_max = distrito['y_range']
            ancho = x_max - x_min
            alto = y_max - y_min
            
            rect = Rectangle((x_min, y_min), ancho, alto, 
                           facecolor=distrito['color'], alpha=0.2,
                           edgecolor=distrito['color'], linewidth=2)
            ax.add_patch(rect)
            
            # Etiqueta del distrito
            ax.text((x_min + x_max)/2, (y_min + y_max)/2, 
                   distrito['nombre'], ha='center', va='center',
                   fontsize=9, weight='bold', color=distrito['color'])
        
        # Dibujar carreteras
        for carretera in resultado['ciudad']['carreteras']:
            ax.plot([carretera['x1'], carretera['x2']], 
                   [carretera['y1'], carretera['y2']], 
                   'gray', linewidth=carretera['ancho'], alpha=0.7)
        
        # Dibujar edificios
        colores_tipos = {'residencial': 'blue', 'comercial': 'orange', 
                        'industrial': 'red', 'rascacielos': 'purple'}
        
        for edificio in resultado['ciudad']['edificios']:
            distancia = np.sqrt((edificio['x'] - punto_impacto_x)**2 + (edificio['y'] - punto_impacto_y)**2)
            
            # Determinar estado del edificio
            if distancia <= resultado['radio_destruccion_total'] / 100:
                color = 'black'
                alpha = 0.3
            elif distancia <= resultado['radio_destruccion_parcial'] / 100:
                color = 'red'
                alpha = 0.6
            else:
                color = colores_tipos[edificio['tipo']]
                alpha = 0.8
            
            ancho_edificio = 1.0 * multiplicador_ancho
            altura_edificio = edificio['altura_base'] * multiplicador_altura
            
            rect = Rectangle((edificio['x']-ancho_edificio/2, edificio['y']-0.5), 
                           ancho_edificio, altura_edificio,
                           facecolor=color, alpha=alpha,
                           edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            
            # Marcar puntos de interés
            if edificio.get('es_punto_interes'):
                ax.plot(edificio['x'], edificio['y'], 's', markersize=8, 
                       color='gold', markeredgecolor='black')
                ax.text(edificio['x'], edificio['y'] + 2, edificio['nombre'],
                       fontsize=6, ha='center', va='bottom', weight='bold')
        
        # DIBUJAR ICONOS DE DEFENSA
        for defensa in resultado['ciudad']['defensas']:
            activa = resultado['defensas_activas'][defensa['tipo']]
            dibujar_icono_defensa(ax, defensa['x'], defensa['y'], 
                                defensa['tipo'], activa, defensa['nombre'])
        
        # Dibujar zona de impacto
        impacto = Circle((punto_impacto_x, punto_impacto_y), 
                        resultado['radio_destruccion_total'] / 100,
                        fill=False, color='red', linewidth=3, linestyle='--',
                        label='Zona de Destrucción Total')
        ax.add_patch(impacto)
        
        danos_parciales = Circle((punto_impacto_x, punto_impacto_y),
                               resultado['radio_destruccion_parcial'] / 100,
                               fill=False, color='orange', linewidth=2, linestyle=':',
                               label='Zona de Daños Parciales')
        ax.add_patch(danos_parciales)
        
        # Punto de impacto
        ax.plot(punto_impacto_x, punto_impacto_y, 'ro', markersize=15, 
               label='Punto de Impacto', markeredgecolor='black')
        
        # Configuración del gráfico
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')
        ax.set_title('Ciudad Aurora - Simulación de Impacto de Meteorito', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Coordenada X')
        ax.set_ylabel('Coordenada Y')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        st.pyplot(fig)
        
        # Mostrar configuración aplicada
        st.info(f"⚙️ **Configuración aplicada:** Ancho × {multiplicador_ancho:.1f}, Altura × {multiplicador_altura:.1f}")
        
        # EVALUACIÓN DE DAÑOS POR DISTRITO
        st.markdown("---")
        st.markdown('<div class="evaluation-section">', unsafe_allow_html=True)
        st.subheader("📈 Evaluación de Daños por Distrito")
        
        # Mostrar daños por distrito
        cols_distritos = st.columns(3)
        for i, (distrito_id, datos) in enumerate(resultado['distritos_afectados'].items()):
            distrito = distritos_aurora[distrito_id]
            with cols_distritos[i % 3]:
                porcentaje_dano = (datos['destruidos'] + datos['danados'] * 0.5) / distrito['edificios'] * 100
                st.metric(
                    f"📍 {distrito['nombre']}",
                    f"{datos['destruidos']} dest. / {datos['danados']} dañ.",
                    delta=f"{porcentaje_dano:.1f}% afectado"
                )
        
        # Evaluación general
        total_edificios = sum([d['edificios'] for d in distritos_aurora.values()])
        porcentaje_destruccion = (resultado['edificios_destruidos'] / total_edificios) * 100
        
        if porcentaje_destruccion > 30:
            st.markdown("""
            <div class="impact-warning">
            <h3>💥 CATASTROFE URBANA: IMPACTO DEVASTADOR</h3>
            <p><strong>Nivel de Emergencia:</strong> MÁXIMO - Respuesta de emergencia total requerida</p>
            <p><strong>Impacto:</strong> Destrucción masiva de infraestructura crítica en múltiples distritos</p>
            <p><strong>Población afectada:</strong> {:,} personas requieren evacuación inmediata</p>
            </div>
            """.format(resultado['poblacion_afectada']), unsafe_allow_html=True)
            
        elif porcentaje_destruccion > 15:
            st.markdown("""
            <div class="impact-serious">
            <h3>⚠️ IMPACTO GRAVE: DAÑOS EXTENSOS</h3>
            <p><strong>Nivel de Emergencia:</strong> ALTO - Respuesta regional requerida</p>
            <p><strong>Impacto:</strong> Daños significativos en infraestructura esencial</p>
            <p><strong>Población afectada:</strong> {:,} personas requieren asistencia</p>
            </div>
            """.format(resultado['poblacion_afectada']), unsafe_allow_html=True)
            
        elif porcentaje_destruccion > 5:
            st.markdown("""
            <div class="impact-moderate">
            <h3>🔶 IMPACTO MODERADO: DAÑOS LOCALIZADOS</h3>
            <p><strong>Nivel de Emergencia:</strong> MEDIO - Respuesta local coordinada</p>
            <p><strong>Impacto:</strong> Daños en área específica, servicios esenciales operativos</p>
            <p><strong>Población afectada:</strong> {:,} personas requieren asistencia temporal</p>
            </div>
            """.format(resultado['poblacion_afectada']), unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="mitigation-success">
            <h3>✅ IMPACTO CONTROLADO: SITUACIÓN MANEJABLE</h3>
            <p><strong>Nivel de Emergencia:</strong> BAJO - Respuesta local normal</p>
            <p><strong>Impacto:</strong> Daños menores, infraestructura principal intacta</p>
            <p><strong>Efectividad de defensas:</strong> {:.1f}% de reducción del daño</p>
            </div>
            """.format(resultado['reduccion']), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Mostrar mapa de referencia si no hay simulación
if resultado is None:
    st.info("🎯 **Instrucciones:** Ajusta los parámetros en el panel lateral y haz clic en 'SIMULAR IMPACTO EN CIUDAD AURORA' para ver los efectos en la ciudad.")
    
    # Mostrar ciudad de ejemplo
    ciudad_ejemplo = generar_ciudad_aurora()
    fig_ejemplo, ax_ejemplo = plt.subplots(figsize=(12, 10))
    
    # Dibujar distritos
    for distrito_id, distrito in distritos_aurora.items():
        x_min, x_max = distrito['x_range']
        y_min, y_max = distrito['y_range']
        ancho = x_max - x_min
        alto = y_max - y_min
        
        rect = Rectangle((x_min, y_min), ancho, alto, 
                       facecolor=distrito['color'], alpha=0.3,
                       edgecolor=distrito['color'], linewidth=2)
        ax_ejemplo.add_patch(rect)
        
        ax_ejemplo.text((x_min + x_max)/2, (y_min + y_max)/2, 
                       distrito['nombre'], ha='center', va='center',
                       fontsize=10, weight='bold', color=distrito['color'])
    
    # Dibujar carreteras
    for carretera in ciudad_ejemplo['carreteras']:
        ax_ejemplo.plot([carretera['x1'], carretera['x2']], 
                       [carretera['y1'], carretera['y2']], 
                       'gray', linewidth=carretera['ancho'], alpha=0.7)
    
    # Dibujar algunos edificios de ejemplo
    for i, edificio in enumerate(ciudad_ejemplo['edificios'][:50]):  # Solo algunos para vista previa
        color = colores_tipos[edificio['tipo']]
        ancho_edificio = 1.0 * multiplicador_ancho
        altura_edificio = edificio['altura_base'] * multiplicador_altura
        
        rect = Rectangle((edificio['x']-ancho_edificio/2, edificio['y']-0.5), 
                       ancho_edificio, altura_edificio,
                       facecolor=color, alpha=0.7, edgecolor='black', linewidth=0.5)
        ax_ejemplo.add_patch(rect)
    
    ax_ejemplo.set_xlim(0, 100)
    ax_ejemplo.set_ylim(0, 100)
    ax_ejemplo.set_aspect('equal')
    ax_ejemplo.set_title('Ciudad Aurora - Mapa de Referencia', fontsize=16, fontweight='bold')
    ax_ejemplo.set_xlabel('Coordenada X')
    ax_ejemplo.set_ylabel('Coordenada Y')
    ax_ejemplo.grid(True, alpha=0.3)
    
    st.pyplot(fig_ejemplo)

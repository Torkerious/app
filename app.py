import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# Configuración de la página
st.set_page_config(
    page_title="Simulador de Impacto de Meteoritos",
    page_icon="🌠",
    layout="wide"
)

# CSS personalizado para mejor apariencia
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
    }
    .impact-warning {
        background-color: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .mitigation-success {
        background-color: #44ff44;
        color: black;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🌠 Simulador de Impacto de Meteoritos</h1>', unsafe_allow_html=True)

# Sidebar para controles
with st.sidebar:
    st.header("🎮 Controles de Simulación")
    
    # Parámetros del meteorito
    diametro = st.slider("Diámetro del meteorito (metros)", 10, 5000, 100)
    velocidad = st.slider("Velocidad (km/s)", 5, 70, 20)
    angulo_impacto = st.slider("Ángulo de impacto (grados)", 0, 90, 45)
    composicion = st.selectbox("Composición", ["Roca", "Hierro", "Hielo"])
    
    # Estrategias de mitigación
    st.header("🛡️ Estrategias de Mitigación")
    defensa_laser = st.checkbox("Sistema de Defensa Láser")
    desviacion_nuclear = st.checkbox("Desviación Nuclear")
    tractor_gravitatorio = st.checkbox("Tractor Gravitatorio")
    escudo_atmosferico = st.checkbox("Reforzar Escudo Atmosférico")

# Función de simulación
def simular_impacto(diametro, velocidad, angulo, composicion, defensas):
    # Cálculos simplificados del impacto
    masa = diametro ** 3 * (1000 if composicion == "Hierro" else 500 if composicion == "Roca" else 300)
    energia = 0.5 * masa * (velocidad * 1000) ** 2  # En joules
    energia_megatones = energia / (4.184e15)  # Convertir a megatones
    
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
    
    energia_final = energia_megatones * (1 - reduccion)
    
    return {
        "energia_megatones": energia_megatones,
        "energia_final": energia_final,
        "reduccion": reduccion * 100,
        "crater_diametro": diametro * 20 * (1 - reduccion * 0.5)
    }

# Botón de simulación
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Ejecutar Simulación", use_container_width=True):
        
        # Mostrar animación de carga
        with st.spinner("Simulando trayectoria del meteorito..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
        
        # Ejecutar simulación
        defensas = {
            "laser": defensa_laser,
            "nuclear": desviacion_nuclear,
            "tractor": tractor_gravitatorio,
            "escudo": escudo_atmosferico
        }
        
        resultado = simular_impacto(diametro, velocidad, angulo_impacto, composicion, defensas)
        
        # Mostrar resultados
        st.subheader("📊 Resultados de la Simulación")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Energía del Impacto", f"{resultado['energia_megatones']:.2f} MT")
            st.metric("Diámetro del Cráter", f"{resultado['crater_diametro']:.0f} m")
            
        with col2:
            st.metric("Energía Mitigada", f"{resultado['energia_final']:.2f} MT")
            st.metric("Reducción del Daño", f"{resultado['reduccion']:.1f}%")
        
        # Gráfico de impacto
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Simular cráter
        x = np.linspace(-resultado['crater_diametro']/2, resultado['crater_diametro']/2, 100)
        y = -((2*x/resultado['crater_diametro'])**2) * resultado['crater_diametro']/4
        
        ax.fill_between(x, y, -resultado['crater_diametro']/2, alpha=0.7, color='brown')
        ax.plot(x, y, 'k-', linewidth=2)
        ax.set_title(f'Cráter de Impacto - Diámetro: {resultado["crater_diametro"]:.0f}m')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
        
        # Evaluación de resultados
        if resultado['energia_final'] > 10:
            st.markdown('<div class="impact-warning">⚠️ ALTO PELIGO: Impacto catastrófico probable</div>', unsafe_allow_html=True)
            st.error("💥 Se requiere acción inmediata y estrategias adicionales")
        elif resultado['energia_final'] > 1:
            st.warning("⚠️ PELIGRO MODERADO: Daños significativos esperados")
        else:
            st.markdown('<div class="mitigation-success">✅ SITUACIÓN CONTROLADA: Impacto mitigado exitosamente</div>', unsafe_allow_html=True)
            st.success("🎉 ¡Las estrategias de mitigación han funcionado!")

# Sección educativa
st.markdown("---")
st.header("📚 Estrategias de Mitigación Explicadas")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("🔫 Defensa Láser")
    st.write("Sistema de láseres orbitales que vaporizan parte del meteorito")
    
with col2:
    st.subheader("☢️ Desviación Nuclear")
    st.write("Explosiones nucleares controladas para alterar la trayectoria")
    
with col3:
    st.subheader("🛰️ Tractor Gravitatorio")
    st.write("Nave espacial que usa gravedad para desviar lentamente el objeto")
    
with col4:
    st.subheader("🛡️ Escudo Atmosférico")
    st.write("Refuerzo de sistemas de defensa atmosférica existentes")

# Información adicional
with st.expander("🔍 Más información sobre impactos de meteoritos"):
    st.write("""
    **Datos interesantes:**
    - El meteorito de Chelyabinsk (2013) liberó ~500 kilotones de energía
    - El evento de Tunguska (1908) liberó ~10-15 megatones
    - Los sistemas de detección temprana son cruciales para la defensa planetaria
    """)

# Ejecutar con: streamlit run simulador_meteoritos.py

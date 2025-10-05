import streamlit as st
import streamlit.components.v1 as components
import os

# --- Configuración de Rutas de Archivo (Referenciando a la Raíz) ---

# Rutas locales (solo para la verificación de existencia en Python)
MODELO_STL_PATH = "Earth.stl" 
TEXTURA_PATH = "earth_texture.jpg" 

# URLs directas para el código JavaScript (asume que están en la raíz de la app)
MODEL_URL = "Earth.stl"
TEXTURE_URL = "earth_texture.jpg"


# --- 1. Configuración de Streamlit y Estado ---
st.set_page_config(layout="wide")
st.title("Visor 3D con Textura (Three.js/HTML) 🌎")

# Estado para controlar la adición de objetos de experimentación
if 'show_cube' not in st.session_state:
    st.session_state.show_cube = False
if 'cube_size' not in st.session_state:
    st.session_state.cube_size = 10.0


# --- 2. HTML y JavaScript para el Visor 3D (Three.js) ---

def generate_threejs_viewer(model_url, texture_url, show_cube, cube_size):
    """
    Genera el código HTML/JS que configura el visor Three.js.
    """
    # Verificación de archivos en Python (solo para dar un error descriptivo)
    if not os.path.exists(MODELO_STL_PATH) or not os.path.exists(TEXTURA_PATH):
        return f"""
            <p style='color:red;'>
                Error: No se encontró el modelo o la textura. 
                Asegúrate de que 'Earth.stl' y 'earth_texture.jpg' 
                están en la misma carpeta que 'app.py'.
            </p>
        """
    
    # El JavaScript está contenido en la variable HTML_CODE
    HTML_CODE = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Three.js STL Viewer</title>
        <style>
            body {{ margin: 0; }}
            canvas {{ display: block; }}
        </style>
    </head>
    <body>
        <div id="container" style="width: 100%; height: 600px;"></div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>

        <script>
            // --- Configuración de la Escena ---
            let scene, camera, renderer, controls;
            const container = document.getElementById('container');
            const modelURL = '{model_url}'; // Referencia directa a Earth.stl
            const textureURL = '{texture_url}'; // Referencia directa a earth_texture.jpg
            const showCube = {str(show_cube).lower()};
            const cubeSize = {cube_size};

            function init() {{
                // 1. Scene
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0xFFFFFF); 

                // 2. Camera
                camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 10000);
                
                // 3. Renderer
                renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(container.clientWidth, container.clientHeight);
                container.appendChild(renderer.domElement);

                // 4. Lights
                const ambientLight = new THREE.AmbientLight(0xFFFFFF, 0.9);
                scene.add(ambientLight);
                const directionalLight = new THREE.DirectionalLight(0xFFFFFF, 0.5);
                directionalLight.position.set(100, 100, 100);
                scene.add(directionalLight);

                // 5. Controls
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                
                // 6. Loaders
                const textureLoader = new THREE.TextureLoader();
                const stlLoader = new THREE.STLLoader();

                // --- Cargar Textura y Modelo ---
                textureLoader.load(textureURL, function(texture) {{
                    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
                    
                    stlLoader.load(modelURL, function(geometry) {{
                        geometry.center(); 
                        
                        const material = new THREE.MeshPhongMaterial({{
                            map: texture,
                            shininess: 10,
                            side: THREE.DoubleSide
                        }});

                        const mesh = new THREE.Mesh(geometry, material);
                        
                        // Ajuste de escala (importante para STL)
                        const box = new THREE.Box3().setFromObject(mesh);
                        const size = box.getSize(new THREE.Vector3());
                        const maxDim = Math.max(size.x, size.y, size.z);
                        const scale = 100 / maxDim; // Escalar para que el modelo tenga un tamaño razonable (100 unidades)
                        mesh.scale.set(scale, scale, scale);
                        
                        scene.add(mesh);
                        
                        // Posicionar la cámara
                        camera.position.set(maxDim * scale * 1.5, 0, 0); 
                        controls.update();
                        
                    }}, undefined, function(error) {{
                        console.error('Error al cargar el STL:', error);
                        // Fallback: Mostrar cubo azul si la Tierra falla en cargar
                    }});
                }}, undefined, function(error) {{
                     console.error('Error al cargar la textura:', error);
                     // Fallback: Si la textura falla, intentar cargar el STL con un color plano
                     stlLoader.load(modelURL, function(geometry) {{
                         geometry.center(); 
                         const material = new THREE.MeshPhongMaterial({{ color: 0xADD8E6 }}); 
                         const mesh = new THREE.Mesh(geometry, material);
                         scene.add(mesh);
                     }});
                }});

                // --- Elemento de Experimentación (Cubo) ---
                if (showCube) {{
                    const geometry = new THREE.BoxGeometry(cubeSize, cubeSize, cubeSize);
                    // Colocar el cubo al lado de la esfera de la Tierra para la experimentación
                    const cubeMaterial = new THREE.MeshBasicMaterial({{ color: 0x0000FF, transparent: true, opacity: 0.7 }});
                    const cube = new THREE.Mesh(geometry, cubeMaterial);
                    cube.position.set(cubeSize * 3, 0, 0); 
                    scene.add(cube);
                }}

                animate();
            }}

            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            
            // Lógica de redimensionamiento
            function onWindowResize() {{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }}

            window.addEventListener('resize', onWindowResize, false);

            init();
        </script>
    </body>
    </html>
    """
    return HTML_CODE

# --- 3. Renderizado y Controles de Streamlit ---

st.sidebar.header("Controles de Experimentación")

if st.sidebar.checkbox("Mostrar Cubo de Análisis", key='cube_toggle', value=st.session_state.show_cube):
    st.session_state.show_cube = True
    st.session_state.cube_size = st.sidebar.slider("Tamaño del Cubo", 1.0, 50.0, st.session_state.cube_size, 1.0)
else:
    st.session_state.show_cube = False


html_code = generate_threejs_viewer(MODEL_URL, TEXTURE_URL, st.session_state.show_cube, st.session_state.cube_size)

components.html(
    html_code,
    height=600,
    scrolling=False
)

st.markdown("""
---
**Nota:** Este visor usa **HTML/JavaScript (Three.js)**. Si el modelo de la Tierra sigue sin aparecer, el problema es que el servidor de Streamlit (o tu entorno) está bloqueando el acceso HTTP a los archivos estáticos. 
""")

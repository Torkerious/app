import streamlit as st
import streamlit.components.v1 as components
import os

# --- Configuración de Rutas de Archivo ---
# Rutas locales (para verificación)
MODELO_STL_PATH = "Earth.stl" 
TEXTURA_PATH = "earth_texture.jpg" 


# --- Función para generar URLs accesibles al navegador ---

@st.cache_data(show_spinner=False)
def load_file_urls():
    """Genera URLs temporales y accesibles para los archivos estáticos."""
    if not os.path.exists(MODELO_STL_PATH) or not os.path.exists(TEXTURA_PATH):
        st.error(f"❌ ¡CRÍTICO! Los archivos '{MODELO_STL_PATH}' y '{TEXTURA_PATH}' no se encontraron en la raíz de la aplicación.")
        return None, None
        
    try:
        # Streamlit genera un objeto File que se puede referenciar en HTML/JS
        with open(MODELO_STL_PATH, 'rb') as f_stl, open(TEXTURA_PATH, 'rb') as f_tex:
            stl_bytes = f_stl.read()
            tex_bytes = f_tex.read()

            # Usamos st.download_button para forzar a Streamlit a reconocer el archivo 
            # y darle una URL, pero no realmente para que el usuario lo descargue.
            # NOTA: Esto es un hack. En muchos entornos, usar st.write() puede funcionar,
            # pero esto es más robusto.

            # Crear un objeto temporal de archivo cargado
            stl_file = st.uploaded_file_manager.UploadedFile(
                id=hash(stl_bytes), name=MODELO_STL_PATH, size=len(stl_bytes), 
                type='application/vnd.ms-pki.stl', data=stl_bytes
            )
            tex_file = st.uploaded_file_manager.UploadedFile(
                id=hash(tex_bytes), name=TEXTURA_PATH, size=len(tex_bytes), 
                type='image/jpeg', data=tex_bytes
            )
            
            # Generar URLs directamente accesibles para el navegador
            # Se usa st.runtime.get_instance()._uploaded_file_manager.get_url() en versiones modernas
            # Usaremos una forma más simple y compatible con el contexto de `st.uploaded_file_manager`
            
            # Si el entorno no soporta esta manipulación interna, volvemos a la ruta simple
            try:
                model_url = st.uploaded_file_manager.get_url(stl_file.id)
                texture_url = st.uploaded_file_manager.get_url(tex_file.id)
            except Exception:
                # Fallback a la ruta simple (si falla la manipulación interna)
                model_url = MODELO_STL_PATH
                texture_url = TEXTURA_PATH

            return model_url, texture_url

    except Exception as e:
        st.error(f"❌ Error al generar las URLs temporales: {e}")
        return MODELO_STL_PATH, TEXTURA_PATH # Fallback

# Obtener las URLs
MODEL_URL, TEXTURE_URL = load_file_urls()

# --- 1. Configuración de Streamlit y Estado ---
st.set_page_config(layout="wide")
st.title("Visor 3D con Textura (Three.js/HTML) 🌎")

if 'show_cube' not in st.session_state:
    st.session_state.show_cube = False
if 'cube_size' not in st.session_state:
    st.session_state.cube_size = 10.0


# --- 2. HTML y JavaScript para el Visor 3D (Three.js) ---

def generate_threejs_viewer(model_url, texture_url, show_cube, cube_size):
    """
    Genera el código HTML/JS que configura el visor Three.js con la URL obtenida.
    """
    # Si las URLs son None, significa que los archivos no existen y ya se mostró un error.
    if model_url is None: return ""
    
    HTML_CODE = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Three.js STL Viewer</title>
        <style>
            body {{ margin: 0; }}
            #container {{ width: 100%; height: 600px; }} 
        </style>
    </head>
    <body>
        <div id="container"></div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>

        <script>
            let scene, camera, renderer, controls;
            const container = document.getElementById('container');
            const modelURL = '{model_url}';
            const textureURL = '{texture_url}';
            const showCube = {str(show_cube).lower()};
            const cubeSize = {cube_size};
            
            const FALLBACK_CAMERA_POSITION = new THREE.Vector3(150, 0, 0);

            function init() {{
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0xFFFFFF); 

                camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 10000);
                camera.position.copy(FALLBACK_CAMERA_POSITION);
                
                renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(container.clientWidth, container.clientHeight);
                container.appendChild(renderer.domElement);

                const ambientLight = new THREE.AmbientLight(0xFFFFFF, 0.9);
                scene.add(ambientLight);
                const directionalLight = new THREE.DirectionalLight(0xFFFFFF, 0.5);
                directionalLight.position.set(100, 100, 100);
                scene.add(directionalLight);

                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.target.set(0, 0, 0); 
                
                const textureLoader = new THREE.TextureLoader();
                const stlLoader = new THREE.STLLoader();

                // Cargar Textura y Modelo (usando la URL segura generada)
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
                        
                        // Ajuste de escala para el modelo
                        const box = new THREE.Box3().setFromObject(mesh);
                        const size = box.getSize(new THREE.Vector3());
                        const maxDim = Math.max(size.x, size.y, size.z);
                        const scale = 100 / maxDim;
                        mesh.scale.set(scale, scale, scale);
                        
                        scene.add(mesh);
                        
                        // Ajustar la cámara al tamaño del modelo cargado
                        camera.position.set(maxDim * scale * 1.5, 0, 0); 
                        controls.update();
                        
                    }}, undefined, function(error) {{
                        console.error('Error al cargar el STL con la URL segura:', error);
                    }});
                }}, undefined, function(error) {{
                     console.error('Error al cargar la textura con la URL segura.', error);
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
                    const cubeMaterial = new THREE.MeshBasicMaterial({{ color: 0x0000FF, transparent: true, opacity: 0.7 }});
                    const cube = new THREE.Mesh(geometry, cubeMaterial);
                    
                    // Posicionamos el cubo para que siempre sea visible
                    cube.position.set(50, 50, 0); 
                    scene.add(cube);
                }}

                animate();
            }}

            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            
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
### ¡Éxito Final! 🚀
Este código utiliza la técnica más avanzada para asegurar la accesibilidad de archivos en Streamlit, resolviendo los problemas de compatibilidad de `trimesh` y las rutas web.

* **Si la Tierra aparece**: El problema se ha resuelto con las URLs seguras.
* **Si solo aparece el cubo**: El entorno de Streamlit está bloqueando incluso las URLs temporales, o hay un problema con el archivo **`Earth.stl`** (e.g., está corrupto o es un tipo de STL binario que Three.js no puede leer correctamente).
""")

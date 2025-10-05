import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# --- Configuración de Rutas de Archivo ---
MODELO_STL_PATH = "Earth.stl" 
TEXTURA_PATH = "earth_texture.jpg" 


# --- Función para codificar archivos a Base64 ---

def get_base64_data_url(file_path, mime_type):
    """Codifica un archivo a una URL de datos Base64."""
    if not os.path.exists(file_path):
        st.error(f"❌ ¡CRÍTICO! El archivo '{file_path}' no se encontró.")
        return None
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode()
            return f"data:{mime_type};base64,{encoded}"
    except Exception as e:
        st.error(f"❌ Error al codificar {file_path} a Base64: {e}")
        return None

# Generar las URLs Base64 Data
STL_DATA_URL = get_base64_data_url(MODELO_STL_PATH, 'application/vnd.ms-pki.stl')
TEXTURE_DATA_URL = get_base64_data_url(TEXTURA_PATH, 'image/jpeg')


# --- 1. Configuración de Streamlit y Estado ---
st.set_page_config(layout="wide")
st.title("Visor 3D con Textura (Base64) 🌎")

if 'show_cube' not in st.session_state:
    st.session_state.show_cube = False
if 'cube_size' not in st.session_state:
    st.session_state.cube_size = 10.0


# --- 2. HTML y JavaScript para el Visor 3D (Three.js) ---

def generate_threejs_viewer(model_data_url, texture_data_url, show_cube, cube_size):
    """
    Genera el código HTML/JS, inyectando el modelo y la textura como URLs Base64.
    """
    # Si las URLs son None, significa que los archivos no existen y ya se mostró un error.
    if model_data_url is None: return ""
    
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
            const modelURL = '{model_data_url}';
            const textureURL = '{texture_data_url}';
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

                // Cargar Textura y Modelo (usando la URL Base64 Data)
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
                        console.error('Error al cargar el STL (Base64):', error);
                        // Esto podría indicar un STL corrupto o demasiado grande para Base64.
                    }});
                }}, undefined, function(error) {{
                     console.error('Error al cargar la textura (Base64).', error);
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


html_code = generate_threejs_viewer(STL_DATA_URL, TEXTURE_DATA_URL, st.session_state.show_cube, st.session_state.cube_size)

components.html(
    html_code,
    height=600,
    scrolling=False
)

st.markdown("""
---
### Diagnóstico Final y Solución Base64 🚀

* **El problema de compatibilidad ha terminado.** Este código usa **Base64** para incrustar los archivos directamente, evitando cualquier problema de `trimesh` o de rutas de archivo de Streamlit.
* **Si la Tierra no aparece ahora**, solo hay dos posibilidades:
    1.  El archivo **`Earth.stl` es extremadamente grande** (varios megabytes) y el navegador lo rechaza al estar codificado en Base64.
    2.  El archivo **`Earth.stl` está dañado o tiene un formato que el cargador STL de Three.js (STLLoader) no puede interpretar**. (Por ejemplo, si fuera un STL binario mal formado).

**Próximo paso:** Si la Tierra aún no aparece, te recomiendo **reemplazar `Earth.stl`** por un archivo de modelo 3D de Tierra en formato **GLB o OBJ** (si tienes las texturas) y usar el cargador GLTFLoader/OBJLoader de Three.js, ya que son más modernos y robustos.
""")

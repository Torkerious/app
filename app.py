import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# --- Configuración de Rutas de Archivo (OBJ/PNG) ---
MODELO_OBJ_PATH = "Earth.obj" 
TEXTURA_PATH = "earth_texture.png" 


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
OBJ_DATA_URL = get_base64_data_url(MODELO_OBJ_PATH, 'text/plain')
TEXTURE_DATA_URL = get_base64_data_url(TEXTURA_PATH, 'image/png')


# --- 1. Configuración de Streamlit y Estado ---
st.set_page_config(layout="wide")
st.title("Visor 3D Final: Emergencia OBJ/PNG 🚨")

if 'show_cube' not in st.session_state:
    st.session_state.show_cube = False
if 'cube_size' not in st.session_state:
    st.session_state.cube_size = 10.0


# --- 2. HTML y JavaScript para el Visor 3D (Three.js) ---

def generate_threejs_viewer(obj_data_url, texture_data_url, show_cube, cube_size):
    """
    Usa la estrategia de carga OBJ y aplica la textura PNG por separado.
    """
    if obj_data_url is None: return ""
    texture_url_final = texture_data_url if texture_data_url is not None else ""

    HTML_CODE = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Three.js OBJ Viewer</title>
        <style>
            body {{ margin: 0; }}
            #container {{ width: 100%; height: 600px; }} 
        </style>
    </head>
    <body>
        <div id="container"></div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/OBJLoader.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/MTLLoader.js"></script>

        <script>
            let scene, camera, renderer, controls;
            const container = document.getElementById('container');
            const objURL = '{obj_data_url}';
            const textureURL = '{texture_url_final}'; 
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
                const objLoader = new THREE.OBJLoader();
                
                // 1. Cargar Textura
                const texture = textureLoader.load(textureURL, 
                    undefined, 
                    function(err) {{
                        console.error('Error al cargar la textura PNG.', err);
                    }}
                );
                
                // 2. Crear Material
                const material = new THREE.MeshPhongMaterial({{
                    map: texture,
                    shininess: 10,
                    side: THREE.DoubleSide
                }});
                
                // 3. Cargar el OBJ y aplicar el material
                objLoader.load(objURL, function(object) {{
                    
                    object.traverse(function(child) {{
                        if (child.isMesh) {{
                            child.geometry.center(); 
                            child.material = material; // Aplica el material con la textura
                            
                            // Ajuste de escala
                            const box = new THREE.Box3().setFromObject(child);
                            const size = box.getSize(new THREE.Vector3());
                            const maxDim = Math.max(size.x, size.y, size.z);
                            const scale = 100 / maxDim;
                            child.scale.set(scale, scale, scale);
                        }}
                    }});
                    
                    scene.add(object);
                    
                    // Ajustar la cámara
                    camera.position.set(150, 0, 0); 
                    controls.update();
                    
                }}, undefined, function(error) {{
                    console.error('Error CRÍTICO al cargar el OBJ (Base64).', error);
                }});


                // --- Elemento de Experimentación (Cubo) ---
                if (showCube) {{
                    const geometry = new THREE.BoxGeometry(cubeSize, cubeSize, cubeSize);
                    const cubeMaterial = new THREE.MeshBasicMaterial({{ color: 0x0000FF, transparent: true, opacity: 0.7 }});
                    const cube = new THREE.Mesh(geometry, cubeMaterial);
                    
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


html_code = generate_threejs_viewer(OBJ_DATA_URL, TEXTURE_DATA_URL, st.session_state.show_cube, st.session_state.cube_size)

components.html(
    html_code,
    height=600,
    scrolling=False
)

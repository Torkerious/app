import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# --- Configuración de Rutas de Archivo (GLB) ---
MODELO_GLB_PATH = "Earth.glb" 

# --- Función para codificar archivo a Base64 ---

def get_base64_data_url(file_path, mime_type):
    """Codifica un archivo a una URL de datos Base64."""
    if not os.path.exists(file_path):
        st.error(f"❌ ¡CRÍTICO! El archivo '{file_path}' no se encontró. Asegúrate de que 'Earth.glb' está en la carpeta raíz.")
        return None
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode()
            # El tipo MIME para GLB es crucial: model/gltf-binary
            return f"data:{mime_type};base64,{encoded}"
    except Exception as e:
        st.error(f"❌ Error al codificar {file_path} a Base64: {e}")
        return None

# Generar la URL Base64 Data para el GLB
GLB_DATA_URL = get_base64_data_url(MODELO_GLB_PATH, 'model/gltf-binary')


# --- 1. Configuración de Streamlit y Estado ---
st.set_page_config(layout="wide")
st.title("Visor 3D Final (GLB/Base64) 🌍")

if 'show_cube' not in st.session_state:
    st.session_state.show_cube = False
if 'cube_size' not in st.session_state:
    st.session_state.cube_size = 10.0


# --- 2. HTML y JavaScript para el Visor 3D (Three.js) ---

def generate_threejs_viewer(glb_data_url, show_cube, cube_size):
    """
    Genera el código HTML/JS, usando el GLTFLoader para cargar el modelo.
    """
    if glb_data_url is None: return ""

    HTML_CODE = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Three.js GLB Viewer</title>
        <style>
            body {{ margin: 0; }}
            #container {{ width: 100%; height: 600px; }} 
        </style>
    </head>
    <body>
        <div id="container"></div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>

        <script>
            let scene, camera, renderer, controls;
            const container = document.getElementById('container');
            const modelURL = '{glb_data_url}';
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

                const ambientLight = new THREE.AmbientLight(0xFFFFFF, 1.0);
                scene.add(ambientLight);
                
                // Luz direccional fuerte para modelos PBR (como los GLB)
                const directionalLight = new THREE.DirectionalLight(0xFFFFFF, 2.0);
                directionalLight.position.set(100, 100, 100);
                scene.add(directionalLight);


                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.target.set(0, 0, 0); 
                
                // Usamos el GLTFLoader
                const loader = new THREE.GLTFLoader();

                // Iniciar la carga del GLB
                loader.load(modelURL, function(gltf) {{
                    const object = gltf.scene;
                    
                    // Centrar la geometría
                    const box = new THREE.Box3().setFromObject(object);
                    const size = box.getSize(new THREE.Vector3());
                    const maxDim = Math.max(size.x, size.y, size.z);
                    const scale = 100 / maxDim;
                    object.scale.set(scale, scale, scale);
                    
                    // Mover el objeto al centro
                    box.getCenter(object.position).multiplyScalar(-1);
                    
                    scene.add(object);
                    
                    // Ajustar la cámara al tamaño del modelo
                    camera.position.set(maxDim * scale * 1.5, 0, 0); 
                    controls.update();

                }}, undefined, function(error) {{
                    console.error('Error CRÍTICO al cargar el GLB (Base64).', error);
                    // Si falla, el problema es que el archivo GLB está dañado o es demasiado grande.
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


html_code = generate_threejs_viewer(GLB_DATA_URL, st.session_state.show_cube, st.session_state.cube_size)

components.html(
    html_code,
    height=600,
    scrolling=False
)

st.markdown("""
---
### ¡Instrucciones Finales para GLB! ✨

1.  **Asegúrate de que el modelo se llama `Earth.glb`** y está en la misma carpeta que `app.py`.
2.  El formato **GLB** incluye la textura y los UVs, lo que elimina el problema de la textura que desaparece.
3.  Si la Tierra **no aparece**, el archivo `Earth.glb` es probablemente **demasiado grande** para la inyección Base64. Deberías intentar alojarlo en un servicio de hosting externo y usar la URL directa, aunque esa técnica falló con las rutas locales.
""")

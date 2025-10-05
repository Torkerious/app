import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# --- Rutas de Archivo ---
MODELO_STL_PATH = "Earth.stl" 
TEXTURE_URL = "earth_texture.png" 

# --- Función para codificar SOLO el STL a Base64 ---
def get_stl_base64_data_url(file_path):
    """Codifica el STL a una URL de datos Base64."""
    if not os.path.exists(file_path):
        st.error(f"❌ ¡CRÍTICO! El archivo '{file_path}' no se encontró.")
        return None
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode()
            return f"data:application/vnd.ms-pki.stl;base64,{encoded}"
    except Exception as e:
        st.error(f"❌ Error al codificar {file_path} a Base64: {e}")
        return None

# Generar la URL Base64 Data (SOLO EL STL)
STL_DATA_URL = get_stl_base64_data_url(MODELO_STL_PATH)


# --- 1. Configuración de Streamlit y Estado ---
st.set_page_config(layout="wide")
st.title("Visor 3D: ¡Color Finalmente! 🌈")

if 'show_cube' not in st.session_state:
    st.session_state.show_cube = False
if 'cube_size' not in st.session_state:
    st.session_state.cube_size = 10.0


# --- 2. HTML y JavaScript para el Visor 3D (Three.js) ---

def generate_threejs_viewer(stl_data_url, texture_url, show_cube, cube_size):
    if stl_data_url is None: return ""

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
            const modelURL = '{stl_data_url}';
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

                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.target.set(0, 0, 0); 
                
                const textureLoader = new THREE.TextureLoader();
                const stlLoader = new THREE.STLLoader();

                // 1. Cargar Textura con URL simple
                const texture = textureLoader.load(textureURL, 
                    function(tex) {{
                        tex.needsUpdate = true;
                    }}, 
                    undefined, 
                    function(err) {{
                        console.error('Error al cargar la textura PNG por URL simple.', err);
                    }}
                );
                
                // 2. Cargar el STL y aplicar el material
                stlLoader.load(modelURL, function(geometry) {{
                    geometry.center(); 
                    
                    // --- AJUSTE CRUCIAL: MeshBasicMaterial con color blanco ---
                    const material = new THREE.MeshBasicMaterial({{ 
                        map: texture, 
                        color: 0xFFFFFF, // <--- Color base blanco para no oscurecer la textura
                        side: THREE.DoubleSide, 
                        needsUpdate: true 
                    }}); 

                    const mesh = new THREE.Mesh(geometry, material);
                    
                    const box = new THREE.Box3().setFromObject(mesh);
                    const size = box.getSize(new THREE.Vector3());
                    const maxDim = Math.max(size.x, size.y, size.z);
                    const scale = 100 / maxDim;
                    mesh.scale.set(scale, scale, scale);
                    
                    scene.add(mesh);
                    
                    camera.position.set(maxDim * scale * 1.5, 0, 0); 
                    controls.update();
                    
                }}, undefined, function(error) {{
                    console.error('Error CRÍTICO al cargar el STL (Base64).', error);
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


html_code = generate_threejs_viewer(STL_DATA_URL, TEXTURE_URL, st.session_state.show_cube, st.session_state.cube_size)

components.html(
    html_code,
    height=600,
    scrolling=False
)

st.markdown("""
---
### ¡Éxito en el Diagnóstico! 🎉

Si la textura se nota pero está oscura, casi siempre se debe a que el **color base del material no es blanco**. Al forzar `color: 0xFFFFFF` en el `MeshBasicMaterial`, aseguramos que la textura se muestre sin oscurecimientos.

Si el problema persiste después de este cambio, significa que tu **archivo PNG** de textura en sí es el que tiene la mayoría de sus píxeles muy oscuros.
""")

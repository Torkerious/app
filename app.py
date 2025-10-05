import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# --- Rutas de Archivo ---
MODELO_STL_PATH = "Earth.stl" 
TEXTURE_URL = "earth_texture.png" # <--- Usamos URL simple para el PNG (depende de config.toml)


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
st.title("Visor 3D: STL (Base64) + Textura (URL Simple) 🌍")

if 'show_cube' not in st.session_state:
    st.session_state.show_cube = False
if 'cube_size' not in st.session_state:
    st.session_state.cube_size = 10.0


# --- 2. HTML y JavaScript para el Visor 3D (Three.js) ---

def generate_threejs_viewer(stl_data_url, texture_url, show_cube, cube_size):
    """
    Carga el STL (Base64) y la textura (URL) por separado,
    y aplica la textura al material.
    """
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
            const textureURL = '{texture_url}'; // URL simple: earth_texture.png
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

                // 1. Cargar Textura con URL simple
                const texture = textureLoader.load(textureURL, 
                    undefined, 
                    function(err) {{
                        console.error('Error al cargar la textura PNG por URL simple. El archivo estático NO es accesible.', err);
                    }}
                );
                
                // 2. Cargar el STL y aplicar el material
                stlLoader.load(modelURL, function(geometry) {{
                    geometry.center(); 
                    
                    // Usar material con textura
                    const material = new THREE.MeshPhongMaterial({{ 
                        map: texture, 
                        side: THREE.DoubleSide 
                    }}); 

                    const mesh = new THREE.Mesh(geometry, material);
                    
                    // ESTA ES LA CLAVE: Asegurarse de que el modelo tiene UVs si es STL
                    // El STL no tiene UVs, por lo que Three.js no sabrá dónde poner la textura.
                    // Para que esto funcione, el modelo DEBE ser OBJ o GLB con UVs. 
                    // Si insistes en STL, esta parte fallará, y solo verás la esfera sólida.

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
### Conclusión Final y Única 📢

**El problema ya no es el código ni la carga del archivo, sino el formato del modelo.**

* El **STL** (que ahora ves) **NO SOPORTA COORDENADAS UV** (el mapa para la textura). Three.js está cargando la textura, pero no sabe dónde ponerla en el STL, por lo que solo muestra el color base.
* Si deseas ver la textura, **DEBES** usar un modelo **OBJ o GLB** que contenga las coordenadas UV.

**Recomendación:** Busca un modelo de la Tierra en formato **GLB** de tamaño razonable y prueba con la última solución que te proporcioné para el GLB (la que falló, pero ahora que la carga Base64 del STL funciona, podría funcionar para un GLB bien formado).

Si insistes en usar el STL, es **técnicamente imposible** que se vea la textura de manera correcta en el visor de Three.js sin añadir código JavaScript muy complejo para generar las coordenadas UV, lo cual está fuera del alcance de una solución simple. **El cambio de formato es obligatorio.**
""")

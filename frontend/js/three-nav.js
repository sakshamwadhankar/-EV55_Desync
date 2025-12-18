// --- Three.js Navbar Decoration (Subtle Rotating Lens) ---
const initThree = () => {
    const container = document.getElementById('canvas-container');
    if (!container) return;

    const scene = new THREE.Scene();
    // Transparent background
    // scene.background = null; 

    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.z = 5;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(0x000000, 0); // the default
    container.appendChild(renderer.domElement);

    // Geometry: Wireframe Icosahedron (Abstract Lens structure)
    const geometry = new THREE.IcosahedronGeometry(2.5, 1);
    const material = new THREE.MeshBasicMaterial({
        color: 0x10b981, // Emerald
        wireframe: true,
        transparent: true,
        opacity: 0.15
    });
    const sphere = new THREE.Mesh(geometry, material);
    scene.add(sphere);

    // Inner core
    const coreGeo = new THREE.IcosahedronGeometry(1, 0);
    const coreMat = new THREE.MeshBasicMaterial({ color: 0x14b8a6, wireframe: true, transparent: true, opacity: 0.3 });
    const core = new THREE.Mesh(coreGeo, coreMat);
    scene.add(core);

    // Animation
    const animate = function () {
        requestAnimationFrame(animate);

        sphere.rotation.x += 0.002;
        sphere.rotation.y += 0.003;

        core.rotation.x -= 0.005;
        core.rotation.y -= 0.005;

        renderer.render(scene, camera);
    };

    animate();

    // Handle Resize
    window.addEventListener('resize', () => {
        // Determine new size (based on CSS rules for container)
        renderer.setSize(container.clientWidth, container.clientHeight);
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
    });
};

document.addEventListener('DOMContentLoaded', initThree);

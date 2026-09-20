(function () {

    console.log("JanMitra network.js loaded");

    const container = document.getElementById("network-background");

    if (!container) {
        console.error("JanMitra: network container not found");
        return;
    }

    if (typeof THREE === "undefined") {
        console.error("JanMitra: Three.js failed to load");
        return;
    }

    console.log("JanMitra: Three.js loaded successfully");

    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 2000);

    camera.position.z = 620;

    const renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true
    });

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    renderer.setSize(window.innerWidth, window.innerHeight);

    renderer.setClearColor(0x020617, 1);

    container.appendChild(renderer.domElement);

    const particleCount = window.innerWidth < 768 ? 110 : 300;

    const spreadX = 1250;
    const spreadY = 720;
    const spreadZ = 650;

    const positions = [];
    const originalPositions = [];
    const velocities = [];

    for (let i = 0; i < particleCount; i++) {

        const x = (Math.random() - 0.5) * spreadX;
        const y = (Math.random() - 0.5) * spreadY;
        const z = (Math.random() - 0.5) * spreadZ;

        positions.push(x, y, z);

        originalPositions.push(x, y, z);

        velocities.push(
            (Math.random() - 0.5) * 0.12,
            (Math.random() - 0.5) * 0.12,
            (Math.random() - 0.5) * 0.06
        );
    }

    const particleGeometry = new THREE.BufferGeometry();

    particleGeometry.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(positions, 3)
    );

    const particleMaterial = new THREE.PointsMaterial({
        color: 0x25bfff,
        size: 4.2,
        transparent: true,
        opacity: 0.95,
        depthWrite: false,
        blending: THREE.AdditiveBlending
    });

    const particles = new THREE.Points(
        particleGeometry,
        particleMaterial
    );

    scene.add(particles);

    const glowMaterial = new THREE.PointsMaterial({
        color: 0x168bd1,
        size: 11,
        transparent: true,
        opacity: 0.12,
        depthWrite: false,
        blending: THREE.AdditiveBlending
    });

    const particleGlow = new THREE.Points(
        particleGeometry,
        glowMaterial
    );

    scene.add(particleGlow);

    const lineGeometry = new THREE.BufferGeometry();

    const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x159ee5,
        transparent: true,
        opacity: 0.28,
        depthWrite: false,
        blending: THREE.AdditiveBlending
    });

    const lines = new THREE.LineSegments(
        lineGeometry,
        lineMaterial
    );

    scene.add(lines);

    const mouse = {
        x: 0,
        y: 0
    };

    const targetMouse = {
        x: 0,
        y: 0
    };

    window.addEventListener("mousemove", function (event) {

        targetMouse.x =
            (event.clientX / window.innerWidth) * 2 - 1;

        targetMouse.y =
            -(event.clientY / window.innerHeight) * 2 + 1;

    });

    function updateConnections() {

        const currentPositions =
            particleGeometry.attributes.position.array;

        const connectionPositions = [];

        const maxDistance = 150;

        for (let i = 0; i < particleCount; i++) {

            const i3 = i * 3;

            for (let j = i + 1; j < particleCount; j++) {

                const j3 = j * 3;

                const dx =
                    currentPositions[i3] -
                    currentPositions[j3];

                const dy =
                    currentPositions[i3 + 1] -
                    currentPositions[j3 + 1];

                const dz =
                    currentPositions[i3 + 2] -
                    currentPositions[j3 + 2];

                const distance =
                    Math.sqrt(
                        dx * dx +
                        dy * dy +
                        dz * dz
                    );

                if (distance < maxDistance) {

                    connectionPositions.push(
                        currentPositions[i3],
                        currentPositions[i3 + 1],
                        currentPositions[i3 + 2],
                        currentPositions[j3],
                        currentPositions[j3 + 1],
                        currentPositions[j3 + 2]
                    );
                }
            }
        }

        lineGeometry.setAttribute(
            "position",
            new THREE.Float32BufferAttribute(
                connectionPositions,
                3
            )
        );

    }

    let frame = 0;
    let time = 0;

    function animate() {

        requestAnimationFrame(animate);

        frame++;

        time += 0.004;

        mouse.x +=
            (targetMouse.x - mouse.x) * 0.035;

        mouse.y +=
            (targetMouse.y - mouse.y) * 0.035;

        const currentPositions =
            particleGeometry.attributes.position.array;

        for (let i = 0; i < particleCount; i++) {

            const index = i * 3;

            const originalX =
                originalPositions[index];

            const originalY =
                originalPositions[index + 1];

            const originalZ =
                originalPositions[index + 2];

            currentPositions[index] +=
                velocities[index];

            currentPositions[index + 1] +=
                velocities[index + 1];

            currentPositions[index + 2] +=
                velocities[index + 2];

            currentPositions[index] +=
                (originalX - currentPositions[index]) * 0.001;

            currentPositions[index + 1] +=
                (originalY - currentPositions[index + 1]) * 0.001;

            currentPositions[index + 2] +=
                (originalZ - currentPositions[index + 2]) * 0.001;

            if (currentPositions[index] > spreadX / 2 || currentPositions[index] < -spreadX / 2) {
                velocities[index] *= -1;
            }

            if (currentPositions[index + 1] > spreadY / 2 || currentPositions[index + 1] < -spreadY / 2) {
                velocities[index + 1] *= -1;
            }

            if (currentPositions[index + 2] > spreadZ / 2 || currentPositions[index + 2] < -spreadZ / 2) {
                velocities[index + 2] *= -1;
            }

            const cursorX = mouse.x * 420;
            const cursorY = mouse.y * 280;

            const dx =
                currentPositions[index] -
                cursorX;

            const dy =
                currentPositions[index + 1] -
                cursorY;

            const distance =
                Math.sqrt(dx * dx + dy * dy);

            if (distance < 220) {

                const force =
                    (220 - distance) / 220;

                currentPositions[index] +=
                    dx * force * 0.025;

                currentPositions[index + 1] +=
                    dy * force * 0.025;
            }
        }

        particleGeometry.attributes.position.needsUpdate = true;

        particles.rotation.y =
            Math.sin(time * 0.35) * 0.08 +
            mouse.x * 0.025;

        particles.rotation.x =
            Math.sin(time * 0.25) * 0.035 +
            mouse.y * 0.018;

        particleGlow.rotation.y =
            particles.rotation.y;

        particleGlow.rotation.x =
            particles.rotation.x;

        lines.rotation.y =
            particles.rotation.y;

        lines.rotation.x =
            particles.rotation.x;

        if (frame % 3 === 0) {
            updateConnections();
        }

        renderer.render(scene, camera);
    }

    window.addEventListener("resize", function () {

        camera.aspect =
            window.innerWidth /
            window.innerHeight;

        camera.updateProjectionMatrix();

        renderer.setSize(
            window.innerWidth,
            window.innerHeight
        );

    });

    updateConnections();

    animate();

})();










// (function () {

//     console.log("JanMitra network.js loaded");

//     const container = document.getElementById("network-background");

//     if (!container) {
//         console.error("JanMitra: network container not found");
//         return;
//     }

//     if (typeof THREE === "undefined") {
//         console.error("JanMitra: Three.js failed to load");
//         return;
//     }

//     console.log("JanMitra: Three.js loaded successfully");

//     /* =========================================================
//        SCENE
//     ========================================================= */

//     const scene = new THREE.Scene();

//     const camera = new THREE.PerspectiveCamera(
//         60,
//         window.innerWidth / window.innerHeight,
//         1,
//         2200
//     );

//     camera.position.z = 620;

//     const renderer = new THREE.WebGLRenderer({
//         antialias: true,
//         alpha: true
//     });

//     renderer.setPixelRatio(
//         Math.min(window.devicePixelRatio, 1.8)
//     );

//     renderer.setSize(
//         window.innerWidth,
//         window.innerHeight
//     );

//     renderer.setClearColor(0x020617, 1);

//     container.appendChild(renderer.domElement);


//     /* =========================================================
//        RESPONSIVE SETTINGS
//     ========================================================= */

//     const isMobile = window.innerWidth < 768;

//     const particleCount = isMobile ? 100 : 260;

//     const spreadX = 1450;
//     const spreadY = 820;
//     const spreadZ = 700;


//     /* =========================================================
//        PARTICLE DATA
//     ========================================================= */

//     const positions = [];
//     const originalPositions = [];
//     const velocities = [];
//     const particleSizes = [];
//     const particlePhases = [];

//     for (let i = 0; i < particleCount; i++) {

//         const x =
//             (Math.random() - 0.5) * spreadX;

//         const y =
//             (Math.random() - 0.5) * spreadY;

//         const z =
//             (Math.random() - 0.5) * spreadZ;

//         positions.push(x, y, z);

//         originalPositions.push(x, y, z);

//         velocities.push(
//             (Math.random() - 0.5) * 0.045,
//             (Math.random() - 0.5) * 0.045,
//             (Math.random() - 0.5) * 0.025
//         );

//         particleSizes.push(
//             1.5 + Math.random() * 3.2
//         );

//         particlePhases.push(
//             Math.random() * Math.PI * 2
//         );
//     }


//     /* =========================================================
//        PARTICLE GEOMETRY
//     ========================================================= */

//     const particleGeometry =
//         new THREE.BufferGeometry();

//     particleGeometry.setAttribute(
//         "position",
//         new THREE.Float32BufferAttribute(
//             positions,
//             3
//         )
//     );


//     /* =========================================================
//        MAIN PARTICLES
//     ========================================================= */

//     const particleMaterial =
//         new THREE.PointsMaterial({

//             color: 0x28c7ff,

//             size: 3.2,

//             transparent: true,

//             opacity: 0.72,

//             depthWrite: false,

//             blending: THREE.AdditiveBlending
//         });


//     const particles =
//         new THREE.Points(
//             particleGeometry,
//             particleMaterial
//         );

//     scene.add(particles);


//     /* =========================================================
//        PARTICLE GLOW
//     ========================================================= */

//     const glowMaterial =
//         new THREE.PointsMaterial({

//             color: 0x168bd1,

//             size: 10,

//             transparent: true,

//             opacity: 0.07,

//             depthWrite: false,

//             blending: THREE.AdditiveBlending
//         });


//     const particleGlow =
//         new THREE.Points(
//             particleGeometry,
//             glowMaterial
//         );

//     scene.add(particleGlow);


//     /* =========================================================
//        CONNECTION LINES
//     ========================================================= */

//     const lineGeometry =
//         new THREE.BufferGeometry();

//     const lineMaterial =
//         new THREE.LineBasicMaterial({

//             color: 0x159ee5,

//             transparent: true,

//             opacity: 0.13,

//             depthWrite: false,

//             blending: THREE.AdditiveBlending
//         });


//     const lines =
//         new THREE.LineSegments(
//             lineGeometry,
//             lineMaterial
//         );

//     scene.add(lines);


//     /* =========================================================
//        CURSOR
//     ========================================================= */

//     const mouse = {

//         x: 0,

//         y: 0,

//         worldX: 0,

//         worldY: 0

//     };


//     const targetMouse = {

//         x: 0,

//         y: 0

//     };


//     let cursorActive = false;


//     window.addEventListener(
//         "mousemove",
//         function (event) {

//             targetMouse.x =
//                 (event.clientX /
//                     window.innerWidth) * 2 - 1;

//             targetMouse.y =
//                 -(event.clientY /
//                     window.innerHeight) * 2 + 1;

//             cursorActive = true;

//         },
//         { passive: true }
//     );


//     window.addEventListener(
//         "mouseleave",
//         function () {

//             cursorActive = false;

//         }
//     );


//     /* =========================================================
//        CURSOR GLOW
//     ========================================================= */

//     const cursorGlowGeometry =
//         new THREE.CircleGeometry(
//             1,
//             64
//         );


//     const cursorGlowMaterial =
//         new THREE.MeshBasicMaterial({

//             color: 0x18bfff,

//             transparent: true,

//             opacity: 0.035,

//             depthWrite: false,

//             blending: THREE.AdditiveBlending
//         });


//     const cursorGlow =
//         new THREE.Mesh(
//             cursorGlowGeometry,
//             cursorGlowMaterial
//         );


//     cursorGlow.scale.set(
//         190,
//         190,
//         1
//     );

//     cursorGlow.position.z = 120;

//     scene.add(cursorGlow);


//     /* =========================================================
//        SECONDARY CURSOR GLOW
//     ========================================================= */

//     const cursorCoreGeometry =
//         new THREE.CircleGeometry(
//             1,
//             48
//         );


//     const cursorCoreMaterial =
//         new THREE.MeshBasicMaterial({

//             color: 0x35d5ff,

//             transparent: true,

//             opacity: 0.025,

//             depthWrite: false,

//             blending: THREE.AdditiveBlending
//         });


//     const cursorCore =
//         new THREE.Mesh(
//             cursorCoreGeometry,
//             cursorCoreMaterial
//         );


//     cursorCore.scale.set(
//         75,
//         75,
//         1
//     );

//     cursorCore.position.z = 130;

//     scene.add(cursorCore);


//     /* =========================================================
//        CONNECTION SETTINGS
//     ========================================================= */

//     const maxDistance = isMobile
//         ? 135
//         : 155;


//     /* =========================================================
//        UPDATE CONNECTIONS
//     ========================================================= */

//     function updateConnections() {

//         const currentPositions =
//             particleGeometry
//                 .attributes
//                 .position
//                 .array;

//         const connectionPositions = [];

//         for (
//             let i = 0;
//             i < particleCount;
//             i++
//         ) {

//             const i3 = i * 3;

//             for (
//                 let j = i + 1;
//                 j < particleCount;
//                 j++
//             ) {

//                 const j3 = j * 3;

//                 const dx =
//                     currentPositions[i3] -
//                     currentPositions[j3];

//                 const dy =
//                     currentPositions[i3 + 1] -
//                     currentPositions[j3 + 1];

//                 const dz =
//                     currentPositions[i3 + 2] -
//                     currentPositions[j3 + 2];


//                 const distance =
//                     Math.sqrt(
//                         dx * dx +
//                         dy * dy +
//                         dz * dz
//                     );


//                 if (
//                     distance <
//                     maxDistance
//                 ) {

//                     connectionPositions.push(

//                         currentPositions[i3],

//                         currentPositions[i3 + 1],

//                         currentPositions[i3 + 2],

//                         currentPositions[j3],

//                         currentPositions[j3 + 1],

//                         currentPositions[j3 + 2]

//                     );

//                 }

//             }

//         }


//         lineGeometry.setAttribute(

//             "position",

//             new THREE.Float32BufferAttribute(

//                 connectionPositions,

//                 3

//             )

//         );

//     }


//     /* =========================================================
//        ANIMATION
//     ========================================================= */

//     let frame = 0;

//     let time = 0;


//     function animate() {

//         requestAnimationFrame(
//             animate
//         );

//         frame++;

//         time += 0.003;


//         /* -----------------------------------------------------
//            SMOOTH CURSOR
//         ----------------------------------------------------- */

//         mouse.x +=
//             (
//                 targetMouse.x -
//                 mouse.x
//             ) * 0.045;


//         mouse.y +=
//             (
//                 targetMouse.y -
//                 mouse.y
//             ) * 0.045;


//         /* -----------------------------------------------------
//            CURSOR WORLD POSITION
//         ----------------------------------------------------- */

//         mouse.worldX =
//             mouse.x * 450;


//         mouse.worldY =
//             mouse.y * 290;


//         /* -----------------------------------------------------
//            CURSOR GLOW
//         ----------------------------------------------------- */

//         cursorGlow.position.x +=
//             (
//                 mouse.worldX -
//                 cursorGlow.position.x
//             ) * 0.08;


//         cursorGlow.position.y +=
//             (
//                 mouse.worldY -
//                 cursorGlow.position.y
//             ) * 0.08;


//         cursorCore.position.x =
//             cursorGlow.position.x;


//         cursorCore.position.y =
//             cursorGlow.position.y;


//         /* -----------------------------------------------------
//            PULSE CURSOR GLOW
//         ----------------------------------------------------- */

//         const pulse =
//             1 +
//             Math.sin(time * 3.0) * 0.08;


//         cursorGlow.scale.set(
//             190 * pulse,
//             190 * pulse,
//             1
//         );


//         cursorCore.scale.set(
//             75 * pulse,
//             75 * pulse,
//             1
//         );


//         /* -----------------------------------------------------
//            PARTICLES
//         ----------------------------------------------------- */

//         const currentPositions =
//             particleGeometry
//                 .attributes
//                 .position
//                 .array;


//         for (
//             let i = 0;
//             i < particleCount;
//             i++
//         ) {

//             const index = i * 3;


//             const originalX =
//                 originalPositions[index];

//             const originalY =
//                 originalPositions[index + 1];

//             const originalZ =
//                 originalPositions[index + 2];


//             /* -------------------------------------------------
//                NATURAL FLOATING
//             ------------------------------------------------- */

//             const phase =
//                 particlePhases[i];


//             const floatX =
//                 Math.sin(
//                     time * 0.8 +
//                     phase
//                 ) * 0.035;


//             const floatY =
//                 Math.cos(
//                     time * 0.7 +
//                     phase
//                 ) * 0.035;


//             const floatZ =
//                 Math.sin(
//                     time * 0.5 +
//                     phase
//                 ) * 0.02;


//             currentPositions[index] +=
//                 velocities[index] +
//                 floatX;


//             currentPositions[index + 1] +=
//                 velocities[index + 1] +
//                 floatY;


//             currentPositions[index + 2] +=
//                 velocities[index + 2] +
//                 floatZ;


//             /* -------------------------------------------------
//                RETURN TO ORIGINAL POSITION
//             ------------------------------------------------- */

//             currentPositions[index] +=
//                 (
//                     originalX -
//                     currentPositions[index]
//                 ) * 0.0015;


//             currentPositions[index + 1] +=
//                 (
//                     originalY -
//                     currentPositions[index + 1]
//                 ) * 0.0015;


//             currentPositions[index + 2] +=
//                 (
//                     originalZ -
//                     currentPositions[index + 2]
//                 ) * 0.0015;


//             /* -------------------------------------------------
//                BOUNDARIES
//             ------------------------------------------------- */

//             if (
//                 currentPositions[index] >
//                     spreadX / 2 ||
//                 currentPositions[index] <
//                     -spreadX / 2
//             ) {

//                 velocities[index] *= -1;

//             }


//             if (
//                 currentPositions[index + 1] >
//                     spreadY / 2 ||
//                 currentPositions[index + 1] <
//                     -spreadY / 2
//             ) {

//                 velocities[index + 1] *= -1;

//             }


//             if (
//                 currentPositions[index + 2] >
//                     spreadZ / 2 ||
//                 currentPositions[index + 2] <
//                     -spreadZ / 2
//             ) {

//                 velocities[index + 2] *= -1;

//             }


//             /* -------------------------------------------------
//                CURSOR INTERACTION
//             ------------------------------------------------- */

//             const dx =
//                 currentPositions[index] -
//                 mouse.worldX;


//             const dy =
//                 currentPositions[index + 1] -
//                 mouse.worldY;


//             const distance =
//                 Math.sqrt(
//                     dx * dx +
//                     dy * dy
//                 );


//             const interactionRadius =
//                 240;


//             if (
//                 cursorActive &&
//                 distance <
//                     interactionRadius
//             ) {

//                 const strength =
//                     (
//                         interactionRadius -
//                         distance
//                     ) /
//                     interactionRadius;


//                 /*
//                  * Push particles gently away
//                  * from cursor.
//                  */

//                 currentPositions[index] +=
//                     (
//                         dx /
//                         Math.max(distance, 1)
//                     ) *
//                     strength *
//                     1.7;


//                 currentPositions[index + 1] +=
//                     (
//                         dy /
//                         Math.max(distance, 1)
//                     ) *
//                     strength *
//                     1.7;

//             }


//             /* -------------------------------------------------
//                SUBTLE ATTRACTOR
//             ------------------------------------------------- */

//             if (
//                 cursorActive &&
//                 distance > 240 &&
//                 distance < 430
//             ) {

//                 const strength =
//                     (
//                         distance - 240
//                     ) /
//                     190;


//                 currentPositions[index] -=
//                     (
//                         dx /
//                         Math.max(distance, 1)
//                     ) *
//                     strength *
//                     0.12;


//                 currentPositions[index + 1] -=
//                     (
//                         dy /
//                         Math.max(distance, 1)
//                     ) *
//                     strength *
//                     0.12;

//             }

//         }


//         particleGeometry
//             .attributes
//             .position
//             .needsUpdate = true;


//         /* =====================================================
//            NETWORK ROTATION
//         ===================================================== */

//         const targetRotationY =
//             Math.sin(time * 0.45) * 0.055 +
//             mouse.x * 0.035;


//         const targetRotationX =
//             Math.sin(time * 0.35) * 0.025 +
//             mouse.y * 0.025;


//         particles.rotation.y +=
//             (
//                 targetRotationY -
//                 particles.rotation.y
//             ) * 0.025;


//         particles.rotation.x +=
//             (
//                 targetRotationX -
//                 particles.rotation.x
//             ) * 0.025;


//         particleGlow.rotation.y =
//             particles.rotation.y;


//         particleGlow.rotation.x =
//             particles.rotation.x;


//         lines.rotation.y =
//             particles.rotation.y;


//         lines.rotation.x =
//             particles.rotation.x;


//         /* =====================================================
//            CONNECTION OPACITY
//         ===================================================== */

//         if (cursorActive) {

//             lineMaterial.opacity =
//                 0.12 +
//                 Math.abs(mouse.x) * 0.03;

//         } else {

//             lineMaterial.opacity =
//                 0.11;

//         }


//         /* =====================================================
//            UPDATE CONNECTIONS
//         ===================================================== */

//         if (frame % 4 === 0) {

//             updateConnections();

//         }


//         /* =====================================================
//            RENDER
//         ===================================================== */

//         renderer.render(
//             scene,
//             camera
//         );

//     }


//     /* =========================================================
//        RESIZE
//     ========================================================= */

//     window.addEventListener(
//         "resize",
//         function () {

//             camera.aspect =
//                 window.innerWidth /
//                 window.innerHeight;


//             camera.updateProjectionMatrix();


//             renderer.setSize(
//                 window.innerWidth,
//                 window.innerHeight
//             );

//         }
//     );


//     /* =========================================================
//        INITIALIZE
//     ========================================================= */

//     updateConnections();

//     animate();


// })();














//  third version..













// (function () {

//     console.log("JanMitra network.js loaded");

//     const container = document.getElementById("network-background");

//     if (!container) {
//         console.error("JanMitra: network container not found");
//         return;
//     }

//     if (typeof THREE === "undefined") {
//         console.error("JanMitra: Three.js failed to load");
//         return;
//     }

//     console.log("JanMitra: Three.js loaded successfully");

//     // =========================================================
//     // SCENE
//     // =========================================================

//     const scene = new THREE.Scene();

//     const camera = new THREE.PerspectiveCamera(
//         60,
//         window.innerWidth / window.innerHeight,
//         1,
//         2500
//     );

//     camera.position.z = 650;

//     const renderer = new THREE.WebGLRenderer({
//         antialias: true,
//         alpha: true
//     });

//     renderer.setPixelRatio(
//         Math.min(window.devicePixelRatio, 2)
//     );

//     renderer.setSize(
//         window.innerWidth,
//         window.innerHeight
//     );

//     renderer.setClearColor(0x020617, 1);

//     container.appendChild(renderer.domElement);


//     // =========================================================
//     // CONFIGURATION
//     // =========================================================

//     const isMobile = window.innerWidth < 768;

//     const particleCount = isMobile ? 180 : 650;

//     const spreadX = 1450;
//     const spreadY = 850;
//     const spreadZ = 750;

//     // Main connection distance
//     const maxDistance = isMobile ? 135 : 165;

//     // Maximum number of connections
//     const maxConnections = isMobile ? 900 : 5000;


//     // =========================================================
//     // PARTICLE DATA
//     // =========================================================

//     const positions = [];
//     const originalPositions = [];
//     const velocities = [];
//     const particlePhases = [];
//     const particleSizes = [];

//     for (let i = 0; i < particleCount; i++) {

//         const x =
//             (Math.random() - 0.5) * spreadX;

//         const y =
//             (Math.random() - 0.5) * spreadY;

//         const z =
//             (Math.random() - 0.5) * spreadZ;

//         positions.push(x, y, z);

//         originalPositions.push(x, y, z);

//         velocities.push(
//             (Math.random() - 0.5) * 0.10,
//             (Math.random() - 0.5) * 0.10,
//             (Math.random() - 0.5) * 0.045
//         );

//         particlePhases.push(
//             Math.random() * Math.PI * 2
//         );

//         particleSizes.push(
//             2.5 + Math.random() * 3.5
//         );
//     }


//     // =========================================================
//     // PARTICLE GEOMETRY
//     // =========================================================

//     const particleGeometry =
//         new THREE.BufferGeometry();

//     particleGeometry.setAttribute(
//         "position",
//         new THREE.Float32BufferAttribute(
//             positions,
//             3
//         )
//     );


//     // =========================================================
//     // MAIN PARTICLES
//     // =========================================================

//     const particleMaterial =
//         new THREE.PointsMaterial({

//             color: 0x35c7ff,

//             size: isMobile ? 3.2 : 4.2,

//             transparent: true,

//             opacity: 0.9,

//             depthWrite: false,

//             blending:
//                 THREE.AdditiveBlending
//         });


//     const particles =
//         new THREE.Points(
//             particleGeometry,
//             particleMaterial
//         );

//     scene.add(particles);


//     // =========================================================
//     // PARTICLE GLOW
//     // =========================================================

//     const glowMaterial =
//         new THREE.PointsMaterial({

//             color: 0x168bd1,

//             size: isMobile ? 12 : 16,

//             transparent: true,

//             opacity: 0.10,

//             depthWrite: false,

//             blending:
//                 THREE.AdditiveBlending
//         });


//     const particleGlow =
//         new THREE.Points(
//             particleGeometry,
//             glowMaterial
//         );

//     scene.add(particleGlow);


//     // =========================================================
//     // SECONDARY SMALL PARTICLES
//     // =========================================================

//     const smallParticleCount =
//         isMobile ? 100 : 300;

//     const smallPositions = [];

//     for (let i = 0; i < smallParticleCount; i++) {

//         smallPositions.push(
//             (Math.random() - 0.5) * spreadX,
//             (Math.random() - 0.5) * spreadY,
//             (Math.random() - 0.5) * spreadZ
//         );
//     }


//     const smallGeometry =
//         new THREE.BufferGeometry();

//     smallGeometry.setAttribute(
//         "position",
//         new THREE.Float32BufferAttribute(
//             smallPositions,
//             3
//         )
//     );


//     const smallMaterial =
//         new THREE.PointsMaterial({

//             color: 0x73dcff,

//             size: 1.8,

//             transparent: true,

//             opacity: 0.5,

//             depthWrite: false,

//             blending:
//                 THREE.AdditiveBlending
//         });


//     const smallParticles =
//         new THREE.Points(
//             smallGeometry,
//             smallMaterial
//         );

//     scene.add(smallParticles);


//     // =========================================================
//     // CONNECTION LINES
//     // =========================================================

//     const lineGeometry =
//         new THREE.BufferGeometry();

//     const lineMaterial =
//         new THREE.LineBasicMaterial({

//             color: 0x159ee5,

//             transparent: true,

//             opacity: 0.22,

//             depthWrite: false,

//             blending:
//                 THREE.AdditiveBlending
//         });


//     const lines =
//         new THREE.LineSegments(
//             lineGeometry,
//             lineMaterial
//         );

//     scene.add(lines);


//     // =========================================================
//     // SECONDARY CONNECTION NETWORK
//     // =========================================================

//     const secondaryLineGeometry =
//         new THREE.BufferGeometry();

//     const secondaryLineMaterial =
//         new THREE.LineBasicMaterial({

//             color: 0x0875b5,

//             transparent: true,

//             opacity: 0.09,

//             depthWrite: false,

//             blending:
//                 THREE.AdditiveBlending
//         });


//     const secondaryLines =
//         new THREE.LineSegments(
//             secondaryLineGeometry,
//             secondaryLineMaterial
//         );

//     scene.add(secondaryLines);


//     // =========================================================
//     // MOUSE
//     // =========================================================

//     const mouse = {
//         x: 0,
//         y: 0
//     };

//     const targetMouse = {
//         x: 0,
//         y: 0
//     };


//     window.addEventListener(
//         "mousemove",
//         function (event) {

//             targetMouse.x =
//                 (event.clientX /
//                     window.innerWidth) * 2 - 1;

//             targetMouse.y =
//                 -(event.clientY /
//                     window.innerHeight) * 2 + 1;

//         }
//     );


//     // =========================================================
//     // UPDATE CONNECTIONS
//     // =========================================================

//     function updateConnections() {

//         const currentPositions =
//             particleGeometry
//                 .attributes
//                 .position
//                 .array;

//         const connectionPositions = [];

//         const secondaryPositions = [];

//         let connectionCount = 0;

//         let secondaryCount = 0;


//         for (let i = 0; i < particleCount; i++) {

//             const i3 = i * 3;

//             for (
//                 let j = i + 1;
//                 j < particleCount;
//                 j++
//             ) {

//                 if (
//                     connectionCount >=
//                     maxConnections
//                 ) {
//                     break;
//                 }

//                 const j3 = j * 3;

//                 const dx =
//                     currentPositions[i3] -
//                     currentPositions[j3];

//                 const dy =
//                     currentPositions[i3 + 1] -
//                     currentPositions[j3 + 1];

//                 const dz =
//                     currentPositions[i3 + 2] -
//                     currentPositions[j3 + 2];

//                 const distanceSquared =
//                     dx * dx +
//                     dy * dy +
//                     dz * dz;


//                 // Main network
//                 if (
//                     distanceSquared <
//                     maxDistance * maxDistance
//                 ) {

//                     connectionPositions.push(

//                         currentPositions[i3],
//                         currentPositions[i3 + 1],
//                         currentPositions[i3 + 2],

//                         currentPositions[j3],
//                         currentPositions[j3 + 1],
//                         currentPositions[j3 + 2]

//                     );

//                     connectionCount++;
//                 }


//                 // Secondary wider network
//                 else if (
//                     distanceSquared <
//                     (maxDistance * 1.65) *
//                     (maxDistance * 1.65)
//                 ) {

//                     if (
//                         secondaryCount <
//                         maxConnections / 2
//                     ) {

//                         secondaryPositions.push(

//                             currentPositions[i3],
//                             currentPositions[i3 + 1],
//                             currentPositions[i3 + 2],

//                             currentPositions[j3],
//                             currentPositions[j3 + 1],
//                             currentPositions[j3 + 2]

//                         );

//                         secondaryCount++;
//                     }
//                 }
//             }
//         }


//         // Main network
//         lineGeometry.setAttribute(
//             "position",
//             new THREE.Float32BufferAttribute(
//                 connectionPositions,
//                 3
//             )
//         );


//         // Secondary network
//         secondaryLineGeometry.setAttribute(
//             "position",
//             new THREE.Float32BufferAttribute(
//                 secondaryPositions,
//                 3
//             )
//         );
//     }


//     // =========================================================
//     // ANIMATION
//     // =========================================================

//     let frame = 0;
//     let time = 0;


//     function animate() {

//         requestAnimationFrame(animate);

//         frame++;

//         time += 0.004;


//         // -----------------------------------------------------
//         // Smooth mouse movement
//         // -----------------------------------------------------

//         mouse.x +=
//             (targetMouse.x - mouse.x) *
//             0.025;

//         mouse.y +=
//             (targetMouse.y - mouse.y) *
//             0.025;


//         const currentPositions =
//             particleGeometry
//                 .attributes
//                 .position
//                 .array;


//         // -----------------------------------------------------
//         // Particle movement
//         // -----------------------------------------------------

//         for (
//             let i = 0;
//             i < particleCount;
//             i++
//         ) {

//             const index = i * 3;

//             const originalX =
//                 originalPositions[index];

//             const originalY =
//                 originalPositions[index + 1];

//             const originalZ =
//                 originalPositions[index + 2];


//             // Natural floating motion
//             currentPositions[index] +=
//                 velocities[index];

//             currentPositions[index + 1] +=
//                 velocities[index + 1];

//             currentPositions[index + 2] +=
//                 velocities[index + 2];


//             // Slowly pull particles back
//             currentPositions[index] +=
//                 (originalX -
//                     currentPositions[index]) *
//                 0.0015;

//             currentPositions[index + 1] +=
//                 (originalY -
//                     currentPositions[index + 1]) *
//                 0.0015;

//             currentPositions[index + 2] +=
//                 (originalZ -
//                     currentPositions[index + 2]) *
//                 0.0015;


//             // -------------------------------------------------
//             // Boundary bouncing
//             // -------------------------------------------------

//             if (
//                 currentPositions[index] >
//                     spreadX / 2 ||
//                 currentPositions[index] <
//                     -spreadX / 2
//             ) {

//                 velocities[index] *= -1;
//             }


//             if (
//                 currentPositions[index + 1] >
//                     spreadY / 2 ||
//                 currentPositions[index + 1] <
//                     -spreadY / 2
//             ) {

//                 velocities[index + 1] *= -1;
//             }


//             if (
//                 currentPositions[index + 2] >
//                     spreadZ / 2 ||
//                 currentPositions[index + 2] <
//                     -spreadZ / 2
//             ) {

//                 velocities[index + 2] *= -1;
//             }


//             // -------------------------------------------------
//             // Mouse interaction
//             // -------------------------------------------------

//             const cursorX =
//                 mouse.x * 420;

//             const cursorY =
//                 mouse.y * 280;


//             const dx =
//                 currentPositions[index] -
//                 cursorX;

//             const dy =
//                 currentPositions[index + 1] -
//                 cursorY;


//             const distance =
//                 Math.sqrt(
//                     dx * dx +
//                     dy * dy
//                 );


//             if (distance < 240) {

//                 const force =
//                     (240 - distance) / 240;

//                 currentPositions[index] +=
//                     dx * force * 0.035;

//                 currentPositions[index + 1] +=
//                     dy * force * 0.035;
//             }
//         }


//         particleGeometry
//             .attributes
//             .position
//             .needsUpdate = true;


//         // -----------------------------------------------------
//         // Rotation
//         // -----------------------------------------------------

//         const rotationY =
//             Math.sin(time * 0.35) * 0.06 +
//             mouse.x * 0.035;

//         const rotationX =
//             Math.sin(time * 0.25) * 0.025 +
//             mouse.y * 0.025;


//         particles.rotation.y =
//             rotationY;

//         particles.rotation.x =
//             rotationX;


//         particleGlow.rotation.y =
//             rotationY;

//         particleGlow.rotation.x =
//             rotationX;


//         lines.rotation.y =
//             rotationY;

//         lines.rotation.x =
//             rotationX;


//         secondaryLines.rotation.y =
//             rotationY;

//         secondaryLines.rotation.x =
//             rotationX;


//         // -----------------------------------------------------
//         // Small particles move independently
//         // -----------------------------------------------------

//         smallParticles.rotation.y =
//             Math.sin(time * 0.18) * 0.04 +
//             mouse.x * 0.02;

//         smallParticles.rotation.x =
//             Math.sin(time * 0.14) * 0.02;


//         // -----------------------------------------------------
//         // Subtle pulsing glow
//         // -----------------------------------------------------

//         particleMaterial.opacity =
//             0.82 +
//             Math.sin(time * 2.0) *
//             0.08;

//         glowMaterial.opacity =
//             0.08 +
//             Math.sin(time * 1.5) *
//             0.035;


//         // -----------------------------------------------------
//         // Rebuild network periodically
//         // -----------------------------------------------------

//         if (
//             frame % (isMobile ? 5 : 3) === 0
//         ) {

//             updateConnections();
//         }


//         renderer.render(
//             scene,
//             camera
//         );
//     }


//     // =========================================================
//     // RESIZE
//     // =========================================================

//     window.addEventListener(
//         "resize",
//         function () {

//             camera.aspect =
//                 window.innerWidth /
//                 window.innerHeight;

//             camera.updateProjectionMatrix();


//             renderer.setSize(
//                 window.innerWidth,
//                 window.innerHeight
//             );

//         }
//     );


//     // =========================================================
//     // START
//     // =========================================================

//     updateConnections();

//     animate();

// })();
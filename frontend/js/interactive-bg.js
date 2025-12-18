// --- Interactive Background Script ---
const canvas = document.getElementById('interactive-bg');
if (canvas) {
    const ctx = canvas.getContext('2d');

    // Resize
    let width, height;
    const resize = () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    // Mouse
    const mouse = { x: null, y: null };
    window.addEventListener('mousemove', e => {
        mouse.x = e.x;
        mouse.y = e.y;
    });
    window.addEventListener('mouseleave', () => {
        mouse.x = null; mouse.y = null;
    });

    // Particles
    const particles = [];
    const particleCount = 60; // Density

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.5; // Slow movement
            this.vy = (Math.random() - 0.5) * 0.5;
            this.size = Math.random() * 2 + 1;
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;

            // Bounce
            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;

            // Mouse interaction (Attract)
            if (mouse.x != null) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < 150) {
                    this.x += dx * 0.01;
                    this.y += dy * 0.01;
                }
            }
        }
        draw() {
            ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // Init
    for (let i = 0; i < particleCount; i++) particles.push(new Particle());

    // Animate
    const animate = () => {
        ctx.clearRect(0, 0, width, height);

        // Draw particles and lines
        particles.forEach((p, index) => {
            p.update();
            p.draw();

            // Connect particles
            for (let j = index + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 150) {
                    ctx.strokeStyle = `rgba(255, 255, 255, ${0.1 - dist / 1500})`; // Fade out
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }

            // Connect to mouse
            if (mouse.x != null) {
                const dx = p.x - mouse.x;
                const dy = p.y - mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 200) {
                    ctx.strokeStyle = `rgba(16, 185, 129, ${0.2 - dist / 1000})`; // Green accent near mouse
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.stroke();
                }
            }
        });

        requestAnimationFrame(animate);
    };
    animate();
}

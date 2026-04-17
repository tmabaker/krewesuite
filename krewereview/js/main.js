/* ============================================
   KreweReview Landing Page — Main JS
   Scroll animations, form handling, mobile menu,
   hero particle canvas
   ============================================ */

(function () {
    'use strict';

    // --- Hero Canvas: Floating Particles ---
    const canvas = document.getElementById('heroCanvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let particles = [];
        let animId;
        let w, h;

        const COLORS = [
            'rgba(91, 45, 142, 0.35)',   // purple
            'rgba(212, 168, 67, 0.3)',    // gold
            'rgba(27, 107, 58, 0.3)',     // green
            'rgba(255, 255, 255, 0.08)',  // white dim
        ];

        function resize() {
            w = canvas.width = canvas.offsetWidth;
            h = canvas.height = canvas.offsetHeight;
        }

        function createParticles() {
            const count = Math.min(Math.floor((w * h) / 18000), 80);
            particles = [];
            for (let i = 0; i < count; i++) {
                particles.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    r: Math.random() * 2.5 + 0.5,
                    dx: (Math.random() - 0.5) * 0.3,
                    dy: (Math.random() - 0.5) * 0.3,
                    color: COLORS[Math.floor(Math.random() * COLORS.length)],
                    pulse: Math.random() * Math.PI * 2,
                    pulseSpeed: Math.random() * 0.01 + 0.005,
                });
            }
        }

        function draw() {
            ctx.clearRect(0, 0, w, h);

            for (const p of particles) {
                p.x += p.dx;
                p.y += p.dy;
                p.pulse += p.pulseSpeed;

                if (p.x < -10) p.x = w + 10;
                if (p.x > w + 10) p.x = -10;
                if (p.y < -10) p.y = h + 10;
                if (p.y > h + 10) p.y = -10;

                const scale = 0.7 + 0.3 * Math.sin(p.pulse);
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r * scale, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();
            }

            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 120) {
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = `rgba(255, 255, 255, ${0.03 * (1 - dist / 120)})`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }

            animId = requestAnimationFrame(draw);
        }

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        function initCanvas() {
            resize();
            createParticles();
            if (!prefersReducedMotion.matches) {
                draw();
            } else {
                draw();
                cancelAnimationFrame(animId);
            }
        }

        window.addEventListener('resize', () => {
            resize();
            createParticles();
        });

        initCanvas();
        prefersReducedMotion.addEventListener('change', () => {
            cancelAnimationFrame(animId);
            if (!prefersReducedMotion.matches) draw();
        });
    }

    // --- Navigation: Scroll Effect ---
    const nav = document.getElementById('nav');

    function handleNavScroll() {
        const scrollY = window.scrollY;
        if (scrollY > 60) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    }

    window.addEventListener('scroll', handleNavScroll, { passive: true });

    // --- Mobile Menu ---
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            const isOpen = navLinks.classList.toggle('open');
            navToggle.classList.toggle('active');
            navToggle.setAttribute('aria-expanded', isOpen);
            document.body.style.overflow = isOpen ? 'hidden' : '';
        });

        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('open');
                navToggle.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            });
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && navLinks.classList.contains('open')) {
                navLinks.classList.remove('open');
                navToggle.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            }
        });
    }

    // --- Smooth Scroll for anchor links ---
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', (e) => {
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                e.preventDefault();
                const offset = nav.offsetHeight + 12;
                const top = target.getBoundingClientRect().top + window.scrollY - offset;
                window.scrollTo({ top, behavior: 'smooth' });
            }
        });
    });

    // --- Scroll Reveal ---
    const revealElements = document.querySelectorAll('.reveal');

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
        );

        revealElements.forEach(el => observer.observe(el));
    } else {
        revealElements.forEach(el => el.classList.add('visible'));
    }

    // --- Contact Form ---
    const form = document.getElementById('contactForm');
    const formSuccess = document.getElementById('formSuccess');

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            const fullName = form.querySelector('#fullName');
            const company = form.querySelector('#company');
            const email = form.querySelector('#email');
            let valid = true;

            [fullName, company, email].forEach(field => {
                field.classList.remove('error');
                if (!field.value.trim()) {
                    field.classList.add('error');
                    valid = false;
                }
            });

            if (email.value.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
                email.classList.add('error');
                valid = false;
            }

            if (!valid) {
                const firstError = form.querySelector('.error');
                if (firstError) firstError.focus();
                return;
            }

            const data = {
                fullName: fullName.value.trim(),
                company: company.value.trim(),
                email: email.value.trim(),
                phone: form.querySelector('#phone').value.trim(),
                contracts: form.querySelector('#contracts').value,
                message: form.querySelector('#message').value.trim(),
                product: 'KreweReview',
                timestamp: new Date().toISOString(),
            };

            try {
                const submissions = JSON.parse(localStorage.getItem('krewesuite_submissions') || '[]');
                submissions.push(data);
                localStorage.setItem('krewesuite_submissions', JSON.stringify(submissions));
            } catch (err) {
                console.warn('Could not save to localStorage:', err);
            }

            form.hidden = true;
            formSuccess.hidden = false;
        });

        form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('input', () => {
                field.classList.remove('error');
            });
        });
    }

    // --- Active nav link highlighting ---
    const sections = document.querySelectorAll('section[id]');
    const navLinksAll = document.querySelectorAll('.nav-links a[href^="#"]');

    function updateActiveNav() {
        const scrollY = window.scrollY + nav.offsetHeight + 100;

        sections.forEach(section => {
            const top = section.offsetTop;
            const height = section.offsetHeight;
            const id = section.getAttribute('id');

            if (scrollY >= top && scrollY < top + height) {
                navLinksAll.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }

    window.addEventListener('scroll', updateActiveNav, { passive: true });
})();

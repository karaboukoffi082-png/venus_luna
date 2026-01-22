document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. GESTION DU CARROUSEL (HERO SECTION) ---
    const slides = document.querySelectorAll('.hero-slide');
    let currentSlide = 0;

    if (slides.length > 0) {
        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.remove('active');
                if (i === index) {
                    slide.classList.add('active');
                }
            });
        }

        function nextSlide() {
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide);
        }

        // Initialisation du carrousel
        showSlide(currentSlide);
        setInterval(nextSlide, 5000); // Change toutes les 5 secondes
    }

    // --- 2. ANIMATIONS AU DÉFILEMENT (SCROLL REVEAL) ---
    const observerOptions = {
        root: null,
        threshold: 0.1 // Déclenche à 10% de visibilité
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Éléments à surveiller pour l'animation
    const animatableElements = document.querySelectorAll(
        'main, .section-title, .card, .product-item, .value-card, .testimonial-card, footer .col-lg-4, footer .col-lg-2, footer .col-lg-3'
    );

    animatableElements.forEach(el => {
        // Préparer l'état initial (masqué et légèrement décalé vers le bas)
        el.style.opacity = "0";
        el.style.transform = "translateY(20px)";
        el.style.transition = "opacity 0.8s ease-out, transform 0.8s ease-out";
        
        // Lancer l'observation
        observer.observe(el);
    });

    console.log("🚀 Système d'animations et carrousel initialisés !");
});
// MSBTE Student Saver Interactive Motion & Animation System
document.addEventListener('DOMContentLoaded', function() {
    // 1. Sidebar Toggle & Mobile Off-canvas Handlers
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarClose = document.getElementById('sidebarClose');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');
    const wrapper = document.getElementById('wrapper');
    
    function toggleSidebar() {
        if (wrapper) wrapper.classList.toggle('toggled');
    }

    function closeSidebar() {
        if (wrapper) wrapper.classList.remove('toggled');
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSidebar();
        });
    }

    if (sidebarClose) {
        sidebarClose.addEventListener('click', function(e) {
            e.preventDefault();
            closeSidebar();
        });
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener('click', function() {
            closeSidebar();
        });
    }

    // Auto-close sidebar on mobile when navigating
    document.querySelectorAll('#sidebar-wrapper .nav-link').forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 992) {
                closeSidebar();
            }
        });
    });

    // 2. Dynamic Number Counter Animation for KPI Values
    function animateCounters() {
        const counters = document.querySelectorAll('.kpi-val, .count-up');
        counters.forEach(counter => {
            const text = counter.innerText.trim();
            const hasPercent = text.includes('%');
            const numericValue = parseFloat(text.replace('%', ''));
            
            if (isNaN(numericValue)) return;

            const duration = 1200; // ms
            const frameRate = 30;
            const totalFrames = Math.round(duration / (1000 / frameRate));
            let frame = 0;

            counter.innerText = hasPercent ? '0%' : '0';

            const timer = setInterval(() => {
                frame++;
                const progress = frame / totalFrames;
                // Ease-out cubic formula
                const current = (1 - Math.pow(1 - progress, 3)) * numericValue;

                if (Number.isInteger(numericValue)) {
                    counter.innerText = Math.round(current) + (hasPercent ? '%' : '');
                } else {
                    counter.innerText = current.toFixed(1) + (hasPercent ? '%' : '');
                }

                if (frame >= totalFrames) {
                    clearInterval(timer);
                    counter.innerText = text;
                }
            }, 1000 / frameRate);
        });
    }

    animateCounters();

    // 3. Interactive Button Ripple Effect
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const rect = button.getBoundingClientRect();
            const circle = document.createElement('span');
            const diameter = Math.max(button.clientWidth, button.clientHeight);
            const radius = diameter / 2;

            circle.style.width = circle.style.height = `${diameter}px`;
            circle.style.left = `${e.clientX - rect.left - radius}px`;
            circle.style.top = `${e.clientY - rect.top - radius}px`;
            circle.style.position = 'absolute';
            circle.style.borderRadius = '50%';
            circle.style.background = 'rgba(255, 255, 255, 0.4)';
            circle.style.transform = 'scale(0)';
            circle.style.animation = 'ripple 0.6s linear';
            circle.style.pointerEvents = 'none';

            const existingRipple = button.querySelector('.btn-ripple');
            if (existingRipple) existingRipple.remove();

            circle.classList.add('btn-ripple');
            button.appendChild(circle);

            setTimeout(() => circle.remove(), 600);
        });
    });

    // 4. Staggered Entrance Animations for Cards
    const cards = document.querySelectorAll('.kpi-card-modern, .card-clean');
    cards.forEach((card, idx) => {
        card.style.animation = `fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) ${idx * 0.07}s both`;
    });

    // 5. Auto-Dismiss Flash Alerts with Fade Slide
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'all 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-15px)';
            setTimeout(() => {
                const bsAlert = bootstrap.Alert.getInstance(alert);
                if (bsAlert) bsAlert.close();
                else alert.remove();
            }, 500);
        }, 5000);
    });
});

// Inject Ripple Keyframes Dynamically
const style = document.createElement('style');
style.innerHTML = `
@keyframes ripple {
    to {
        transform: scale(4);
        opacity: 0;
    }
}
`;
document.head.appendChild(style);

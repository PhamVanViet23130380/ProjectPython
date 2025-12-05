$(document).ready(function() {
    // Smooth scroll for anchor links
    $('a[href^="#"]').on('click', function(e) {
        const target = $(this.getAttribute('href'));
        if (target.length) {
            e.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 140
            }, 600);
        }
    });

    // Scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.content-block, .policy-card, .cancellation-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });

    // Timeline animation
    const timelineObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateX(0)';
                }, index * 100);
            }
        });
    }, { threshold: 0.2 });

    $('.timeline-item').each(function() {
        this.style.opacity = '0';
        this.style.transform = 'translateX(-30px)';
        this.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        timelineObserver.observe(this);
    });

    // Back to top button
    const backToTop = $('<button>')
        .addClass('back-to-top')
        .html('<i class="fas fa-arrow-up"></i>')
        .css({
            position: 'fixed',
            bottom: '30px',
            right: '30px',
            background: '#FF385C',
            color: 'white',
            border: 'none',
            width: '50px',
            height: '50px',
            borderRadius: '50%',
            fontSize: '20px',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            display: 'none',
            zIndex: 1000,
            transition: 'all 0.3s ease'
        });

    $('body').append(backToTop);

    $(window).scroll(function() {
        if ($(this).scrollTop() > 500) {
            backToTop.fadeIn();
        } else {
            backToTop.fadeOut();
        }
    });

    backToTop.on('click', function() {
        $('html, body').animate({scrollTop: 0}, 600);
    });

    backToTop.hover(
        function() { $(this).css('background', '#E31C5F'); },
        function() { $(this).css('background', '#FF385C'); }
    );
});

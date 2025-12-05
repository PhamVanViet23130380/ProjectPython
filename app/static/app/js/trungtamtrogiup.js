// Tab switching functionality
document.addEventListener('DOMContentLoaded', function() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all tabs
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked tab
            this.classList.add('active');

            // Show corresponding content
            const tabId = this.getAttribute('data-tab');
            const content = document.getElementById(`${tabId}-content`);
            if (content) {
                content.classList.add('active');
            }
        });
    });

    // Search functionality
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');

    searchBtn.addEventListener('click', function() {
        const query = searchInput.value.trim();
        if (query) {
            console.log('Searching for:', query);
            // TODO: Implement actual search functionality
            alert('Tính năng tìm kiếm đang được phát triển. Bạn đã tìm kiếm: ' + query);
        }
    });

    // Search on Enter key
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });

    // Add smooth scroll to top when clicking help cards
    const helpCards = document.querySelectorAll('.help-card');
    helpCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.classList.contains('card-link')) {
                const link = this.querySelector('.card-link');
                if (link) {
                    link.click();
                }
            }
        });
    });

    // Contact card click handlers
    const contactCards = document.querySelectorAll('.contact-card');
    contactCards.forEach(card => {
        card.addEventListener('click', function() {
            const method = this.querySelector('h4').textContent;
            console.log('Contact method selected:', method);
            
            if (method === 'Gọi cho chúng tôi') {
                alert('Vui lòng gọi: 1900-xxxx để được hỗ trợ');
            } else if (method === 'Email') {
                window.location.href = 'mailto:support@homenest.vn';
            } else if (method === 'Chat trực tuyến') {
                alert('Tính năng chat trực tuyến đang được phát triển');
            }
        });
    });

    // Topic link analytics
    const topicLinks = document.querySelectorAll('.topic-link');
    topicLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const topic = this.querySelector('span').textContent;
            console.log('Topic clicked:', topic);
            
            // Chỉ chặn các link không có href thực tế (href="#")
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
                alert('Đang chuyển đến chủ đề: ' + topic);
            }
            // Các link có href thực tế sẽ được phép chuyển trang bình thường
        });
    });

    // Add animation to cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all help cards and topic links
    document.querySelectorAll('.help-card, .topic-link, .contact-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.5s ease';
        observer.observe(el);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    const offsetTop = targetElement.offsetTop - 140;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Contact button functionality
    const contactBtn = document.querySelector('.btn-contact');
    if (contactBtn) {
        contactBtn.addEventListener('click', function() {
            showContactModal();
        });
    }

    function showContactModal() {
        // Create modal overlay
        const modal = document.createElement('div');
        modal.className = 'contact-modal-overlay';
        modal.innerHTML = `
            <div class="contact-modal">
                <div class="modal-header">
                    <h3>Liên hệ với chúng tôi</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Vui lòng chọn phương thức liên hệ phù hợp:</p>
                    <div class="contact-options">
                        <button class="contact-option">
                            <i class="fas fa-comments"></i>
                            <span>Chat trực tuyến</span>
                            <small>Thời gian phản hồi: ~2 phút</small>
                        </button>
                        <button class="contact-option">
                            <i class="fas fa-phone"></i>
                            <span>Gọi điện thoại</span>
                            <small>Hỗ trợ 24/7</small>
                        </button>
                        <button class="contact-option">
                            <i class="fas fa-envelope"></i>
                            <span>Gửi email</span>
                            <small>Phản hồi trong 24h</small>
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Add modal styles
        const style = document.createElement('style');
        style.textContent = `
            .contact-modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                animation: fadeIn 0.3s ease;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            .contact-modal {
                background: white;
                border-radius: 12px;
                max-width: 500px;
                width: 90%;
                animation: slideUp 0.3s ease;
            }

            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .contact-modal .modal-header {
                padding: 24px;
                border-bottom: 1px solid #EBEBEB;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .contact-modal .modal-header h3 {
                margin: 0;
                font-size: 22px;
                font-weight: 700;
                color: #222;
            }

            .modal-close {
                background: none;
                border: none;
                font-size: 32px;
                color: #717171;
                cursor: pointer;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: all 0.3s ease;
            }

            .modal-close:hover {
                background: #F7F7F7;
                color: #222;
            }

            .contact-modal .modal-body {
                padding: 24px;
            }

            .contact-modal .modal-body p {
                margin-bottom: 20px;
                color: #717171;
                font-size: 15px;
            }

            .contact-options {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .contact-option {
                background: #F7F7F7;
                border: 2px solid transparent;
                border-radius: 8px;
                padding: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: left;
                display: flex;
                align-items: center;
                gap: 16px;
            }

            .contact-option:hover {
                border-color: #FF385C;
                background: white;
                transform: translateX(4px);
            }

            .contact-option i {
                font-size: 28px;
                color: #FF385C;
            }

            .contact-option span {
                display: block;
                font-weight: 600;
                color: #222;
                font-size: 16px;
                margin-bottom: 4px;
            }

            .contact-option small {
                display: block;
                color: #717171;
                font-size: 13px;
            }
        `;
        document.head.appendChild(style);

        document.body.appendChild(modal);

        // Close modal functionality
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.addEventListener('click', function() {
            modal.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                modal.remove();
                style.remove();
            }, 300);
        });

        // Close on overlay click
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => {
                    modal.remove();
                    style.remove();
                }, 300);
            }
        });

        // Handle contact option clicks
        const contactOptions = modal.querySelectorAll('.contact-option');
        contactOptions.forEach(option => {
            option.addEventListener('click', function() {
                const optionText = this.querySelector('span').textContent;
                showNotification(`Đang kết nối đến ${optionText}...`);
                modal.remove();
                style.remove();
            });
        });
    }

    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'custom-notification';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 24px;
            background: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: center;
            gap: 12px;
            z-index: 10001;
            animation: slideIn 0.3s ease;
        `;
        
        const icon = notification.querySelector('i');
        icon.style.cssText = `
            color: #06A644;
            font-size: 20px;
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    // Highlight current section in TOC
    const sections = document.querySelectorAll('.content-block[id]');
    const tocLinks = document.querySelectorAll('.toc-list a');

    function highlightTOC() {
        let currentSection = '';
        const scrollPos = window.scrollY + 200;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;

            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                currentSection = section.getAttribute('id');
            }
        });

        tocLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + currentSection) {
                link.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', highlightTOC);
    highlightTOC(); // Initial call

    // Add animation on scroll
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

    // Observe payment cards
    document.querySelectorAll('.payment-method-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease';
        observer.observe(card);
    });
});

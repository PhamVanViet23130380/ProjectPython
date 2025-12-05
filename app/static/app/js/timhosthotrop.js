document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchBtn = document.querySelector('.search-btn');
    const searchInput = document.querySelector('.search-input');

    searchBtn.addEventListener('click', function() {
        performSearch();
    });

    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    function performSearch() {
        const searchTerm = searchInput.value.trim();
        if (searchTerm) {
            console.log('Đang tìm kiếm:', searchTerm);
            // Simulate search
            showLoadingState();
            setTimeout(() => {
                showNoResults();
            }, 1500);
        }
    }

    function showLoadingState() {
        const noResultsSection = document.querySelector('.no-results-section');
        noResultsSection.style.opacity = '0.5';
    }

    function showNoResults() {
        const noResultsSection = document.querySelector('.no-results-section');
        noResultsSection.style.opacity = '1';
    }

    // Notify button functionality
    const notifyBtn = document.querySelector('.notify-btn');

    notifyBtn.addEventListener('click', function() {
        this.disabled = true;
        this.textContent = 'Đang xử lý...';
        
        // Simulate API call
        setTimeout(() => {
            this.textContent = 'Đã đăng ký thành công ✓';
            this.style.background = '#06A644';
            
            // Show confirmation message
            showNotification('Bạn sẽ nhận được thông báo qua email khi có host hỗ trợ trong khu vực của bạn.');
            
            // Reset button after 3 seconds
            setTimeout(() => {
                this.disabled = false;
                this.textContent = 'Thông báo cho tôi';
                this.style.background = '#222';
            }, 3000);
        }, 1500);
    });

    function showNotification(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'custom-notification';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        
        // Add styles
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
            z-index: 10000;
            animation: slideIn 0.3s ease;
            max-width: 400px;
        `;
        
        // Add icon style
        const icon = notification.querySelector('i');
        icon.style.cssText = `
            color: #06A644;
            font-size: 20px;
        `;
        
        // Add animation
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
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                notification.remove();
                style.remove();
            }, 300);
        }, 5000);
    }

    // Add smooth scroll animation
    window.addEventListener('scroll', function() {
        const illustration = document.querySelector('.illustration');
        const scrolled = window.pageYOffset;
        const rate = scrolled * 0.3;
        
        if (illustration) {
            illustration.style.transform = `translateY(${rate}px)`;
        }
    });

    // Add entrance animation
    const noResultsSection = document.querySelector('.no-results-section');
    noResultsSection.style.opacity = '0';
    noResultsSection.style.transform = 'translateY(30px)';
    
    setTimeout(() => {
        noResultsSection.style.transition = 'all 0.6s ease';
        noResultsSection.style.opacity = '1';
        noResultsSection.style.transform = 'translateY(0)';
    }, 200);
});

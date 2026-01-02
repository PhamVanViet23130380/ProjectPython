// Search Results Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Sort buttons
    const sortBtns = document.querySelectorAll('.sort-btn');
    const filterForm = document.getElementById('filterForm');
    
    sortBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const sortValue = this.dataset.sort;
            
            // Create URL with sort parameter
            const url = new URL(window.location.href);
            url.searchParams.set('sort', sortValue);
            url.searchParams.delete('page'); // Reset to first page
            
            // Redirect to new URL
            window.location.href = url.toString();
        });
    });

    // Clear all filters
    const clearFiltersBtn = document.querySelector('.clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            // Get base URL without query parameters
            const baseUrl = window.location.origin + window.location.pathname;
            window.location.href = baseUrl;
        });
    }

    // Auto-submit form when checkboxes change
    const checkboxes = filterForm.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Optional: Auto-submit on checkbox change
            // filterForm.submit();
        });
    });

    // Price range validation
    const minPriceInput = document.getElementById('min_price');
    const maxPriceInput = document.getElementById('max_price');
    
    if (minPriceInput && maxPriceInput) {
        minPriceInput.addEventListener('change', function() {
            const minVal = parseFloat(this.value) || 0;
            const maxVal = parseFloat(maxPriceInput.value) || Infinity;
            
            if (minVal > maxVal && maxVal > 0) {
                alert('Giá tối thiểu không thể lớn hơn giá tối đa');
                this.value = '';
            }
        });
        
        maxPriceInput.addEventListener('change', function() {
            const minVal = parseFloat(minPriceInput.value) || 0;
            const maxVal = parseFloat(this.value) || Infinity;
            
            if (maxVal < minVal && minVal > 0) {
                alert('Giá tối đa không thể nhỏ hơn giá tối thiểu');
                this.value = '';
            }
        });
    }

    // Smooth scroll to top when changing pages
    const paginationLinks = document.querySelectorAll('.pagination-btn');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    // Toggle mobile filters (if needed for responsive design)
    function initMobileFilters() {
        if (window.innerWidth <= 768) {
            const sidebar = document.querySelector('.filter-sidebar');
            if (!sidebar) return;

            // Create backdrop if not exists
            let backdrop = document.getElementById('mobileFilterBackdrop');
            if (!backdrop) {
                backdrop = document.createElement('div');
                backdrop.id = 'mobileFilterBackdrop';
                backdrop.className = 'mobile-filter-backdrop';
                document.body.appendChild(backdrop);

                backdrop.addEventListener('click', function() {
                    sidebar.classList.remove('mobile-open');
                    backdrop.classList.remove('show');
                });
            }

            // Create toggle button if not exists
            let toggleBtn = document.getElementById('mobileFilterToggle');
            if (!toggleBtn) {
                toggleBtn = document.createElement('button');
                toggleBtn.id = 'mobileFilterToggle';
                toggleBtn.className = 'mobile-filter-toggle';
                toggleBtn.innerHTML = '<i class="fa-solid fa-sliders"></i> Bộ lọc';
                
                const resultsMain = document.querySelector('.results-main');
                if (resultsMain) {
                    resultsMain.insertBefore(toggleBtn, resultsMain.firstChild);
                }

                toggleBtn.addEventListener('click', function() {
                    sidebar.classList.toggle('mobile-open');
                    backdrop.classList.toggle('show');
                });
            }
        } else {
            // Remove mobile elements on desktop
            const backdrop = document.getElementById('mobileFilterBackdrop');
            const toggleBtn = document.getElementById('mobileFilterToggle');
            if (backdrop) backdrop.remove();
            if (toggleBtn) toggleBtn.remove();
            
            const sidebar = document.querySelector('.filter-sidebar');
            if (sidebar) sidebar.classList.remove('mobile-open');
        }
    }

    // Initialize mobile features
    initMobileFilters();
    window.addEventListener('resize', initMobileFilters);

    // Format number inputs
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                const value = parseFloat(this.value);
                if (!isNaN(value)) {
                    this.value = Math.round(value);
                }
            }
        });
    });

    // Highlight active filters
    function highlightActiveFilters() {
        const activeFilters = [];
        
        // Check price filters
        if (minPriceInput && minPriceInput.value) {
            activeFilters.push('Giá tối thiểu: ' + minPriceInput.value + '₫');
        }
        if (maxPriceInput && maxPriceInput.value) {
            activeFilters.push('Giá tối đa: ' + maxPriceInput.value + '₫');
        }
        
        // Check checkboxes
        const checkedBoxes = filterForm.querySelectorAll('input[type="checkbox"]:checked');
        if (checkedBoxes.length > 0) {
            activeFilters.push(checkedBoxes.length + ' tiện nghi đã chọn');
        }
        
        // Display active filters count
        if (activeFilters.length > 0) {
            const filterHeader = document.querySelector('.filter-header h2');
            if (filterHeader && !filterHeader.querySelector('.filter-count')) {
                const countBadge = document.createElement('span');
                countBadge.className = 'filter-count';
                countBadge.textContent = ` (${activeFilters.length})`;
                filterHeader.appendChild(countBadge);
            }
        }
    }

    highlightActiveFilters();
});

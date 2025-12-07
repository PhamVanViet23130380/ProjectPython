// Address Page Script
document.addEventListener('DOMContentLoaded', function() {
    const addressInput = document.getElementById('addressInput');
    const useCurrentLocation = document.getElementById('useCurrentLocation');
    const nextBtn = document.querySelector('.next-btn');
    const backLink = document.querySelector('.back-link');

    // Validate if address is entered
    function validateForm() {
        const hasAddress = addressInput.value.trim() !== '';
        nextBtn.disabled = !hasAddress;
    }

    // Input validation on typing
    addressInput.addEventListener('input', validateForm);

    // Use current location
    useCurrentLocation.addEventListener('change', function() {
        if (this.checked) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const { latitude, longitude } = position.coords;
                    // Store coordinates
                    sessionStorage.setItem('latitude', latitude);
                    sessionStorage.setItem('longitude', longitude);
                    addressInput.value = `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
                    validateForm();
                });
            } else {
                alert('Trình duyệt của bạn không hỗ trợ vị trí.');
                useCurrentLocation.checked = false;
            }
        }
    });

    // Next button click
    nextBtn.addEventListener('click', function() {
        if (addressInput.value.trim()) {
            // Store address
            sessionStorage.setItem('address', addressInput.value);
            // Navigate to next page
            window.location.href = '/duocuse/';
        }
    });

    // Back button
        backLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/duocuse/';
        });

    // Help button
    document.querySelector('.btnThacMac')?.addEventListener('click', function() {
        alert('Liên hệ support: support@homenest.com');
    });

    // Exit button
    document.querySelector('.btnLuuThoat')?.addEventListener('click', function() {
        if (confirm('Bạn chắc chắn muốn thoát? Dữ liệu chưa lưu sẽ bị mất.')) {
            window.location.href = '/';
        }
    });

    // Initial validation
    validateForm();
});

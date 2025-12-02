(function() {
    // 1. Khai báo và lấy phần tử
    const overlay = document.getElementById('host-modal-overlay');
    if (!overlay) return; // Thoát nếu không tìm thấy modal

    const closeBtn = overlay.querySelector('.host-modal-close');
    const nextBtn = overlay.querySelector('.host-modal-next');
    const options = overlay.querySelectorAll('.host-option');
    const hostBtns = document.querySelectorAll('.host-btn');

    // 2. Hàm Tắt/Mở Modal (sử dụng ClassList.toggle)
    function toggleModal(open = false) {
        overlay.classList.toggle('is-open', open);
        overlay.setAttribute('aria-hidden', (!open).toString());

        if (open) {
            const firstInput = overlay.querySelector('input[name="host-type"]');
            if (firstInput) firstInput.focus();
        }
    }

    // 3. Gắn Sự Kiện Khởi Tạo
    function initializeEvents() {
        // Mở Modal
        hostBtns.forEach(el => {
            el.style.cursor = 'pointer';
            el.addEventListener('click', (e) => {
                e.preventDefault();
                toggleModal(true);
            });
        });

        // Đóng Modal
        if (closeBtn) closeBtn.addEventListener('click', () => toggleModal(false));
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) toggleModal(false);
        });

        // Xử lý Tùy chọn (Option Selection)
        options.forEach(opt => {
            opt.addEventListener('click', function() {
                const input = this.querySelector('input[name="host-type"]');
                if (input) input.checked = true;

                // Cập nhật trạng thái 'selected'
                options.forEach(o => o.classList.remove('selected'));
                this.classList.add('selected');

                if (nextBtn) nextBtn.disabled = false;
            });
        });

        // Xử lý Nút Tiếp Tục (Next Button)
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                const chosen = overlay.querySelector('input[name="host-type"]:checked');
                if (!chosen) return;
                console.log('Selected host type:', chosen.value);
                toggleModal(false);
            });
        }
    }

    // Chạy hàm khởi tạo
    initializeEvents();
})();

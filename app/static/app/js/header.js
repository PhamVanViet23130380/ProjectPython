window.addEventListener('load', () => {
    const menuBtn      = document.querySelector('.ab-icon[aria-label="Menu"]');
    const menuDropdown = document.getElementById('menuDropdown');

    if (!menuBtn || !menuDropdown) return;

    // Bấm icon = bật/tắt menu
    menuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        menuDropdown.classList.toggle('active');
    });

    // Click ra ngoài = đóng menu
    document.addEventListener('click', (e) => {
        if (!menuDropdown.contains(e.target) && !menuBtn.contains(e.target)) {
            menuDropdown.classList.remove('active');
        }
    });
});
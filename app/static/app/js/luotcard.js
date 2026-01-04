function _findWrapper(btn) {
    const sectionAncestor = btn.closest('.cards-section')
    if (!sectionAncestor) return null;
    return sectionAncestor.querySelector('.cards-wrapper');
}

function slideLeft(btn) {
    const wrapper = _findWrapper(btn);
    if (!wrapper) return;
    wrapper.scrollLeft -= 350;
}

function slideRight(btn) {
    const wrapper = _findWrapper(btn);
    if (!wrapper) return;
    wrapper.scrollLeft += 350;
}

// Add click event listeners to all room cards
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.card[data-room-id]');
    cards.forEach(card => {
        card.addEventListener('click', function() {
            const roomId = this.getAttribute('data-room-id');
            if (roomId) {
                window.location.href = `/chitietnoio/${roomId}/`;
            }
        });
    });
});


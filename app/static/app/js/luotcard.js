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


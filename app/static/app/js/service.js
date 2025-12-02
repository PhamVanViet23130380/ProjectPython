function slideLeft(btn) {
    const wrapper = btn.closest(".service-section").querySelector(".scroll-wrapper");
    wrapper.scrollLeft -= 350; // lướt sang trái 1 card
}

function slideRight(btn) {
    const wrapper = btn.closest(".service-section").querySelector(".scroll-wrapper");
    wrapper.scrollLeft += 350; // lướt sang phải 1 card
}


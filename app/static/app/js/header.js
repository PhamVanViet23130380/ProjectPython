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

window.addEventListener('load', () => {
    const panelWrap   = document.getElementById('searchPanelWrap');
    const panels      = document.querySelectorAll('.search-panel');
    const triggers    = document.querySelectorAll('.search-trigger');
    const backdrop    = document.getElementById('searchBackdrop');
    const locationInp = document.getElementById('locationInput');

    const valueEls = {
        location: document.querySelector('.value[data-field="location"]'),
        dates: document.querySelector('.value[data-field="dates"]'),
        guests: document.querySelector('.value[data-field="guests"]'),
    };

    Object.values(valueEls).forEach((el) => {
        if (el && !el.dataset.placeholder) {
            el.dataset.placeholder = el.textContent.trim();
        }
    });

    const guestState = { adults: 0, children: 0, infants: 0, pets: 0 };

    const setValue = (field, text) => {
        if (valueEls[field]) {
            valueEls[field].textContent = text && text.trim() ? text : valueEls[field].dataset.placeholder || valueEls[field].textContent;
        }
    };

    const openPanel = (name) => {
        if (!panelWrap) return;
        panelWrap.classList.add('open');
        panelWrap.style.display = 'block';
        if (backdrop) backdrop.classList.add('show');
        panels.forEach((p) => p.classList.toggle('active', p.dataset.panel === name));
        triggers.forEach((t) => t.classList.toggle('active', t.dataset.panel === name));
    };

    const closePanels = () => {
        if (panelWrap) {
            panelWrap.classList.remove('open');
            panelWrap.style.display = 'none';
        }
        if (backdrop) backdrop.classList.remove('show');
        panels.forEach((p) => p.classList.remove('active'));
        triggers.forEach((t) => t.classList.remove('active'));
    };

    const handleTrigger = (trigger) => {
        const targetPanel = trigger.dataset.panel;
        if (!targetPanel) return;

        const open = () => openPanel(targetPanel);

        trigger.addEventListener('click', () => {
            open();
        });

        trigger.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                open();
            }
        });
    };

    triggers.forEach(handleTrigger);

    const searchBar = document.querySelector('.ab-search');
    if (searchBar) {
        searchBar.addEventListener('click', () => {
            if (!panelWrap || panelWrap.classList.contains('open')) return;
            openPanel('location');
        });
    }

    if (backdrop) {
        backdrop.addEventListener('click', closePanels);
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closePanels();
    });

    document.addEventListener('click', (e) => {
        const searchBar = document.querySelector('.ab-search');
        if (!panelWrap || !panelWrap.classList.contains('open')) return;
        if (panelWrap.contains(e.target) || (searchBar && searchBar.contains(e.target))) return;
        closePanels();
    });

    // Location suggestions
    const suggestionBtns = document.querySelectorAll('.suggestion-item');
    suggestionBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            const place = btn.dataset.place || btn.textContent.trim();
            if (locationInp) locationInp.value = place;
            setValue('location', place);
            openPanel('dates');
        });
    });

    if (locationInp) {
        locationInp.addEventListener('input', () => {
            const text = locationInp.value.trim();
            setValue('location', text || 'Tìm kiếm điểm đến');
        });
    }

    // Date tabs + quick ranges
    const dateTabs = document.querySelectorAll('.date-tabs .tab');
    dateTabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            dateTabs.forEach((t) => t.classList.remove('active'));
            tab.classList.add('active');
            setValue('dates', tab.textContent.trim());
        });
    });

    const rangeBtns = document.querySelectorAll('.range-btn');
    rangeBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            const value = btn.dataset.range ? `± ${btn.dataset.range} ngày` : 'Ngày chính xác';
            setValue('dates', value);
            openPanel('guests');
        });
    });

    const calendarDays = document.querySelectorAll('.calendar-grid span');
    calendarDays.forEach((day) => {
        if (day.classList.contains('muted')) return;
        day.addEventListener('click', () => {
            const monthWrap = day.closest('.calendar-month');
            const headingEl = monthWrap ? monthWrap.querySelector('.calendar-heading') : null;
            const monthTitle = headingEl ? headingEl.textContent.trim() : '';
            const dayNum = day.textContent.trim();
            if (dayNum) setValue('dates', `${dayNum} · ${monthTitle}`.trim());
            openPanel('guests');
        });
    });

    // Guest counters
    const renderGuests = () => {
        const total = guestState.adults + guestState.children;
        const parts = [];
        if (total > 0) parts.push(`${total} khách`);
        if (guestState.infants > 0) parts.push(`${guestState.infants} em bé`);
        if (guestState.pets > 0) parts.push(`${guestState.pets} thú cưng`);
        setValue('guests', parts.length ? parts.join(', ') : 'Thêm khách');
    };

    const rows = document.querySelectorAll('.guest-row');
    rows.forEach((row) => {
        const field = row.dataset.field;
        if (!field || !(field in guestState)) return;

        const minus = row.querySelector('.count-btn.minus');
        const plus = row.querySelector('.count-btn.plus');
        const countEl = row.querySelector('.count');

        const update = () => {
            if (countEl) countEl.textContent = guestState[field];
            if (minus) minus.disabled = guestState[field] <= 0;
            renderGuests();
        };

        if (plus) {
            plus.addEventListener('click', () => {
                guestState[field] += 1;
                update();
            });
        }

        if (minus) {
            minus.addEventListener('click', () => {
                guestState[field] = Math.max(0, guestState[field] - 1);
                update();
            });
        }

        update();
    });
});
document.addEventListener('DOMContentLoaded', () => {
    const menuBtn      = document.querySelector('.ab-icon[aria-label="Menu"]');
    const menuDropdown = document.getElementById('menuDropdown');

    if (!menuBtn || !menuDropdown) {
        console.log('Menu elements not found!', menuBtn, menuDropdown);
        return;
    }

    // Bấm icon = bật/tắt menu
    menuBtn.addEventListener('click', (e) => {
        e.preventDefault();
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

    // ========================
    // DYNAMIC CALENDAR
    // ========================
    let currentMonth = new Date().getMonth();
    let currentYear = new Date().getFullYear();
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Store selected dates
    let selectedCheckIn = null;
    let selectedCheckOut = null;
    let selectedCheckInDate = null;
    let selectedCheckOutDate = null;

    const monthNames = [
        'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
        'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'
    ];
    const dayNames = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'];

    function getDaysInMonth(month, year) {
        return new Date(year, month + 1, 0).getDate();
    }

    function getFirstDayOfMonth(month, year) {
        let day = new Date(year, month, 1).getDay();
        // Convert Sunday=0 to Monday=0 format
        return day === 0 ? 6 : day - 1;
    }

    function formatDateForDisplay(day, month, year) {
        return `${day} ${monthNames[month]} năm ${year}`;
    }

    function formatDateForAPI(day, month, year) {
        const m = String(month + 1).padStart(2, '0');
        const d = String(day).padStart(2, '0');
        return `${year}-${m}-${d}`;
    }

    function renderCalendar(month, year, containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        const heading = container.querySelector('.calendar-heading');
        const grid = container.querySelector('.calendar-grid');

        if (heading) {
            heading.textContent = `${monthNames[month]} năm ${year}`;
        }

        if (!grid) return;
        grid.innerHTML = '';

        // Day headers
        dayNames.forEach(d => {
            const span = document.createElement('span');
            span.className = 'day-header';
            span.textContent = d;
            grid.appendChild(span);
        });

        // Empty cells for first week
        const firstDay = getFirstDayOfMonth(month, year);
        for (let i = 0; i < firstDay; i++) {
            const span = document.createElement('span');
            span.className = 'empty';
            grid.appendChild(span);
        }

        // Days of month
        const daysInMonth = getDaysInMonth(month, year);
        for (let day = 1; day <= daysInMonth; day++) {
            const span = document.createElement('span');
            span.textContent = day;
            span.className = 'day';

            const cellDate = new Date(year, month, day);
            cellDate.setHours(0, 0, 0, 0);

            // Check if past date
            if (cellDate < today) {
                span.classList.add('muted', 'past');
            } else {
                span.classList.add('selectable');
                
                // Check if selected
                if (selectedCheckInDate && cellDate.getTime() === selectedCheckInDate.getTime()) {
                    span.classList.add('selected', 'check-in');
                }
                if (selectedCheckOutDate && cellDate.getTime() === selectedCheckOutDate.getTime()) {
                    span.classList.add('selected', 'check-out');
                }
                // Check if in range
                if (selectedCheckInDate && selectedCheckOutDate && 
                    cellDate > selectedCheckInDate && cellDate < selectedCheckOutDate) {
                    span.classList.add('in-range');
                }

                // Click handler
                span.addEventListener('click', (e) => {
                    e.stopPropagation();
                    handleDateClick(day, month, year);
                });
            }

            grid.appendChild(span);
        }
    }

    function handleDateClick(day, month, year) {
        const clickedDate = new Date(year, month, day);
        clickedDate.setHours(0, 0, 0, 0);

        if (!selectedCheckInDate || (selectedCheckInDate && selectedCheckOutDate)) {
            // First selection or reset
            selectedCheckInDate = clickedDate;
            selectedCheckOutDate = null;
            selectedCheckIn = formatDateForAPI(day, month, year);
            selectedCheckOut = null;
            setValue('dates', formatDateForDisplay(day, month, year));
        } else {
            // Second selection
            if (clickedDate <= selectedCheckInDate) {
                // Clicked before check-in, reset
                selectedCheckInDate = clickedDate;
                selectedCheckOutDate = null;
                selectedCheckIn = formatDateForAPI(day, month, year);
                selectedCheckOut = null;
                setValue('dates', formatDateForDisplay(day, month, year));
            } else {
                selectedCheckOutDate = clickedDate;
                selectedCheckOut = formatDateForAPI(day, month, year);
                const checkInDay = selectedCheckInDate.getDate();
                const checkInMonth = selectedCheckInDate.getMonth();
                const checkInYear = selectedCheckInDate.getFullYear();
                setValue('dates', `${formatDateForDisplay(checkInDay, checkInMonth, checkInYear)} - ${formatDateForDisplay(day, month, year)}`);
                
                // Open guests panel after selecting date range
                setTimeout(() => openPanel('guests'), 300);
            }
        }

        // Re-render calendars to update selection
        renderCalendars();
    }

    function renderCalendars() {
        renderCalendar(currentMonth, currentYear, '#calendarMonth1');
        
        let nextMonth = currentMonth + 1;
        let nextYear = currentYear;
        if (nextMonth > 11) {
            nextMonth = 0;
            nextYear++;
        }
        renderCalendar(nextMonth, nextYear, '#calendarMonth2');
    }

    // Navigation buttons
    const prevBtn = document.querySelector('.prev-month');
    const nextBtn = document.querySelector('.next-month');

    if (prevBtn) {
        prevBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            // Don't go before current month
            const now = new Date();
            if (currentYear > now.getFullYear() || 
                (currentYear === now.getFullYear() && currentMonth > now.getMonth())) {
                currentMonth--;
                if (currentMonth < 0) {
                    currentMonth = 11;
                    currentYear--;
                }
                renderCalendars();
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            currentMonth++;
            if (currentMonth > 11) {
                currentMonth = 0;
                currentYear++;
            }
            renderCalendars();
        });
    }

    // Initial render
    renderCalendars();

    // Date tabs handler
    const dateTabs = document.querySelectorAll('.date-tabs .tab');
    dateTabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            dateTabs.forEach((t) => t.classList.remove('active'));
            tab.classList.add('active');
        });
    });

    // Quick range buttons
    const rangeBtns = document.querySelectorAll('.range-btn');
    rangeBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            const value = btn.dataset.range ? `± ${btn.dataset.range} ngày` : 'Ngày chính xác';
            setValue('dates', value);
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

    // Search button handler
    const searchBtn = document.querySelector('.ab-search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    }

    function performSearch() {
        // Collect search parameters
        const params = new URLSearchParams();
        
        // Location
        const location = locationInp ? locationInp.value.trim() : '';
        if (location) {
            params.set('location', location);
        }
        
        // Dates
        if (selectedCheckIn) {
            params.set('check_in', selectedCheckIn);
        }
        if (selectedCheckOut) {
            params.set('check_out', selectedCheckOut);
        }
        
        // Guests
        if (guestState.adults > 0) {
            params.set('adults', guestState.adults);
        }
        if (guestState.children > 0) {
            params.set('children', guestState.children);
        }
        if (guestState.infants > 0) {
            params.set('infants', guestState.infants);
        }
        if (guestState.pets > 0) {
            params.set('pets', guestState.pets);
        }
        
        // Build search URL
        const searchUrl = '/search/?' + params.toString();
        
        // Navigate to search results
        window.location.href = searchUrl;
    }

    // Allow Enter key to trigger search in location input
    if (locationInp) {
        locationInp.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
});


/* ========================
   NOTIFICATION BELL
   ======================== */
document.addEventListener('DOMContentLoaded', () => {
    const notificationBell = document.getElementById('notificationBell');
    const notificationDropdown = document.getElementById('notificationDropdown');
    const notificationBadge = document.getElementById('notificationBadge');
    const notificationList = document.getElementById('notificationList');
    const markAllReadBtn = document.getElementById('markAllRead');

    if (!notificationBell) return;

    // Icon map cho các loại thông báo
    const iconMap = {
        'listing_approved': { icon: 'fa-solid fa-check-circle', class: 'approved' },
        'listing_rejected': { icon: 'fa-solid fa-times-circle', class: 'rejected' },
        'new_booking': { icon: 'fa-solid fa-calendar-plus', class: 'booking' },
        'booking_confirmed': { icon: 'fa-solid fa-calendar-check', class: 'booking' },
        'booking_cancelled': { icon: 'fa-solid fa-calendar-xmark', class: 'rejected' },
        'guest_checkin': { icon: 'fa-solid fa-door-open', class: 'checkin' },
        'guest_checkout': { icon: 'fa-solid fa-door-closed', class: 'checkout' },
        'booking_completed': { icon: 'fa-solid fa-flag-checkered', class: 'completed' },
        'payment_received': { icon: 'fa-solid fa-money-bill-wave', class: 'payment' },
        'review_received': { icon: 'fa-solid fa-star', class: 'review' },
    };

    // Toggle dropdown
    notificationBell.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const isOpen = notificationDropdown.classList.contains('show');
        
        // Close menu dropdown if open
        const menuDropdown = document.getElementById('menuDropdown');
        if (menuDropdown) menuDropdown.classList.remove('active');
        
        if (isOpen) {
            notificationDropdown.classList.remove('show');
        } else {
            notificationDropdown.classList.add('show');
            loadNotifications();
        }
    });

    // Click outside to close
    document.addEventListener('click', (e) => {
        if (notificationDropdown && 
            !notificationDropdown.contains(e.target) && 
            !notificationBell.contains(e.target)) {
            notificationDropdown.classList.remove('show');
        }
    });

    // Load notifications
    async function loadNotifications() {
        try {
            const response = await fetch('/notifications/api/');
            const data = await response.json();
            
            updateBadge(data.unread_count);
            renderNotifications(data.notifications);
        } catch (error) {
            console.error('Error loading notifications:', error);
            notificationList.innerHTML = '<div class="notification-empty">Không thể tải thông báo</div>';
        }
    }

    // Update badge
    function updateBadge(count) {
        if (count > 0) {
            notificationBadge.textContent = count > 99 ? '99+' : count;
            notificationBadge.style.display = 'block';
            notificationBell.classList.add('has-unread');
        } else {
            notificationBadge.style.display = 'none';
            notificationBell.classList.remove('has-unread');
        }
    }

    // Render notifications
    function renderNotifications(notifications) {
        if (!notifications || notifications.length === 0) {
            notificationList.innerHTML = '<div class="notification-empty">Không có thông báo mới</div>';
            return;
        }

        let html = '';
        notifications.forEach(n => {
            const iconInfo = iconMap[n.type] || { icon: 'fa-solid fa-bell', class: '' };
            const unreadClass = n.is_read ? '' : 'unread';
            
            // Determine link
            let href = '/notifications/';
            if (n.booking_id) {
                href = '/booking/history/';
            } else if (n.listing_id) {
                href = `/chitietnoio/${n.listing_id}/`;
            }
            
            html += `
                <a href="${href}" class="notification-item ${unreadClass}" data-id="${n.id}">
                    <div class="notification-icon ${iconInfo.class}">
                        <i class="${iconInfo.icon}"></i>
                    </div>
                    <div class="notification-content">
                        <div class="notification-title">${escapeHtml(n.title)}</div>
                        <div class="notification-message">${escapeHtml(n.message)}</div>
                        <div class="notification-time">${n.created_at}</div>
                    </div>
                </a>
            `;
        });

        notificationList.innerHTML = html;

        // Add click handler to mark as read
        notificationList.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', function() {
                const notifId = this.dataset.id;
                markAsRead(notifId);
            });
        });
    }

    // Mark single notification as read
    async function markAsRead(notifId) {
        try {
            const csrfToken = getCsrfToken();
            await fetch(`/notifications/mark-read/${notifId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
            });
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    // Mark all as read
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                const csrfToken = getCsrfToken();
                await fetch('/notifications/mark-all-read/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                    },
                });
                
                // Update UI
                updateBadge(0);
                notificationList.querySelectorAll('.notification-item.unread').forEach(item => {
                    item.classList.remove('unread');
                });
            } catch (error) {
                console.error('Error marking all as read:', error);
            }
        });
    }

    // Helper: Get CSRF token
    function getCsrfToken() {
        const cookie = document.cookie.split('; ').find(c => c.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    // Helper: Escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Initial load badge count
    async function loadUnreadCount() {
        try {
            const response = await fetch('/notifications/api/');
            const data = await response.json();
            updateBadge(data.unread_count);
        } catch (error) {
            // Silent fail
        }
    }

    // Load unread count on page load
    loadUnreadCount();

    // Refresh every 60 seconds
    setInterval(loadUnreadCount, 60000);
});
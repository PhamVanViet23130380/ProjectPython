// Get room data from URL or Django template context
function getRoomDataFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const roomId = parseInt(urlParams.get('room')) || 1;
    
    // Try to get data from Django template context first (if available)
    const bodyEl = document.querySelector('body[data-listing-id]');
    if (bodyEl) {
        const listingId = bodyEl.getAttribute('data-listing-id');
        const priceEl = document.getElementById('pricePerNight');
        console.log('priceEl:', priceEl);
        console.log('priceEl.textContent:', priceEl ? priceEl.textContent : 'null');
        let priceText = priceEl ? priceEl.textContent : '0';
        // Remove ₫ symbol and parse
        priceText = priceText.replace(/[₫đ,\s]/g, '');
        console.log('priceText after cleanup:', priceText);
        const price = parseFloat(priceText) || 0;
        console.log('Parsed price:', price);
        
        return {
            id: parseInt(listingId) || roomId,
            image: document.getElementById('roomImage')?.src || '/static/app/images/room1.jpg',
            title: document.getElementById('roomTitle')?.textContent || 'Căn hộ',
            rating: parseFloat(document.getElementById('roomRating')?.textContent) || 4.8,
            reviews: parseInt(document.getElementById('roomReviews')?.textContent.match(/\d+/)?.[0]) || 12,
            pricePerNight: price,
            nights: 2,
            location: 'Thành phố Hồ Chí Minh'
        };
    }
    
    // Fallback to default room data if template data not available
    return {
        id: roomId,
        image: '/static/app/images/room1.jpg',
        title: 'Căn hộ tại Quận Tây Hồ',
        rating: 4.8,
        reviews: 12,
        pricePerNight: 2259530,
        nights: 2,
        location: 'Quận Tây Hồ, Hà Nội'
    };
}

// Format currency
function formatCurrency(amount) {
    if (amount === undefined || amount === null || isNaN(amount)) {
        return 'đ0';
    }
    const num = typeof amount === 'string' ? parseFloat(amount) : amount;
    if (isNaN(num)) return 'đ0';
    return 'đ' + num.toLocaleString('vi-VN', { maximumFractionDigits: 0 });
}

// Calculate prices
function calculatePrices(pricePerNight, nights) {
    // Validate inputs
    const price = parseFloat(pricePerNight) || 0;
    const numNights = parseInt(nights) || 0;
    
    const subtotal = price * numNights;
    // Hardcoded service fee (VND) — configurable later
    const serviceFee = 350000;
    // Host protection fee default 0 (hidden when 0)
    const hostFee = 0;
    const total = subtotal + serviceFee + hostFee;
    
    return {
        subtotal,
        serviceFee,
        hostFee,
        total
    };
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    const roomData = getRoomDataFromURL();
    // Initialize from URL params if available
    const params = new URLSearchParams(window.location.search);
    const paramCheckIn = params.get('checkin');
    const paramCheckOut = params.get('checkout');
    const paramGuests = params.get('guests');
    const roomFromParam = parseInt(params.get('room')) || roomData.id;

    // If a room id provided by URL, use room data from template
    let currentRoom = roomData;
    console.log('Current room data:', currentRoom);

    // Helper to parse YYYY-MM-DD into Date
    function parseISODate(s) {
        if (!s) return null;
        const parts = s.split('-').map(p => parseInt(p, 10));
        if (parts.length !== 3 || parts.some(isNaN)) return null;
        return new Date(parts[0], parts[1] - 1, parts[2]);
    }

    // Format date with month name and year
    function formatDateWithYear(date) {
        if (!date) return '';
        const months = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
                       'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'];
        return `${date.getDate()} ${months[date.getMonth()]}, ${date.getFullYear()}`;
    }

    // Determine initial dates
    let checkInDateVal = paramCheckIn || document.getElementById('checkInDate').value || null;
    let checkOutDateVal = paramCheckOut || document.getElementById('checkOutDate').value || null;

    let checkInDateObj = parseISODate(checkInDateVal);
    let checkOutDateObj = parseISODate(checkOutDateVal);

    // If no dates provided, fall back to defaults in roomData (nights) and today
    if (!checkInDateObj || !checkOutDateObj) {
        // Default: tomorrow as check-in and tomorrow + roomData.nights as check-out
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        checkInDateObj = new Date(today);
        checkInDateObj.setDate(checkInDateObj.getDate() + 1); // tomorrow
        checkOutDateObj = new Date(checkInDateObj);
        checkOutDateObj.setDate(checkOutDateObj.getDate() + (roomData.nights || 1));
        // set inputs accordingly
        document.getElementById('checkInDate').value = checkInDateObj.toISOString().slice(0,10);
        document.getElementById('checkOutDate').value = checkOutDateObj.toISOString().slice(0,10);
    } else {
        // Populate inputs from URL
        document.getElementById('checkInDate').value = checkInDateVal;
        document.getElementById('checkOutDate').value = checkOutDateVal;
    }

    // Disable past dates: set min attributes so users cannot pick today or earlier
    const checkInInput = document.getElementById('checkInDate');
    const checkOutInput = document.getElementById('checkOutDate');
    const nowForMin = new Date();
    const todayForMin = new Date(nowForMin.getFullYear(), nowForMin.getMonth(), nowForMin.getDate());
    const tomorrowForMin = new Date(todayForMin);
    tomorrowForMin.setDate(tomorrowForMin.getDate() + 1);
    const toISODate = (d) => d.toISOString().slice(0,10);

    // Enforce check-in min = tomorrow
    checkInInput.min = toISODate(tomorrowForMin);

    // If the URL provided a check-in that's today or earlier, replace with tomorrow
    let currentCheckIn = parseISODate(checkInInput.value);
    if (!currentCheckIn || currentCheckIn <= todayForMin) {
        checkInInput.value = toISODate(tomorrowForMin);
        currentCheckIn = new Date(tomorrowForMin);
    }

    // Set check-out min to check-in + 1
    const minCheckOut = new Date(currentCheckIn);
    minCheckOut.setDate(minCheckOut.getDate() + 1);
    checkOutInput.min = toISODate(minCheckOut);

    // If URL provided check-out is <= check-in, set to minCheckOut
    let currentCheckOut = parseISODate(checkOutInput.value);
    if (!currentCheckOut || currentCheckOut <= currentCheckIn) {
        checkOutInput.value = toISODate(minCheckOut);
    }

    // Keep check-out min in sync when user changes check-in
    checkInInput.addEventListener('change', function() {
        const ci = parseISODate(this.value);
        if (!ci) return;
        // ensure check-in is after today
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        if (ci <= today) {
            // revert to tomorrow
            this.value = toISODate(tomorrowForMin);
            currentCheckIn = new Date(tomorrowForMin);
        } else {
            currentCheckIn = ci;
        }

        const newMinCo = new Date(currentCheckIn);
        newMinCo.setDate(newMinCo.getDate() + 1);
        checkOutInput.min = toISODate(newMinCo);

        const co = parseISODate(checkOutInput.value);
        if (!co || co <= currentCheckIn) {
            checkOutInput.value = toISODate(newMinCo);
        }
    });

    // compute nights correctly across year boundaries
    const nights = Math.max(1, Math.ceil((checkOutDateObj - checkInDateObj) / (1000 * 60 * 60 * 24)));
    const prices = calculatePrices(currentRoom.pricePerNight, nights);
    
    // Update room info
    document.getElementById('roomImage').src = currentRoom.image;
    document.getElementById('roomTitle').textContent = currentRoom.title;
    document.getElementById('roomRating').textContent = currentRoom.rating;
    document.getElementById('roomReviews').textContent = `(${currentRoom.reviews} đánh giá)`;
    
    // Update price details - with null checks
    const pricePerNightEl = document.getElementById('pricePerNight');
    const numNightsEl = document.getElementById('numNights');
    const subtotalEl = document.getElementById('subtotal');
    const serviceFeeEl = document.getElementById('serviceFee');
    const hostFeeEl = document.getElementById('hostFee');
    const totalPriceEl = document.getElementById('totalPrice');
    
    if (pricePerNightEl) pricePerNightEl.textContent = formatCurrency(currentRoom.pricePerNight);
    if (numNightsEl) numNightsEl.textContent = nights;
    if (subtotalEl) subtotalEl.textContent = formatCurrency(prices.subtotal);
    if (serviceFeeEl) serviceFeeEl.textContent = formatCurrency(prices.serviceFee);
    if (hostFeeEl) hostFeeEl.textContent = formatCurrency(prices.hostFee);
    
    // Hide host fee row if zero or element doesn't exist
    if (prices.hostFee === 0 || !hostFeeEl) {
        document.querySelectorAll('.price-row').forEach(row => {
            const label = row.querySelector('.price-label');
            if (label && label.textContent.trim().includes('Phí bảo vệ chủ nhà')) {
                row.style.display = 'none';
            }
        });
    }
    
    if (totalPriceEl) totalPriceEl.textContent = formatCurrency(prices.total);
    
    // Update review section dates and guests - with null checks
    const tripDatesEl = document.getElementById('tripDates');
    const reviewDatesEl = document.getElementById('reviewDates');
    const tripGuestsEl = document.getElementById('tripGuests');
    const reviewGuestsEl = document.getElementById('reviewGuests');
    
    if (tripDatesEl) {
        tripDatesEl.textContent = `${formatDateWithYear(checkInDateObj)} — ${formatDateWithYear(checkOutDateObj)}`;
        if (reviewDatesEl) reviewDatesEl.textContent = tripDatesEl.textContent;
    }
    
    if (paramGuests) {
        if (tripGuestsEl) tripGuestsEl.textContent = paramGuests + ' khách';
        if (reviewGuestsEl) reviewGuestsEl.textContent = paramGuests + ' khách';
    } else {
        if (tripGuestsEl && reviewGuestsEl) {
            reviewGuestsEl.textContent = tripGuestsEl.textContent;
        }
    }
    
    // Collapsible sections
    const sectionHeaders = document.querySelectorAll('.section-header[data-toggle="collapse"]');
    sectionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const section = this.closest('.collapsible-section');
            const content = section.querySelector('.section-content');
            const isExpanded = this.classList.contains('expanded');
            
            if (isExpanded) {
                // Collapse
                this.classList.remove('expanded');
                content.classList.remove('expanded');
                content.classList.add('collapsed');
            } else {
                // Expand
                this.classList.add('expanded');
                content.classList.remove('collapsed');
                content.classList.add('expanded');
            }
        });
    });
    
    // Card number formatting
    const cardNumberInput = document.getElementById('cardNumber');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            e.target.value = formattedValue;
        });
    }
    
    // Expiry date formatting
    const expiryDateInput = document.getElementById('expiryDate');
    if (expiryDateInput) {
        expiryDateInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }
    
    // CVV validation (numbers only)
    const cvvInput = document.getElementById('cvv');
    if (cvvInput) {
        cvvInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '');
        });
    }

    
    // Modal functionality
    const dateModal = document.getElementById('dateModal');
    const guestsModal = document.getElementById('guestsModal');
    const editDatesBtn = document.getElementById('editDatesBtn');
    const editGuestsBtn = document.getElementById('editGuestsBtn');
    
    console.log('Datphong.js loaded - editDatesBtn:', editDatesBtn);
    
    // Date Modal
    function openDateModal() {
        console.log('Opening date modal');
        if (dateModal) {
            dateModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }
    
    function closeDateModal() {
        console.log('Closing date modal');
        if (dateModal) {
            dateModal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    }
    
    function saveDates() {
        const checkIn = document.getElementById('checkInDate').value;
        const checkOut = document.getElementById('checkOutDate').value;
        
        // helper to show inline date validation messages
        function showDateError(msg) {
            let err = document.getElementById('dateErrorMsg');
            if (!err) {
                err = document.createElement('div');
                err.id = 'dateErrorMsg';
                err.style.color = '#b00020';
                err.style.marginTop = '8px';
                err.style.fontSize = '0.95rem';
                err.style.textAlign = 'left';
                // insert before modal footer if possible
                const footer = dateModal.querySelector('.modal-footer');
                if (footer && footer.parentNode) footer.parentNode.insertBefore(err, footer);
                else dateModal.appendChild(err);
            }
            err.textContent = msg;
        }

        function clearDateError() {
            const err = document.getElementById('dateErrorMsg');
            if (err) err.textContent = '';
        }

        // clear previous errors on input changes
        document.getElementById('checkInDate').addEventListener('input', clearDateError);
        document.getElementById('checkOutDate').addEventListener('input', clearDateError);

        if (checkIn && checkOut) {
            const checkInDate = parseISODate(checkIn);
            const checkOutDate = parseISODate(checkOut);
            
            // Ensure check-in is after today
            const now = new Date();
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            if (checkInDate <= today) {
                showDateError('Ngày nhận phòng phải sau ngày hôm nay. Vui lòng chọn ngày khác.');
                return;
            }

            // Ensure check-out is after check-in
            if (checkOutDate <= checkInDate) {
                showDateError('Ngày trả phòng phải sau ngày nhận phòng.');
                return;
            }
            
            const formattedCheckIn = formatDateWithYear(checkInDate);
            const formattedCheckOut = formatDateWithYear(checkOutDate);
            const dateText = `${formattedCheckIn} — ${formattedCheckOut}`;

            const tripDatesEl = document.getElementById('tripDates');
            if (tripDatesEl) tripDatesEl.textContent = dateText;
            
            const reviewDatesEl = document.getElementById('reviewDates');
            if (reviewDatesEl) reviewDatesEl.textContent = dateText;

            // Calculate nights correctly across years
            const nights = Math.max(1, Math.ceil((checkOutDate - checkInDate) / (1000 * 60 * 60 * 24)));
            const prices = calculatePrices(currentRoom.pricePerNight, nights);

            // Update price details
            const numNightsEl = document.getElementById('numNights');
            if (numNightsEl) numNightsEl.textContent = nights;
            
            const subtotalEl = document.getElementById('subtotal');
            if (subtotalEl) subtotalEl.textContent = formatCurrency(prices.subtotal);
            
            const serviceFeeEl = document.getElementById('serviceFee');
            if (serviceFeeEl) serviceFeeEl.textContent = formatCurrency(prices.serviceFee);
            
            const hostFeeEl = document.getElementById('hostFee');
            if (hostFeeEl) hostFeeEl.textContent = formatCurrency(prices.hostFee);
            
            const totalPriceEl = document.getElementById('totalPrice');
            if (totalPriceEl) totalPriceEl.textContent = formatCurrency(prices.total);

            // Hide host fee row if zero
            if (prices.hostFee === 0) {
                document.querySelectorAll('.price-row').forEach(row => {
                    const label = row.querySelector('.price-label');
                    if (label && label.textContent.trim().includes('Phí bảo vệ chủ nhà')) {
                        row.style.display = 'none';
                    }
                });
            }

            // Update URL params so changes persist when sharing/refreshing
            const newParams = new URLSearchParams(window.location.search);
            newParams.set('checkin', checkIn);
            newParams.set('checkout', checkOut);
            // keep room param if present
            if (roomFromParam) newParams.set('room', roomFromParam);
            if (paramGuests) newParams.set('guests', paramGuests);
            const newUrl = window.location.pathname + '?' + newParams.toString();
            window.history.replaceState({}, '', newUrl);

            closeDateModal();
        } else {
            showDateError('Vui lòng chọn cả ngày nhận và trả phòng.');
        }
    }
    
    function clearDates() {
        document.getElementById('checkInDate').value = '';
        document.getElementById('checkOutDate').value = '';
    }

    // Expose modal functions to global scope so inline `onclick` in templates work
    window.openDateModal = openDateModal;
    window.closeDateModal = closeDateModal;
    window.saveDates = saveDates;
    window.clearDates = clearDates;
    // Expose guest modal functions too
    window.openGuestsModal = openGuestsModal;
    window.closeGuestsModal = closeGuestsModal;
    window.saveGuests = saveGuests;
    window.incrementGuests = incrementGuests;
    window.decrementGuests = decrementGuests;
    window.updateGuestCounters = updateGuestCounters;
    
    function formatDate(date) {
        const months = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
                       'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'];
        return `${date.getDate()} ${months[date.getMonth()]}`;
    }
    
    // Guests Modal
    let guestCounts = {
        adults: 1,
        children: 0,
        infants: 0,
        pets: 0
    };
    
    function openGuestsModal() {
        guestsModal.classList.add('active');
        document.body.style.overflow = 'hidden';
        updateGuestCounters();
    }
    
    function closeGuestsModal() {
        guestsModal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
    
    function incrementGuests(type) {
        if (type === 'adults' && guestCounts[type] < 16) {
            guestCounts[type]++;
        } else if (type === 'children' && guestCounts[type] < 5) {
            guestCounts[type]++;
        } else if (type === 'infants' && guestCounts[type] < 5) {
            guestCounts[type]++;
        } else if (type === 'pets' && guestCounts[type] < 5) {
            guestCounts[type]++;
        }
        updateGuestCounters();
    }
    
    function decrementGuests(type) {
        if (type === 'adults' && guestCounts[type] > 1) {
            guestCounts[type]--;
        } else if (guestCounts[type] > 0) {
            guestCounts[type]--;
        }
        updateGuestCounters();
    }
    
    function updateGuestCounters() {
        const safeSetText = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };
        safeSetText('adultsCount', guestCounts.adults);
        safeSetText('childrenCount', guestCounts.children);
        safeSetText('infantsCount', guestCounts.infants);
        safeSetText('petsCount', guestCounts.pets);

        // Helper to find increment/decrement buttons using several fallback selectors
        function findBtn(type, action) {
            // try data- attributes first
            let sel = `[data-type="${type}"][data-action="${action}"]`;
            let btn = document.querySelector(sel);
            if (btn) return btn;
            // try inline onclick attribute exact match
            const onclickExact = action === 'decrement'
                ? `decrementGuests('${type}')`
                : `incrementGuests('${type}')`;
            btn = document.querySelector(`[onclick="${onclickExact}"]`);
            if (btn) return btn;
            // try contains (lenient)
            btn = Array.from(document.querySelectorAll('.counter-btn')).find(b => {
                const o = b.getAttribute('onclick') || '';
                return o.indexOf(type) !== -1 && o.indexOf(action === 'decrement' ? 'decrement' : 'increment') !== -1;
            });
            return btn || null;
        }

        const buttons = [
            {t: 'adults', minDisabled: guestCounts.adults <= 1, maxDisabled: guestCounts.adults >= 16},
            {t: 'children', minDisabled: guestCounts.children <= 0, maxDisabled: guestCounts.children >= 5},
            {t: 'infants', minDisabled: guestCounts.infants <= 0, maxDisabled: guestCounts.infants >= 5},
            {t: 'pets', minDisabled: guestCounts.pets <= 0, maxDisabled: guestCounts.pets >= 5},
        ];

        buttons.forEach(b => {
            const dec = findBtn(b.t, 'decrement');
            const inc = findBtn(b.t, 'increment');
            if (dec) dec.disabled = !!b.minDisabled;
            if (inc) inc.disabled = !!b.maxDisabled;
        });
    }
    
    function saveGuests() {
        const totalGuests = guestCounts.adults + guestCounts.children;
        const parts = [];

        if (totalGuests > 0) {
            parts.push(`${totalGuests} khách`);
        }
        if (guestCounts.infants > 0) {
            parts.push(`${guestCounts.infants} trẻ sơ sinh`);
        }
        if (guestCounts.pets > 0) {
            parts.push(`${guestCounts.pets} thú cưng`);
        }

        const guestText = parts.join(', ');
        const tripEl = document.getElementById('tripGuests');
        const reviewEl = document.getElementById('reviewGuests');
        if (tripEl) tripEl.textContent = guestText;
        if (reviewEl) reviewEl.textContent = guestText;

        // Persist guests in URL so selection survives reload/share
        const newParams = new URLSearchParams(window.location.search);
        newParams.set('guests', String(totalGuests));
        const newUrl = window.location.pathname + '?' + newParams.toString();
        window.history.replaceState({}, '', newUrl);

        closeGuestsModal();
    }
    
    // Event listeners for modals (attach only if elements exist)
    if (editDatesBtn) {
        console.log('Adding click listener to editDatesBtn');
        editDatesBtn.addEventListener('click', openDateModal);
    }
    if (editGuestsBtn) editGuestsBtn.addEventListener('click', openGuestsModal);
    
    // Close modals on overlay click
    if (dateModal) {
        dateModal.addEventListener('click', function(e) {
            if (e.target === dateModal) {
                closeDateModal();
            }
        });
    }
    
    if (guestsModal) {
        guestsModal.addEventListener('click', function(e) {
            if (e.target === guestsModal) {
                closeGuestsModal();
            }
        });
    }
    
    // Close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal-overlay');
            if (modal === dateModal) {
                closeDateModal();
            } else if (modal === guestsModal) {
                closeGuestsModal();
            }
        });
    });
    
    // Save buttons (attach only if present)
    const saveDatesBtnEl = document.getElementById('saveDatesBtn');
    if (saveDatesBtnEl) saveDatesBtnEl.addEventListener('click', saveDates);
    const saveGuestsBtnEl = document.getElementById('saveGuestsBtn');
    if (saveGuestsBtnEl) saveGuestsBtnEl.addEventListener('click', saveGuests);

    // Clear dates button
    const clearDatesBtnEl = document.getElementById('clearDatesBtn');
    if (clearDatesBtnEl) clearDatesBtnEl.addEventListener('click', clearDates);

    // Cancel guests button
    const cancelGuestsBtnEl = document.getElementById('cancelGuestsBtn');
    if (cancelGuestsBtnEl) cancelGuestsBtnEl.addEventListener('click', closeGuestsModal);
    
    // Guest counter buttons
    document.querySelectorAll('.counter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.getAttribute('data-type');
            const action = this.getAttribute('data-action');
            
            if (action === 'increment') {
                incrementGuests(type);
            } else if (action === 'decrement') {
                decrementGuests(type);
            }
        });
    });
    
    // Submit booking with inline validation
    const submitBtn = document.getElementById('submitBooking');
    const paymentForm = document.getElementById('paymentForm');

    function showFieldError(fieldEl, msg) {
        if (!fieldEl) return;
        let err = fieldEl.nextElementSibling;
        if (!err || !err.classList || !err.classList.contains('field-error')) {
            err = document.createElement('div');
            err.className = 'field-error';
            err.style.color = '#b00020';
            err.style.fontSize = '0.9rem';
            err.style.marginTop = '6px';
            fieldEl.parentNode.insertBefore(err, fieldEl.nextSibling);
        }
        err.textContent = msg;
    }

    function clearFieldError(fieldEl) {
        if (!fieldEl) return;
        const err = fieldEl.nextElementSibling;
        if (err && err.classList && err.classList.contains('field-error')) err.textContent = '';
    }

    function clearAllPaymentErrors() {
        ['cardNumber','expiryDate','cvv','postalCode'].forEach(id => {
            const el = document.getElementById(id);
            if (el) clearFieldError(el);
        });
    }

    // Form-level error (display below submit button)
    function showFormError(msg) {
        let formErr = document.getElementById('paymentFormError');
        if (!formErr) {
            formErr = document.createElement('div');
            formErr.id = 'paymentFormError';
            formErr.style.color = '#b00020';
            formErr.style.marginTop = '12px';
            formErr.style.fontSize = '1rem';
            const submit = document.getElementById('submitBooking');
            if (submit && submit.parentNode) submit.parentNode.insertBefore(formErr, submit.nextSibling);
            else if (paymentForm) paymentForm.appendChild(formErr);
            else document.body.appendChild(formErr);
        }
        formErr.textContent = msg;
    }

    function clearFormError() {
        const formErr = document.getElementById('paymentFormError');
        if (formErr) formErr.textContent = '';
    }

    if (submitBtn) submitBtn.addEventListener('click', function(ev) {
        ev.preventDefault();
        clearAllPaymentErrors();
        clearFormError();

        const paymentTypeEl = document.querySelector('input[name="payment_type"]:checked');
        const paymentType = paymentTypeEl ? paymentTypeEl.value : 'card';

        // Basic HTML5 validity first
        if (paymentForm && paymentType === 'card' && !paymentForm.checkValidity()) {
            paymentForm.reportValidity();
            return;
        }

        let valid = true;

        if (paymentType === 'card') {
            const cardNumberEl = document.getElementById('cardNumber');
            const expiryEl = document.getElementById('expiryDate');
            const cvvEl = document.getElementById('cvv');
            const postalEl = document.getElementById('postalCode');

            const cardNumber = cardNumberEl ? cardNumberEl.value.replace(/\s/g, '') : '';
            const expiry = expiryEl ? expiryEl.value.trim() : '';
            const cvv = cvvEl ? cvvEl.value.trim() : '';
            const postal = postalEl ? postalEl.value.trim() : '';

            // Card number: exactly 16 digits
            if (!/^\d{16}$/.test(cardNumber)) {
                showFieldError(cardNumberEl, 'So the phai la 16 chu so.');
                if (valid) cardNumberEl.focus();
                valid = false;
            }

            // Expiry: MM/YY or MM/YYYY, must be later than current month
            if (!expiry) {
                showFieldError(expiryEl, 'Vui long nhap ngay het han (MM/YY).');
                if (valid) expiryEl.focus();
                valid = false;
            } else {
                const parts = expiry.split('/').map(p => p.trim());
                if (parts.length != 2) {
                    showFieldError(expiryEl, 'Dinh dang phai la MM/YY.');
                    if (valid) expiryEl.focus();
                    valid = false;
                } else {
                    const mm = parseInt(parts[0], 10);
                    let yy = parseInt(parts[1], 10);
                    if (isNaN(mm) || mm < 1 || mm > 12 || isNaN(yy)) {
                        showFieldError(expiryEl, 'Thang hoac nam khong hop le.');
                        if (valid) expiryEl.focus();
                        valid = false;
                    } else {
                        if (yy < 100) yy += 2000;
                        const expiryDate = new Date(yy, mm, 0, 23, 59, 59, 999);
                        const today = new Date();
                        const todayDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
                        if (expiryDate <= todayDate) {
                            showFieldError(expiryEl, 'The da het han.');
                            if (valid) expiryEl.focus();
                            valid = false;
                        }
                    }
                }
            }

            // CVV: exactly 3 digits
            if (!/^\d{3}$/.test(cvv)) {
                showFieldError(cvvEl, 'CVV phai gom 3 chu so.');
                if (valid) cvvEl.focus();
                valid = false;
            }

            // Postal code: required (non-empty)
            if (!postal) {
                showFieldError(postalEl, 'Ma buu chinh khong duoc de trong.');
                if (valid) postalEl.focus();
                valid = false;
            }
        }

        if (!valid) {
            showFormError('Vui long sua cac truong mau do phia tren truoc khi tiep tuc.');
            return;
        }

        // All validations passed ? create booking first (with pending status)
        // Then show confirmation modal
        
        // disable submit to prevent double clicks
        submitBtn.disabled = true;
        submitBtn.textContent = 'Dang xu ly...';

        // helper to get CSRF token from cookie
        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
            return null;
        }

        const checkin = document.getElementById('checkInDate').value;
        const checkout = document.getElementById('checkOutDate').value;
        const guestsVal = new URLSearchParams(window.location.search).get('guests') || '1';
        const listingId = (new URLSearchParams(window.location.search).get('room')) || currentRoom.id;
        const noteText = document.getElementById('hostMessage')?.value || '';

        const postUrl = `/booking/create/${listingId}/`;
        const formBody = new URLSearchParams();
        formBody.set('checkin', checkin);
        formBody.set('checkout', checkout);
        formBody.set('guests', guestsVal);
        formBody.set('note', noteText);
        
        const csrfToken = getCookie('csrftoken');

        fetch(postUrl, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            credentials: 'same-origin',
            body: formBody.toString()
        }).then(resp => {
            if (resp.status === 302 || resp.status === 401 || resp.redirected) {
                if (window.__loginUrl) {
                    window.location.href = window.__loginUrl + '?next=' + encodeURIComponent(window.location.pathname + window.location.search);
                } else {
                    window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname + window.location.search);
                }
                return Promise.reject({skipErrorHandling: true});
            }
            
            return resp.json().then(data => {
                return { ok: resp.ok, status: resp.status, data: data };
            });
        }).then(result => {
            if (!result.ok) {
                const errorMsg = result.data.error || 'Loi server khi tao booking.';
                throw { error: errorMsg };
            }
            
            const data = result.data;
            if (data && data.booking_id) {
                window.__pendingBookingId = data.booking_id;
            }

            const confirmModal = document.getElementById('confirmBookingModal');
            const confirmRoomTitleText = document.getElementById('confirmRoomTitleText');
            const confirmDates = document.getElementById('confirmDates');
            const confirmGuests = document.getElementById('confirmGuests');
            const confirmSubtotal = document.getElementById('confirmSubtotal');
            const confirmServiceFee = document.getElementById('confirmServiceFee');
            const confirmTotalPrice = document.getElementById('confirmTotalPrice');
            const confirmRoomImage = document.getElementById('confirmRoomImage');

            if (confirmRoomTitleText) confirmRoomTitleText.textContent = currentRoom.title || '';
            if (confirmDates) confirmDates.textContent = document.getElementById('tripDates').textContent || '';
            if (confirmGuests) confirmGuests.textContent = document.getElementById('reviewGuests').textContent || '';
            if (confirmSubtotal) confirmSubtotal.textContent = document.getElementById('subtotal').textContent || '';
            if (confirmServiceFee) confirmServiceFee.textContent = document.getElementById('serviceFee').textContent || '';
            if (confirmTotalPrice) confirmTotalPrice.textContent = document.getElementById('totalPrice').textContent || '';
            if (confirmRoomImage) confirmRoomImage.src = document.getElementById('roomImage').src || '';

            if (confirmModal) {
                confirmModal.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }
            
            submitBtn.disabled = false;
            submitBtn.textContent = 'Xac nhan va thanh toan';
        }).catch(err => {
            if (err && err.skipErrorHandling) {
                return;
            }
            const msg = (err && err.error) ? err.error : 'Loi khi tao booking. Vui long thu lai.';
            showFormError(msg);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Xac nhan va thanh toan';
        });
    });

// Attach handler on confirm button (idempotent) - moved outside
        const confirmBtn = document.getElementById('confirmPayBtn');
        const cancelBtn = document.getElementById('cancelPayBtn');
        const closeBtn = document.getElementById('confirmModalClose');

        function closeConfirm() {
            const confirmModal = document.getElementById('confirmBookingModal');
            if (confirmModal) { confirmModal.style.display = 'none'; document.body.style.overflow = 'auto'; }
        }

        if (cancelBtn) cancelBtn.onclick = closeConfirm;
        if (closeBtn) closeBtn.onclick = closeConfirm;

        if (confirmBtn) {
            confirmBtn.onclick = function() {
                // disable submit to prevent double clicks
                confirmBtn.disabled = true;
                confirmBtn.textContent = 'Dang xu ly...';

                // helper to get CSRF token from cookie
                function getCookie(name) {
                    const value = `; ${document.cookie}`;
                    const parts = value.split(`; ${name}=`);
                    if (parts.length === 2) return parts.pop().split(';').shift();
                    return null;
                }

                const csrfToken = getCookie('csrftoken');

                // Gather form data to create booking and pay in one step
                const checkin = document.getElementById('checkInDate').value;
                const checkout = document.getElementById('checkOutDate').value;
                const guestsVal = new URLSearchParams(window.location.search).get('guests') || '1';
                const listingId = (new URLSearchParams(window.location.search).get('room')) || 1;
                const noteText = document.getElementById('hostMessage')?.value || '';

                const paymentTypeEl = document.querySelector('input[name="payment_type"]:checked');
                const paymentType = paymentTypeEl ? paymentTypeEl.value : 'card';
                const pendingBookingId = window.__pendingBookingId;

                if (paymentType === 'vnpay') {
                    if (!pendingBookingId) {
                        const errEl = document.getElementById('confirmErrorMsg');
                        if (errEl) {
                            errEl.style.display = 'block';
                            errEl.textContent = 'Missing pending booking. Please try again.';
                        }
                        confirmBtn.disabled = false;
                        confirmBtn.textContent = 'Thanh toan';
                        return;
                    }

                    const vnpUrl = `/payment/vnpay/create/${pendingBookingId}/`;
                    fetch(vnpUrl, {
                        method: 'GET',
                        headers: { 'X-Requested-With': 'XMLHttpRequest' },
                        credentials: 'same-origin',
                    }).then(resp => resp.json())
                    .then(data => {
                        if (data.error) throw new Error(data.error);
                        if (data.payment_url) {
                            window.location.href = data.payment_url;
                        } else {
                            window.location.href = '/';
                        }
                    }).catch(err => {
                        const errEl = document.getElementById('confirmErrorMsg');
                        if (errEl) {
                            errEl.style.display = 'block';
                            errEl.textContent = (err && err.message) ? err.message : 'Payment error.';
                        }
                        confirmBtn.disabled = false;
                        confirmBtn.textContent = 'Thanh toan';
                    });

                    return;
                }

                const paymentUrl = `/payment/create-and-pay/${listingId}/`;
                const body = new URLSearchParams();
                body.set('checkin', checkin);
                body.set('checkout', checkout);
                body.set('guests', guestsVal);
                body.set('note', noteText);

                fetch(paymentUrl, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                    },
                    credentials: 'same-origin',
                    body: body.toString()
                }).then(resp => resp.json())
                .then(data => {
                    if (data.error) throw new Error(data.error);
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    } else {
                        window.location.href = '/';
                    }
                }).catch(err => {
                    console.error('Payment error:', err);
                    const errEl = document.getElementById('confirmErrorMsg');
                    if (errEl) { 
                        errEl.style.display = 'block'; 
                        errEl.textContent = (err && err.message) ? err.message : 'Loi khi thanh toan. Vui long thu lai.';
                    }
                    confirmBtn.disabled = false;
                    confirmBtn.textContent = 'Thanh toan';
                });
            };
        }

// Policy link
    const policyLink = document.querySelector('.policy-link');
    if (policyLink) {
        policyLink.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Chính sách hủy:\n\n' +
                  '- Hủy miễn phí trước 7 ngày: Hoàn tiền 100%\n' +
                  '- Hủy trước 3-7 ngày: Hoàn tiền 50%\n' +
                  '- Hủy trong vòng 3 ngày: Không hoàn tiền');
        });
    }

    // Terms links
    const termsLinks = document.querySelectorAll('.terms-text a');
    if (termsLinks && termsLinks.length) {
        termsLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const text = this.textContent;
                alert(`Trang ${text} đang được phát triển`);
            });
        });
    }
    
    // Add animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe booking sections
    document.querySelectorAll('.booking-section').forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'all 0.5s ease';
        observer.observe(section);
    });
});

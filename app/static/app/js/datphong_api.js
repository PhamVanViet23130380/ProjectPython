// Datphong API - Kết nối với backend để tính giá động
(function() {
    'use strict';

    // Lấy listing_id từ template Django
    const urlParams = new URLSearchParams(window.location.search);
    const listingId = urlParams.get('room') || urlParams.get('listing') || document.querySelector('[data-listing-id]')?.dataset.listingId;

    // State
    let checkInDate = null;
    let checkOutDate = null;
    let guestCounts = {
        adults: 1,
        children: 0,
        infants: 0,
        pets: 0
    };

    // Format tiền VND
    function formatVND(amount) {
        if (!amount) return '₫0';
        const num = parseFloat(amount);
        return '₫' + num.toLocaleString('vi-VN', { maximumFractionDigits: 0 });
    }

    // Tính tổng số khách
    function getTotalGuests() {
        return guestCounts.adults + guestCounts.children;
    }

    // Gọi API để tính giá
    function calculatePrice() {
        if (!listingId || !checkInDate || !checkOutDate) {
            console.log('Missing data:', { listingId, checkInDate, checkOutDate });
            return;
        }

        const url = `/api/price/?listing=${listingId}&checkin=${checkInDate}&checkout=${checkOutDate}&guests=${getTotalGuests()}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('API Error:', data.error);
                    return;
                }

                // Cập nhật UI
                updatePriceDisplay(data);
            })
            .catch(error => {
                console.error('Fetch error:', error);
            });
    }

    // Cập nhật hiển thị giá
    function updatePriceDisplay(priceData) {
        const {
            nights,
            base,
            service_fee,
            total
        } = priceData;

        document.getElementById('numNights').textContent = nights;
        document.getElementById('subtotal').textContent = formatVND(base);
        document.getElementById('serviceFee').textContent = formatVND(service_fee);
        document.getElementById('totalPrice').textContent = formatVND(total);

        const confirmSubtotal = document.getElementById('confirmSubtotal');
        const confirmServiceFee = document.getElementById('confirmServiceFee');
        const confirmTotalPrice = document.getElementById('confirmTotalPrice');

        if (confirmSubtotal) confirmSubtotal.textContent = formatVND(base);
        if (confirmServiceFee) confirmServiceFee.textContent = formatVND(service_fee);
        if (confirmTotalPrice) confirmTotalPrice.textContent = formatVND(total);
    }
// Lấy ngày từ URL params
    function getInitialDates() {
        const checkin = urlParams.get('checkin');
        const checkout = urlParams.get('checkout');
        
        if (checkin) {
            checkInDate = checkin;
            const checkInInput = document.getElementById('checkInDate');
            if (checkInInput) checkInInput.value = checkin;
        } else {
            // Mặc định: hôm nay + 1
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            checkInDate = tomorrow.toISOString().split('T')[0];
        }

        if (checkout) {
            checkOutDate = checkout;
            const checkOutInput = document.getElementById('checkOutDate');
            if (checkOutInput) checkOutInput.value = checkout;
        } else {
            // Mặc định: hôm nay + 3
            const dayAfter = new Date();
            dayAfter.setDate(dayAfter.getDate() + 3);
            checkOutDate = dayAfter.toISOString().split('T')[0];
        }

        updateTripDatesDisplay();
    }

    // Cập nhật hiển thị ngày
    function updateTripDatesDisplay() {
        if (!checkInDate || !checkOutDate) return;

        const checkIn = new Date(checkInDate);
        const checkOut = new Date(checkOutDate);
        
        const options = { day: 'numeric', month: 'long', year: 'numeric' };
        const checkInStr = checkIn.toLocaleDateString('vi-VN', options);
        const checkOutStr = checkOut.toLocaleDateString('vi-VN', options);

        const tripDatesEl = document.getElementById('tripDates');
        if (tripDatesEl) {
            tripDatesEl.textContent = `${checkInStr} — ${checkOutStr}`;
        }
    }

    // Cập nhật hiển thị số khách
    function updateGuestsDisplay() {
        const { adults, children, infants, pets } = guestCounts;
        const tripGuestsEl = document.getElementById('tripGuests');
        
        if (!tripGuestsEl) return;

        let guestText = [];
        if (adults > 0) guestText.push(`${adults} người lớn`);
        if (children > 0) guestText.push(`${children} trẻ em`);
        if (infants > 0) guestText.push(`${infants} em bé`);
        if (pets > 0) guestText.push(`${pets} thú cưng`);

        tripGuestsEl.textContent = guestText.join(', ');

        // Cập nhật counters
        document.getElementById('adultsCount').textContent = adults;
        document.getElementById('childrenCount').textContent = children;
        document.getElementById('infantsCount').textContent = infants;
        document.getElementById('petsCount').textContent = pets;
    }

    // Expose global functions for existing datphong.js
    window.DatphongAPI = {
        setCheckIn: function(date) {
            checkInDate = date;
            updateTripDatesDisplay();
            calculatePrice();
        },
        setCheckOut: function(date) {
            checkOutDate = date;
            updateTripDatesDisplay();
            calculatePrice();
        },
        setGuests: function(type, count) {
            guestCounts[type] = parseInt(count) || 0;
            updateGuestsDisplay();
            calculatePrice();
        },
        recalculate: calculatePrice,
        getState: function() {
            return {
                listingId,
                checkInDate,
                checkOutDate,
                guestCounts
            };
        }
    };

    // Initialize khi DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DatphongAPI initializing...');
        getInitialDates();
        updateGuestsDisplay();
        
        // Tính giá lần đầu
        setTimeout(calculatePrice, 100);

        // Lắng nghe sự kiện thay đổi ngày
        const checkInInput = document.getElementById('checkInDate');
        const checkOutInput = document.getElementById('checkOutDate');

        if (checkInInput) {
            checkInInput.addEventListener('change', function() {
                checkInDate = this.value;
                updateTripDatesDisplay();
                calculatePrice();
            });
        }

        if (checkOutInput) {
            checkOutInput.addEventListener('change', function() {
                checkOutDate = this.value;
                updateTripDatesDisplay();
                calculatePrice();
            });
        }
        
        console.log('DatphongAPI initialized with listing:', listingId);
    });
})();

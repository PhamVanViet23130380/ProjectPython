// Get room data from URL
function getRoomDataFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const roomId = parseInt(urlParams.get('room')) || 1;
    
    // Try to get room from rooms array (loaded from chitietnoio-data.js)
    if (typeof rooms !== 'undefined' && rooms.length > 0) {
        const room = rooms.find(r => r.id === roomId);
        if (room) {
            return {
                id: room.id,
                image: room.image,
                title: room.title,
                rating: room.rating,
                reviews: room.reviews,
                pricePerNight: room.price,
                nights: 2,
                location: room.location
            };
        }
    }
    
    // Fallback to default room data if rooms array not loaded
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
    return 'đ' + amount.toLocaleString('vi-VN');
}

// Calculate prices
function calculatePrices(pricePerNight, nights) {
    const subtotal = pricePerNight * nights;
    const serviceFee = Math.round(subtotal * 0.32); // 32% service fee
    const hostFee = Math.round(subtotal * 0.08); // 8% host protection fee
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
    const prices = calculatePrices(roomData.pricePerNight, roomData.nights);
    
    // Update room info
    document.getElementById('roomImage').src = roomData.image;
    document.getElementById('roomTitle').textContent = roomData.title;
    document.getElementById('roomRating').textContent = roomData.rating;
    document.getElementById('roomReviews').textContent = `(${roomData.reviews} đánh giá)`;
    
    // Update price details
    document.getElementById('pricePerNight').textContent = formatCurrency(roomData.pricePerNight);
    document.getElementById('numNights').textContent = roomData.nights;
    document.getElementById('subtotal').textContent = formatCurrency(prices.subtotal);
    document.getElementById('serviceFee').textContent = formatCurrency(prices.serviceFee);
    document.getElementById('hostFee').textContent = formatCurrency(prices.hostFee);
    document.getElementById('totalPrice').textContent = formatCurrency(prices.total);
    
    // Update review section dates
    document.getElementById('reviewDates').textContent = document.getElementById('tripDates').textContent;
    document.getElementById('reviewGuests').textContent = document.getElementById('tripGuests').textContent;
    
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
    cardNumberInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\s/g, '');
        let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
        e.target.value = formattedValue;
    });
    
    // Expiry date formatting
    const expiryDateInput = document.getElementById('expiryDate');
    expiryDateInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 2) {
            value = value.substring(0, 2) + '/' + value.substring(2, 4);
        }
        e.target.value = value;
    });
    
    // CVV validation (numbers only)
    const cvvInput = document.getElementById('cvv');
    cvvInput.addEventListener('input', function(e) {
        e.target.value = e.target.value.replace(/\D/g, '');
    });
    
    // Modal functionality
    const dateModal = document.getElementById('dateModal');
    const guestsModal = document.getElementById('guestsModal');
    const editDatesBtn = document.getElementById('editDatesBtn');
    const editGuestsBtn = document.getElementById('editGuestsBtn');
    
    // Date Modal
    function openDateModal() {
        dateModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    function closeDateModal() {
        dateModal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
    
    function saveDates() {
        const checkIn = document.getElementById('checkInDate').value;
        const checkOut = document.getElementById('checkOutDate').value;
        
        if (checkIn && checkOut) {
            const checkInDate = new Date(checkIn);
            const checkOutDate = new Date(checkOut);
            
            if (checkOutDate <= checkInDate) {
                alert('Ngày trả phòng phải sau ngày nhận phòng!');
                return;
            }
            
            const formattedCheckIn = formatDate(checkInDate);
            const formattedCheckOut = formatDate(checkOutDate);
            const dateText = `${formattedCheckIn} - ${formattedCheckOut}`;
            
            document.getElementById('tripDates').textContent = dateText;
            document.getElementById('reviewDates').textContent = dateText;
            
            // Calculate nights
            const nights = Math.ceil((checkOutDate - checkInDate) / (1000 * 60 * 60 * 24));
            const prices = calculatePrices(roomData.pricePerNight, nights);
            
            // Update price details
            document.getElementById('numNights').textContent = nights;
            document.getElementById('subtotal').textContent = formatCurrency(prices.subtotal);
            document.getElementById('serviceFee').textContent = formatCurrency(prices.serviceFee);
            document.getElementById('hostFee').textContent = formatCurrency(prices.hostFee);
            document.getElementById('totalPrice').textContent = formatCurrency(prices.total);
            
            closeDateModal();
        } else {
            alert('Vui lòng chọn cả ngày nhận và trả phòng!');
        }
    }
    
    function clearDates() {
        document.getElementById('checkInDate').value = '';
        document.getElementById('checkOutDate').value = '';
    }
    
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
        document.getElementById('adultsCount').textContent = guestCounts.adults;
        document.getElementById('childrenCount').textContent = guestCounts.children;
        document.getElementById('infantsCount').textContent = guestCounts.infants;
        document.getElementById('petsCount').textContent = guestCounts.pets;
        
        // Update button states
        document.querySelector('[data-type="adults"][data-action="decrement"]').disabled = guestCounts.adults <= 1;
        document.querySelector('[data-type="children"][data-action="decrement"]').disabled = guestCounts.children <= 0;
        document.querySelector('[data-type="infants"][data-action="decrement"]').disabled = guestCounts.infants <= 0;
        document.querySelector('[data-type="pets"][data-action="decrement"]').disabled = guestCounts.pets <= 0;
        
        document.querySelector('[data-type="adults"][data-action="increment"]').disabled = guestCounts.adults >= 16;
        document.querySelector('[data-type="children"][data-action="increment"]').disabled = guestCounts.children >= 5;
        document.querySelector('[data-type="infants"][data-action="increment"]').disabled = guestCounts.infants >= 5;
        document.querySelector('[data-type="pets"][data-action="increment"]').disabled = guestCounts.pets >= 5;
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
        document.getElementById('tripGuests').textContent = guestText;
        document.getElementById('reviewGuests').textContent = guestText;
        
        closeGuestsModal();
    }
    
    // Event listeners for modals
    editDatesBtn.addEventListener('click', openDateModal);
    editGuestsBtn.addEventListener('click', openGuestsModal);
    
    // Close modals on overlay click
    dateModal.addEventListener('click', function(e) {
        if (e.target === dateModal) {
            closeDateModal();
        }
    });
    
    guestsModal.addEventListener('click', function(e) {
        if (e.target === guestsModal) {
            closeGuestsModal();
        }
    });
    
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
    
    // Save buttons
    document.getElementById('saveDatesBtn').addEventListener('click', saveDates);
    document.getElementById('saveGuestsBtn').addEventListener('click', saveGuests);
    
    // Clear dates button
    document.getElementById('clearDatesBtn').addEventListener('click', clearDates);
    
    // Cancel guests button
    document.getElementById('cancelGuestsBtn').addEventListener('click', closeGuestsModal);
    
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
    
    // Submit booking
    const submitBtn = document.getElementById('submitBooking');
    const paymentForm = document.getElementById('paymentForm');
    
    submitBtn.addEventListener('click', function() {
        // Validate form
        if (!paymentForm.checkValidity()) {
            paymentForm.reportValidity();
            return;
        }
        
        const cardNumber = document.getElementById('cardNumber').value;
        const expiryDate = document.getElementById('expiryDate').value;
        const cvv = document.getElementById('cvv').value;
        const postalCode = document.getElementById('postalCode').value;
        const country = document.getElementById('country').value;
        
        // Basic validation
        if (cardNumber.replace(/\s/g, '').length < 16) {
            alert('Vui lòng nhập số thẻ hợp lệ (16 số)');
            return;
        }
        
        if (cvv.length < 3) {
            alert('Vui lòng nhập CVV hợp lệ (3 số)');
            return;
        }
        
        // Show confirmation
        const confirmed = confirm(
            `Xác nhận đặt phòng\n\n` +
            `Phòng: ${roomData.title}\n` +
            `Ngày: ${document.getElementById('tripDates').textContent}\n` +
            `Khách: ${document.getElementById('tripGuests').textContent}\n` +
            `Tổng tiền: ${formatCurrency(prices.total)}\n\n` +
            `Bạn có chắc chắn muốn tiếp tục?`
        );
        
        if (confirmed) {
            // Simulate payment processing
            submitBtn.disabled = true;
            submitBtn.textContent = 'Đang xử lý...';
            
            setTimeout(() => {
                alert('Đặt phòng thành công! Bạn sẽ nhận được email xác nhận trong giây lát.');
                // Redirect to home or booking confirmation page
                window.location.href = '/';
            }, 2000);
        }
    });
    
    // Policy link
    const policyLink = document.querySelector('.policy-link');
    policyLink.addEventListener('click', function(e) {
        e.preventDefault();
        alert('Chính sách hủy:\n\n' +
              '- Hủy miễn phí trước 7 ngày: Hoàn tiền 100%\n' +
              '- Hủy trước 3-7 ngày: Hoàn tiền 50%\n' +
              '- Hủy trong vòng 3 ngày: Không hoàn tiền');
    });
    
    // Terms links
    const termsLinks = document.querySelectorAll('.terms-text a');
    termsLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const text = this.textContent;
            alert(`Trang ${text} đang được phát triển`);
        });
    });
    
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

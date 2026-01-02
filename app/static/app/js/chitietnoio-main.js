// Chitietnoio Main JavaScript
// File này chứa tất cả logic xử lý cho trang chi tiết nơi ở

// Lấy room ID từ URL query parameter
function getRoomIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return parseInt(params.get('room')) || 1;
}

// Load dữ liệu phòng
function loadRoom(roomId) {
    const room = rooms.find(r => r.id === roomId);
    if (!room) return;

    // Update title
    document.getElementById('page-title').textContent = room.title;
    document.getElementById('room-title').textContent = room.title;
    document.getElementById('room-location').textContent = room.location;
    document.getElementById('room-rating').textContent = room.rating.toFixed(1);
    document.getElementById('room-reviews').textContent = `${room.reviews} đánh giá`;
    document.getElementById('room-guests').textContent = `${room.guests} khách`;
    document.getElementById('guests-max').textContent = room.guests;
    document.getElementById('room-description').textContent = room.description;
    
    // Card info - but do NOT override server-provided price when SERVER_LISTING is true.
    try {
        const shouldOverridePrice = !(typeof SERVER_LISTING !== 'undefined' && SERVER_LISTING);
        if (shouldOverridePrice) {
            document.getElementById('card-price').textContent = `₫${room.price.toLocaleString('vi-VN')}`;
            document.getElementById('price-per-night').textContent = `₫${room.price.toLocaleString('vi-VN')} x 2 đêm`;
            document.getElementById('price-subtotal').textContent = `₫${(room.price * 2).toLocaleString('vi-VN')}`;
        }
        // Always update rating/reviews (non-price fields)
        document.getElementById('card-rating').textContent = room.rating.toFixed(1);
        document.getElementById('card-reviews').textContent = `${room.reviews} đánh giá`;
    } catch (e) {
        console.warn('loadRoom price update skipped due to error', e);
    }
    
    // Calculate fees only when we're using demo `rooms` data (do not override server breakdown)
    if (shouldOverridePrice) {
        // Calculate fees (roughly 32% service fee + 8% host protection)
        const subtotal = room.price * 2;
        const serviceFee = Math.round(subtotal * 0.32 / 100) * 100;
        const hostFee = Math.round(subtotal * 0.08 / 100) * 100;
        const total = subtotal + serviceFee + hostFee;

        if (document.getElementById('fee-service')) document.getElementById('fee-service').textContent = `₫${serviceFee.toLocaleString('vi-VN')}`;
        if (document.getElementById('fee-host')) document.getElementById('fee-host').textContent = `₫${hostFee.toLocaleString('vi-VN')}`;
        if (document.getElementById('price-total')) document.getElementById('price-total').textContent = `₫${total.toLocaleString('vi-VN')}`;
    } else {
        // When using server-backed listing, ask the server to compute breakdown (if function available)
        try {
            const bookingCard = document.querySelector('.booking-card');
            const listingId = bookingCard ? bookingCard.getAttribute('data-listing-id') || bookingCard.dataset.listingId : null;
            const checkin = document.querySelector('.booking-form input[type="date"]')?.value;
            const checkout = document.querySelectorAll('.booking-form input[type="date"]')[1]?.value;
            if (typeof fetchServerPrice === 'function' && listingId && checkin && checkout) {
                fetchServerPrice(listingId, checkin, checkout, 1);
            }
        } catch (e) {
            console.warn('fetchServerPrice call skipped', e);
        }
    }
    
    // Gallery
    document.getElementById('gallery-main-img').src = room.image;
    document.getElementById('thumb-1').src = room.image;
    document.getElementById('thumb-2').src = room.image;
    document.getElementById('thumb-3').src = room.image;
    document.getElementById('thumb-4').src = room.image;

    // Reviews header
    document.getElementById('reviews-header-rating').textContent = room.rating.toFixed(1);
    document.getElementById('reviews-header-count').textContent = room.reviews;
    
    // Location
    document.getElementById('location-text').textContent = room.location;

    // Host info (placeholder)
    const hostAvatarEl = document.getElementById('host-avatar');
    hostAvatarEl.onerror = function() {
        this.onerror = null;
        this.src = 'https://i.pinimg.com/736x/92/7d/70/927d70ace64407a8f2c0690928d3342d.jpg';
    };
    hostAvatarEl.src = "https://i.pinimg.com/736x/92/7d/70/927d70ace64407a8f2c0690928d3342d.jpg";
    document.getElementById('host-name').textContent = `Chủ nhà phòng ${room.id}`;
    document.getElementById('host-info').textContent = "Chủ nhà siêu cấp · Tham gia vào năm 2020";
    document.getElementById('host-reviews').textContent = Math.floor(Math.random() * 50) + 10;
    document.getElementById('host-rating').textContent = (Math.random() * 0.1 + 4.9).toFixed(2);
    document.getElementById('host-description').textContent = `Tôi yêu thích đón tiếp khách hàng tại phòng này. Phòng được chuẩn bị kỹ lưỡng để đảm bảo bạn có kỳ nghỉ thoải mái.`;

    // Load amenities
    loadAmenities(room);
}

// Load amenities preview (6 tiện nghi đầu tiên)
function loadAmenities(room) {
    const amenities = room.amenities || generateDefaultAmenities(room);
    const amenitiesList = document.getElementById('amenities-list');
    
    // Lấy 6 tiện nghi đầu tiên có available = true
    const displayAmenities = amenities.filter(a => a.available !== false).slice(0, 6);
    
    // Clear và fill lại
    amenitiesList.innerHTML = '';
    displayAmenities.forEach(amenity => {
        const col = document.createElement('div');
        col.className = 'col-md-6 mb-3';
        col.innerHTML = `
            <div class="d-flex align-items-center mb-3">
                <i class="fa-solid ${amenity.icon}" style="color: #ff385c; font-size: 20px;"></i>
                <span class="ms-3">${amenity.name}</span>
            </div>
        `;
        amenitiesList.appendChild(col);
    });

    // Update số lượng tiện nghi
    const totalAmenities = amenities.filter(a => a.available !== false).length;
    document.getElementById('amenities-count').textContent = totalAmenities;
}

// Load room khi trang load
document.addEventListener('DOMContentLoaded', function() {
    const roomId = getRoomIdFromURL();
    if (typeof rooms !== 'undefined') {
        loadRoom(roomId);
    } else {
        // rooms not available (we rely on server API); skip demo loader
        console.debug('rooms demo not present; skipping loadRoom');
    }
    
    // Xử lý nút "Xem thêm" mô tả
    document.getElementById('btn-show-more').addEventListener('click', function(e) {
        e.preventDefault();
        const room = rooms.find(r => r.id === roomId);
        if (room) {
            showDescriptionModal(room);
        }
    });

    // Xử lý nút "Xem tất cả tiện nghi"
    document.getElementById('btn-show-amenities').addEventListener('click', function(e) {
        e.preventDefault();
        const room = rooms.find(r => r.id === roomId);
        if (room) {
            showAmenitiesModal(room);
        }
    });
});

// Hiển thị modal mô tả
function showDescriptionModal(room) {
    const modalContent = document.getElementById('modal-description-content');
    const fullDesc = room.fullDescription || generateDefaultDescription(room);
    
    // Convert \n thành <br> và format
    const formattedDesc = fullDesc.replace(/\n/g, '<br>');
    modalContent.innerHTML = formattedDesc;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('descriptionModal'));
    modal.show();
}

// Tạo mô tả mặc định cho các phòng chưa có fullDescription
function generateDefaultDescription(room) {
    return `<strong>Chào mừng đến với ${room.title}!</strong><br><br>` +
           `📍 <strong>Vị trí:</strong><br>` +
           `- ${room.location}<br>` +
           `- Gần các điểm tham quan chính<br>` +
           `- Giao thông thuận tiện<br><br>` +
           `🏠 <strong>Không gian:</strong><br>` +
           `- Phòng rộng rãi, thoáng mát<br>` +
           `- Thiết kế hiện đại, sang trọng<br>` +
           `- Đầy đủ tiện nghi<br><br>` +
           `✨ <strong>Tiện nghi:</strong><br>` +
           `- Wi-Fi tốc độ cao miễn phí<br>` +
           `- Điều hòa nhiệt độ<br>` +
           `- TV màn hình phẳng<br>` +
           `- Bếp hoặc khu vực nấu ăn<br>` +
           `- Máy giặt<br><br>` +
           `🛏️ <strong>Giường ngủ:</strong><br>` +
           `- Giường thoải mái với ga trải sạch sẽ<br>` +
           `- Chăn gối đầy đủ<br><br>` +
           `🚿 <strong>Phòng tắm:</strong><br>` +
           `- Phòng tắm riêng biệt<br>` +
           `- Nước nóng 24/7<br>` +
           `- Đồ dùng vệ sinh cá nhân<br><br>` +
           `👥 <strong>Phù hợp cho:</strong><br>` +
           `- ${room.guests} khách<br>` +
           `- Gia đình, cặp đôi hoặc bạn bè<br>` +
           `- Du lịch hoặc công tác<br><br>` +
           `💰 <strong>Giá:</strong> ₫${room.price.toLocaleString('vi-VN')}/đêm<br><br>` +
           `<em>Chúng tôi luôn sẵn sàng đón tiếp bạn!</em>`;
}

// Hiển thị modal tiện nghi
function showAmenitiesModal(room) {
    const modalContent = document.getElementById('modal-amenities-content');
    const amenities = room.amenities || generateDefaultAmenities(room);
    
    // Tạo HTML cho danh sách tiện nghi
    let html = '<div class="row">';
    
    amenities.forEach((amenity, index) => {
        const iconClass = amenity.available !== false ? 'text-dark' : 'text-muted text-decoration-line-through';
        const iconStyle = amenity.available !== false ? 'color: #222;' : 'color: #999;';
        
        html += `
            <div class="col-md-6 mb-4">
                <div class="d-flex align-items-center">
                    <i class="fa-solid ${amenity.icon}" style="${iconStyle} font-size: 24px;"></i>
                    <span class="ms-3 ${iconClass}">${amenity.name}</span>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    modalContent.innerHTML = html;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('amenitiesModal'));
    modal.show();
}

// Tạo danh sách tiện nghi mặc định cho các phòng
function generateDefaultAmenities(room) {
    // Mỗi phòng có tiện nghi khác nhau dựa trên ID
    const baseAmenities = [
        {icon: "fa-wifi", name: "Wi-fi", available: true},
        {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
        {icon: "fa-tv", name: "TV", available: true},
        {icon: "fa-hot-tub-person", name: "Nước nóng", available: true},
    ];

    // Thêm tiện nghi dựa trên giá phòng
    if (room.price > 1500000) {
        baseAmenities.push(
            {icon: "fa-kitchen-set", name: "Bếp đầy đủ", available: true},
            {icon: "fa-washer", name: "Máy giặt", available: true},
            {icon: "fa-wind", name: "Máy sấy tóc", available: true},
            {icon: "fa-umbrella-beach", name: "Ban công", available: true},
            {icon: "fa-swimming-pool", name: "Hồ bơi", available: true},
            {icon: "fa-dumbbell", name: "Phòng gym", available: true},
            {icon: "fa-car", name: "Chỗ đỗ xe miễn phí", available: true},
            {icon: "fa-elevator", name: "Thang máy", available: true}
        );
    } else if (room.price > 1000000) {
        baseAmenities.push(
            {icon: "fa-kitchen-set", name: "Bếp", available: true},
            {icon: "fa-washer", name: "Máy giặt", available: true},
            {icon: "fa-lock", name: "Khóa ở cửa phòng ngủ", available: true},
            {icon: "fa-wind", name: "Quạt trần", available: true},
            {icon: "fa-utensils", name: "Đồ dùng nhà bếp", available: true},
            {icon: "fa-person-booth", name: "Cửa ra vào riêng", available: true}
        );
    } else {
        baseAmenities.push(
            {icon: "fa-utensils", name: "Đồ dùng nhà bếp cơ bản", available: true},
            {icon: "fa-wind", name: "Quạt", available: true},
            {icon: "fa-lock", name: "Khóa cửa", available: true}
        );
    }

    // Một số tiện nghi không có
    baseAmenities.push(
        {icon: "fa-paw", name: "Cho phép mang thú cưng", available: false},
        {icon: "fa-smoking", name: "Được phép hút thuốc", available: false}
    );

    // Biến đổi một chút dựa trên room ID để có sự khác biệt
    if (room.id % 3 === 0) {
        baseAmenities.push({icon: "fa-mug-hot", name: "Máy pha cà phê", available: true});
    }
    if (room.id % 5 === 0) {
        baseAmenities.push({icon: "fa-fire-extinguisher", name: "Bình cứu hỏa", available: true});
    }
    if (room.location.includes('Đà Lạt')) {
        baseAmenities.push({icon: "fa-fire", name: "Lò sưởi", available: true});
    }
    if (room.location.includes('Đà Nẵng') || room.location.includes('Vũng Tàu')) {
        baseAmenities.push({icon: "fa-person-swimming", name: "Gần bãi biển", available: true});
    }

    return baseAmenities;
}

// Hàm xóa backdrop và reset body
function cleanupModal() {
    // Kiểm tra xem có modal nào đang mở không
    const openModals = document.querySelectorAll('.modal.show');
    
    // Chỉ cleanup nếu KHÔNG có modal nào đang mở
    if (openModals.length === 0) {
        // Xóa tất cả backdrop còn sót lại
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(el => {
            el.remove();
        });
        
        // Xóa class modal-open khỏi body
        document.body.classList.remove('modal-open');
        
        // Reset style của body
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        document.body.style.pointerEvents = '';
    }
}

// Handle booking button click
document.addEventListener('DOMContentLoaded', function() {
    // Friendly login notice toast
    function showLoginNotice(message, loginUrl) {
        try {
            if (document.getElementById('loginNoticeToast')) return;
            const container = document.createElement('div');
            container.id = 'loginNoticeToast';
            container.style.position = 'fixed';
            container.style.right = '20px';
            container.style.bottom = '20px';
            container.style.zIndex = '99999';
            container.style.maxWidth = '320px';
            container.style.background = 'linear-gradient(180deg, #ffffff, #f8f4f1)';
            container.style.border = '1px solid rgba(0,0,0,0.06)';
            container.style.boxShadow = '0 6px 24px rgba(0,0,0,0.12)';
            container.style.padding = '14px';
            container.style.borderRadius = '10px';
            container.style.fontFamily = 'Arial, sans-serif';

            container.innerHTML = `
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="flex:1">
                        <div style="font-weight:600;margin-bottom:6px;color:#333">Bạn cần đăng nhập</div>
                        <div style="font-size:13px;color:#444">${message}</div>
                    </div>
                    <div style="display:flex;flex-direction:column;gap:6px">
                        <button id="loginNoticeBtn" style="background:#ff6b3d;border:none;color:white;padding:8px 10px;border-radius:8px;cursor:pointer;font-weight:600">Đăng nhập</button>
                        <button id="loginNoticeClose" style="background:transparent;border:none;color:#666;cursor:pointer;font-size:12px">Đóng</button>
                    </div>
                </div>
            `;

            document.body.appendChild(container);

            document.getElementById('loginNoticeBtn').addEventListener('click', function() {
                const next = encodeURIComponent(window.location.pathname + window.location.search);
                const url = (typeof loginUrl !== 'undefined' && loginUrl) ? loginUrl : '/login/';
                window.location.href = `${url}?next=${next}`;
            });
            document.getElementById('loginNoticeClose').addEventListener('click', function() {
                container.remove();
            });

            setTimeout(() => { try { container.remove(); } catch(_){} }, 8000);
        } catch (e) { console.error('showLoginNotice error', e); }
    }

    const bookingBtn = document.querySelector('.booking-btn-main');
    // enforce min dates on listing booking card
    try {
        const bookingFormEl = document.querySelector('.booking-form');
        const dateInputs = bookingFormEl ? bookingFormEl.querySelectorAll('input[type="date"]') : [];
        const checkInEl = dateInputs && dateInputs.length > 0 ? dateInputs[0] : null;
        const checkOutEl = dateInputs && dateInputs.length > 1 ? dateInputs[1] : null;
        const now = new Date(); now.setHours(0,0,0,0);
        const todayISO = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
        const tomorrow = new Date(now.getTime() + 24*60*60*1000);
        const tomorrowISO = `${tomorrow.getFullYear()}-${String(tomorrow.getMonth()+1).padStart(2,'0')}-${String(tomorrow.getDate()).padStart(2,'0')}`;
        if (checkInEl) checkInEl.setAttribute('min', todayISO);
        if (checkOutEl) checkOutEl.setAttribute('min', tomorrowISO);
        // Default values: check-in = today, check-out = today + 2 days
        try {
            if (checkInEl && !checkInEl.value) checkInEl.value = todayISO;
            if (checkOutEl && !checkOutEl.value) {
                const twoDays = new Date(now.getTime() + 2*24*60*60*1000);
                const twoDaysISO = `${twoDays.getFullYear()}-${String(twoDays.getMonth()+1).padStart(2,'0')}-${String(twoDays.getDate()).padStart(2,'0')}`;
                checkOutEl.value = twoDaysISO;
                if (checkOutEl.getAttribute('min') && checkOutEl.value < checkOutEl.getAttribute('min')) {
                    checkOutEl.value = checkOutEl.getAttribute('min');
                }
            }
            if (checkInEl && checkOutEl) {
                checkInEl.addEventListener('change', function() {
                    try {
                        const ci = new Date(checkInEl.value);
                        if (!isNaN(ci)) {
                            ci.setHours(0,0,0,0);
                            const minCo = new Date(ci.getTime() + 24*60*60*1000);
                            const minCoISO = `${minCo.getFullYear()}-${String(minCo.getMonth()+1).padStart(2,'0')}-${String(minCo.getDate()).padStart(2,'0')}`;
                            checkOutEl.setAttribute('min', minCoISO);
                            // default checkout to checkin + 2 days for convenience
                            const defaultCo = new Date(ci.getTime() + 2*24*60*60*1000);
                            const defaultCoISO = `${defaultCo.getFullYear()}-${String(defaultCo.getMonth()+1).padStart(2,'0')}-${String(defaultCo.getDate()).padStart(2,'0')}`;
                            if (!checkOutEl.value) {
                                checkOutEl.value = defaultCoISO;
                            } else if (checkOutEl.value < minCoISO) {
                                checkOutEl.value = defaultCoISO;
                            }
                            // update calendar summary text when dates change
                            try {
                                const calendarEl = document.getElementById('calendarRange');
                                if (calendarEl) {
                                    const ci2 = new Date(checkInEl.value);
                                    const co2 = new Date(checkOutEl.value);
                                    if (!isNaN(ci2) && !isNaN(co2)) {
                                        const fmt = d => `${d.getDate()}/${d.getMonth()+1}/${d.getFullYear()}`;
                                        const nights2 = Math.ceil((co2 - ci2)/(24*60*60*1000));
                                        calendarEl.textContent = `Ngày ${fmt(ci2)} - ${fmt(co2)} · ${nights2} đêm`;
                                    }
                                }
                            } catch (e) {}
                        }
                    } catch (e) {}
                });
            }
            // initial calendar summary update (when defaults assigned)
            try {
                const calendarElInit = document.getElementById('calendarRange');
                if (calendarElInit && checkInEl && checkOutEl) {
                    const ci0 = new Date(checkInEl.value);
                    const co0 = new Date(checkOutEl.value);
                    if (!isNaN(ci0) && !isNaN(co0)) {
                        const fmt0 = d => `${d.getDate()}/${d.getMonth()+1}/${d.getFullYear()}`;
                        const nights0 = Math.ceil((co0 - ci0)/(24*60*60*1000));
                        calendarElInit.textContent = `Ngày ${fmt0(ci0)} - ${fmt0(co0)} · ${nights0} đêm`;
                    }
                }
            } catch (e) {}
        } catch (e) {}
    } catch (e) {}
    if (bookingBtn) {
        // If availability flow is enabled (set by server-backed template),
        // skip attaching the default redirect handler here.
        if (typeof window.__useAvailabilityFlow !== 'undefined' && window.__useAvailabilityFlow) {
            // Availability flow will attach its own click handler in the template.
        } else {
        bookingBtn.addEventListener('click', function() {
            // If user not authenticated, prompt and redirect to login page
            try {
                if (typeof window.__isAuthenticated !== 'undefined' && !window.__isAuthenticated) {
                    // show friendly toast instead of confirm
                    const loginUrl = (typeof window.__loginUrl !== 'undefined') ? window.__loginUrl : '/login/';
                    showLoginNotice('Bạn cần đăng nhập trước khi đặt phòng. Nhấn nút Đăng nhập để tiếp tục.', loginUrl);
                    return;
                }
            } catch (err) {
                console.debug('Auth check failed, proceeding to booking navigation', err);
            }

            const roomId = getRoomIdFromURL();
            // Try to read selected dates and guests from the booking card
            try {
                const bookingForm = document.querySelector('.booking-form');
                const dateInputs = bookingForm ? bookingForm.querySelectorAll('input[type="date"]') : [];
                const checkIn = dateInputs && dateInputs.length > 0 ? dateInputs[0].value : '';
                const checkOut = dateInputs && dateInputs.length > 1 ? dateInputs[1].value : '';
                // Validate dates against today
                try {
                    const now = new Date(); now.setHours(0,0,0,0);
                    const todayISO = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
                    if (checkIn && checkIn < todayISO) { showInlineNotice('Ngày nhận phòng không được trước ngày hôm nay. Vui lòng chọn lại.'); return; }
                    if (checkIn && checkOut && checkOut <= checkIn) { showInlineNotice('Ngày trả phòng phải sau ngày nhận phòng. Vui lòng chọn lại.'); return; }
                } catch (e) {
                    // ignore
                }
                const guestsEl = bookingForm ? bookingForm.querySelector('select') : null;
                let guests = '';
                if (guestsEl) {
                    const opt = guestsEl.options[guestsEl.selectedIndex];
                    guests = opt ? opt.text.replace(/[^0-9]/g, '') : '';
                }

                const params = new URLSearchParams();
                params.set('room', roomId);
                if (checkIn) params.set('checkin', checkIn);
                if (checkOut) params.set('checkout', checkOut);
                if (guests) params.set('guests', guests);

                    // store subtotal in sessionStorage to avoid long URLs
                    const subtotalEl = document.getElementById('price-subtotal') || document.getElementById('subtotal');
                    if (subtotalEl) {
                        try {
                            const raw = subtotalEl.textContent || subtotalEl.value || '';
                            const numeric = raw.replace(/[^0-9]/g, '');
                            if (numeric) sessionStorage.setItem('booking_subtotal', numeric);
                        } catch (err) {
                            // ignore
                        }
                    }

                window.location.href = `/datphong/?${params.toString()}`;
            } catch (e) {
                // fallback to simple navigation
                window.location.href = `/datphong/?room=${roomId}`;
            }
        });
        }
    }

    // Xử lý đóng modal - xóa backdrop và reset body
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        // Khi modal đã đóng hoàn toàn
        modal.addEventListener('hidden.bs.modal', function () {
            // Đợi một chút để Bootstrap xử lý xong
            setTimeout(cleanupModal, 300);
        });
    });
});

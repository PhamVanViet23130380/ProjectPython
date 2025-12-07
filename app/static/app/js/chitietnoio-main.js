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
    
    // Card info
    document.getElementById('card-price').textContent = `₫${room.price.toLocaleString('vi-VN')}`;
    document.getElementById('card-rating').textContent = room.rating.toFixed(1);
    document.getElementById('card-reviews').textContent = `${room.reviews} đánh giá`;
    document.getElementById('price-per-night').textContent = `₫${room.price.toLocaleString('vi-VN')} x 2 đêm`;
    document.getElementById('price-subtotal').textContent = `₫${(room.price * 2).toLocaleString('vi-VN')}`;
    
    // Calculate fees (roughly 32% service fee + 8% host protection)
    const subtotal = room.price * 2;
    const serviceFee = Math.round(subtotal * 0.32 / 100) * 100;
    const hostFee = Math.round(subtotal * 0.08 / 100) * 100;
    const total = subtotal + serviceFee + hostFee;
    
    document.getElementById('fee-service').textContent = `₫${serviceFee.toLocaleString('vi-VN')}`;
    document.getElementById('fee-host').textContent = `₫${hostFee.toLocaleString('vi-VN')}`;
    document.getElementById('price-total').textContent = `₫${total.toLocaleString('vi-VN')}`;
    
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
    loadRoom(roomId);
    
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
    const bookingBtn = document.querySelector('.booking-btn-main');
    if (bookingBtn) {
        bookingBtn.addEventListener('click', function() {
            const roomId = getRoomIdFromURL();
            window.location.href = `/datphong/?room=${roomId}`;
        });
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

// Database của tất cả 48 phòng - chỉ lưu link đến file này sẽ được load từ chitietnoio.html
// Dữ liệu này được export để sử dụng trong chitietnoio-main.js

const rooms = [
    // Section 1: Nơi lưu trú được ưa chuộng tại Hồ Chí Minh (8 phòng)
    { 
        id: 1, 
        title: "Phòng tại Thành phố Hồ Chí Minh", 
        price: 399000, 
        rating: 5.0, 
        reviews: 13, 
        image: "https://a0.muscache.com/im/pictures/hosting/Hosting-1496408576612343725/original/0bbb91de-5c32-46ce-b2aa-4914c331fc13.jpeg?im_w=1440", 
        location: "Quận 1, Thành phố Hồ Chí Minh", 
        guests: 2, 
        description: "Phòng tuyệt vời tại vị trí chiến lược trong trung tâm thành phố. Sạch sẽ, rẻ và khá yên tĩnh.",
        fullDescription: "Chào mừng bạn đến với phòng ấm cúng tại trung tâm Sài Gòn!\n\n🏠 Không gian:\n- Phòng ngủ riêng biệt với giường đôi thoải mái\n- Nhà bếp đầy đủ đồ dùng nấu nướng\n- Phòng tắm riêng với nước nóng 24/7\n- Ban công nhỏ để thư giãn\n\n📍 Vị trí:\n- Cách Bến Thành Market chỉ 5 phút đi bộ\n- Gần phố đi bộ Nguyễn Huệ\n- Nhiều quán ăn, cà phê xung quanh\n- Dễ dàng di chuyển đến các điểm tham quan\n\n✨ Tiện nghi:\n- Wi-Fi tốc độ cao miễn phí\n- Điều hòa không khí\n- Tivi màn hình phẳng\n- Máy giặt chung\n\n🎯 Lưu ý:\n- Check-in linh hoạt với hướng dẫn tự nhận phòng\n- Phù hợp cho du khách, cặp đôi hoặc người công tác\n- Khu vực an toàn, yên tĩnh vào ban đêm",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-kitchen-set", name: "Bếp", available: true},
            {icon: "fa-washer", name: "Máy giặt", available: true},
            {icon: "fa-lock", name: "Khóa ở cửa phòng ngủ", available: true},
            {icon: "fa-tv", name: "TV", available: true},
            {icon: "fa-wind", name: "Quạt trần", available: true},
            {icon: "fa-utensils", name: "Đồ dùng nhà bếp", available: true},
            {icon: "fa-hot-tub-person", name: "Nước nóng", available: true},
            {icon: "fa-person-booth", name: "Cửa ra vào riêng", available: true},
            {icon: "fa-paw", name: "Cho phép mang thú cưng", available: false},
            {icon: "fa-smoking", name: "Được phép hút thuốc", available: false}
        ]
    },
    { 
        id: 2, 
        title: "Căn hộ tại Thành phố Hồ Chí Minh", 
        price: 455900, 
        rating: 4.98, 
        reviews: 42, 
        image: "https://a0.muscache.com/im/pictures/hosting/Hosting-1386690223982968237/original/4df20859-007e-4a86-8db1-7a008298e23e.jpeg?im_w=1200", 
        location: "Quận 1, Thành phố Hồ Chí Minh", 
        guests: 4, 
        description: "Căn hộ hiện đại với view thành phố tuyệt đẹp, gần trung tâm mua sắm.",
        fullDescription: "Căn hộ cao cấp với đầy đủ tiện nghi!\n\n🏙️ View tuyệt đẹp nhìn ra thành phố\n🛏️ 2 phòng ngủ rộng rãi\n🍳 Bếp đầy đủ thiết bị\n🏊 Hồ bơi chung",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-swimming-pool", name: "Hồ bơi", available: true},
            {icon: "fa-dumbbell", name: "Phòng gym", available: true},
            {icon: "fa-elevator", name: "Thang máy", available: true},
            {icon: "fa-parking", name: "Chỗ đậu xe miễn phí", available: true}
        ]
    },
    { 
        id: 3, 
        title: "Căn hộ tại Thành phố Hồ Chí Minh", 
        price: 875930, 
        rating: 4.82, 
        reviews: 28, 
        image: "https://a0.muscache.com/im/pictures/miso/Hosting-1425899556206659577/original/140dc752-7bb4-49f7-b47f-69ef266c1d47.jpeg?im_w=1200", 
        location: "Quận 3, Thành phố Hồ Chí Minh", 
        guests: 3, 
        description: "Studio hiện đại với view đẹp, đầy đủ tiện nghi cao cấp.",
        fullDescription: "Studio sang trọng tại khu vực yên tĩnh!\n\n✨ Thiết kế hiện đại\n🌃 View thành phố tuyệt đẹp\n📺 Smart TV 55 inch\n☕ Máy pha cà phê Nespresso",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-tv", name: "Smart TV", available: true}
        ]
    },
    { 
        id: 4, 
        title: "Căn hộ chung cư cao cấp tại Thành phố Hồ Chí Minh", 
        price: 1180000, 
        rating: 4.96, 
        reviews: 35, 
        image: "https://a0.muscache.com/im/pictures/hosting/Hosting-1462849377191931233/original/081e4730-71e3-43f9-a70e-3b21842046f8.jpeg?im_w=1200", 
        location: "Quận 2, Thành phố Hồ Chí Minh", 
        guests: 4, 
        description: "Căn hộ cao cấp với đầy đủ tiện nghi 5 sao, view sông Sài Gòn.",
        fullDescription: "Penthouse cao cấp!\n\n🌊 View sông Sài Gòn tuyệt đẹp\n🏊 Hồ bơi vô cực\n🍽️ Bếp hiện đại\n🛁 Bồn tắm jacuzzi",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-swimming-pool", name: "Hồ bơi vô cực", available: true},
            {icon: "fa-hot-tub", name: "Jacuzzi", available: true}
        ]
    },
    { 
        id: 5, 
        title: "Phòng tại Thành phố Hồ Chí Minh", 
        price: 467882, 
        rating: 4.93, 
        reviews: 18, 
        image: "https://a0.muscache.com/im/pictures/hosting/Hosting-1418059956711068789/original/ed9cbbbf-14b4-4c38-9624-8f6a7930f7a9.jpeg?im_w=1200", 
        location: "Quận 7, Thành phố Hồ Chí Minh", 
        guests: 2, 
        description: "Phòng ấm cúng tại khu vực yên tĩnh, gần Phú Mỹ Hưng.",
        fullDescription: "Phòng đẹp tại khu vực cao cấp!\n\n🌳 Khu vực yên tĩnh, nhiều cây xanh\n🛒 Gần trung tâm thương mại\n🚗 Bãi đậu xe miễn phí",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-parking", name: "Chỗ đậu xe", available: true}
        ]
    },
    
    // Section 7: Nơi lưu trú được ưa chuộng tại Huyện Văn Giang (8 phòng: 49-56)
    { 
        id: 49, 
        title: "Căn hộ tại Văn Giang", 
        price: 370882, 
        rating: 4.92, 
        reviews: 25, 
        image: "https://a0.muscache.com/im/pictures/miso/Hosting-1151351297822170295/original/6608e314-b668-4f60-b5b8-ce7ad148cff1.jpeg?im_w=1440", 
        location: "Văn Giang, Hưng Yên", 
        guests: 2, 
        description: "Căn hộ hiện đại tại Văn Giang với giá tốt, view đẹp.",
        fullDescription: "Căn hộ thoáng mát tại khu vực phát triển!\n\n🏢 Căn hộ mới xây\n🌳 Không gian xanh\n🚗 Gần cao tốc Hà Nội - Hải Phòng\n🛒 Gần trung tâm thương mại",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-tv", name: "TV", available: true},
            {icon: "fa-parking", name: "Chỗ đậu xe", available: true}
        ]
    },
    { 
        id: 50, 
        title: "Căn hộ tại Văn Giang", 
        price: 720989, 
        rating: 4.94, 
        reviews: 31, 
        image: "https://a0.muscache.com/im/pictures/hosting/Hosting-1286736826121492741/original/08c1d595-7718-4004-85e9-fda37aa66df8.jpeg?im_w=1440", 
        location: "Văn Giang, Hưng Yên", 
        guests: 3, 
        description: "Căn hộ cao cấp với đầy đủ tiện nghi hiện đại.",
        fullDescription: "Căn hộ 2 phòng ngủ rộng rãi!\n\n🛏️ 2 phòng ngủ thoáng mát\n🍳 Bếp đầy đủ thiết bị\n🏊 Hồ bơi chung\n💪 Phòng gym miễn phí",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-swimming-pool", name: "Hồ bơi", available: true},
            {icon: "fa-dumbbell", name: "Phòng gym", available: true}
        ]
    },
    { 
        id: 51, 
        title: "Căn hộ tại Văn Giang", 
        price: 975706, 
        rating: 4.97, 
        reviews: 38, 
        image: "https://a0.muscache.com/im/pictures/hosting/Hosting-U3RheVN1cHBseUxpc3Rpbmc6MTI4NTExNjY0MzgwNDk2NDY2MA==/original/4cccfb0d-a188-405c-a0b9-da83f505d58b.jpeg?im_w=1440", 
        location: "Văn Giang, Hưng Yên", 
        guests: 4, 
        description: "Căn hộ cao cấp view hồ Thiên Nga tuyệt đẹp.",
        fullDescription: "Căn hộ view hồ lãng mạn!\n\n🌊 View hồ Thiên Nga\n🌅 Ban công rộng ngắm hoàng hôn\n🛋️ Nội thất cao cấp\n🔒 Bảo vệ 24/7",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-water", name: "View hồ", available: true},
            {icon: "fa-shield-halved", name: "Bảo vệ 24/7", available: true}
        ]
    },
    { 
        id: 52, 
        title: "Căn hộ tại Văn Giang", 
        price: 741765, 
        rating: 5.0, 
        reviews: 22, 
        image: "https://a0.muscache.com/im/pictures/hosting/Hosting-1363415932540979884/original/d28c1567-d02f-4655-8164-b5ce703b1980.jpeg?im_w=1440", 
        location: "Văn Giang, Hưng Yên", 
        guests: 2, 
        description: "Căn hộ studio hiện đại, sạch sẽ và tiện nghi.",
        fullDescription: "Studio hoàn hảo cho cặp đôi!\n\n💑 Không gian lãng mạn\n🛏️ Giường king size\n📺 Smart TV 43 inch\n🍳 Bếp mini đầy đủ",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-tv", name: "Smart TV", available: true},
            {icon: "fa-kitchen-set", name: "Bếp", available: true}
        ]
    },
    { 
        id: 53, 
        title: "Căn hộ tại Văn Giang", 
        price: 519546, 
        rating: 4.95, 
        reviews: 29, 
        image: "https://a0.muscache.com/im/pictures/miso/Hosting-1332956004603755686/original/88b48b5a-61cf-4a60-973f-d844334298a2.jpeg?im_w=1440", 
        location: "Văn Giang, Hưng Yên", 
        guests: 3, 
        description: "Căn hộ gia đình với 2 phòng ngủ, giá hợp lý.",
        fullDescription: "Căn hộ lý tưởng cho gia đình nhỏ!\n\n👨‍👩‍👧 Phù hợp gia đình 3-4 người\n🛏️ 2 phòng ngủ riêng biệt\n👶 Có nôi cho trẻ em\n🧸 Khu vui chơi trẻ em",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-baby", name: "Nôi trẻ em", available: true},
            {icon: "fa-child", name: "Khu vui chơi", available: true}
        ]
    },
    { 
        id: 54, 
        title: "Căn hộ chung cư cao cấp tại Văn Giang", 
        price: 847323, 
        rating: 4.97, 
        reviews: 34, 
        image: "https://a0.muscache.com/im/pictures/miso/Hosting-1358709795835664748/original/2d80cec2-b1cb-494b-a61f-a0d1efe09cb0.jpeg?im_w=1440", 
        location: "Văn Giang, Hưng Yên", 
        guests: 4, 
        description: "Căn hộ chung cư cao cấp với hồ bơi và gym.",
        fullDescription: "Căn hộ cao cấp đầy đủ tiện ích!\n\n🏊 Hồ bơi 4 mùa\n💪 Phòng gym hiện đại\n🎾 Sân tennis\n🌳 Công viên nội khu",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-swimming-pool", name: "Hồ bơi 4 mùa", available: true},
            {icon: "fa-dumbbell", name: "Phòng gym", available: true},
            {icon: "fa-baseball", name: "Sân tennis", available: true}
        ]
    },
    { 
        id: 55, 
        title: "Căn hộ tại Hồ Thiên Nga", 
        price: 1099671, 
        rating: 4.97, 
        reviews: 41, 
        image: "https://a0.muscache.com/im/pictures/miso/Hosting-1189731487467754109/original/beb1914a-015b-409c-b72d-ac368cf5c6df.jpeg?im_w=1200", 
        location: "Hồ Thiên Nga, Văn Giang, Hưng Yên", 
        guests: 5, 
        description: "Căn hộ 3 phòng ngủ view hồ tuyệt đẹp, phù hợp gia đình lớn.",
        fullDescription: "Căn hộ rộng rãi view hồ!\n\n🏡 3 phòng ngủ + 2 phòng tắm\n🌊 View toàn cảnh hồ Thiên Nga\n🍽️ Phòng ăn rộng 20m²\n🛋️ Phòng khách 35m²",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-water", name: "View hồ tuyệt đẹp", available: true},
            {icon: "fa-utensils", name: "Bếp đầy đủ", available: true},
            {icon: "fa-parking", name: "2 chỗ đậu xe", available: true}
        ]
    },
    { 
        id: 56, 
        title: "Căn hộ tại Văn Giang", 
        price: 764588, 
        rating: 5.0, 
        reviews: 19, 
        image: "https://a0.muscache.com/im/pictures/hosting/Hosting-1486889413234179338/original/2bb9bc2b-2f0d-448e-b392-fecd4d1771f0.jpeg?im_w=1440", 
        location: "Văn Giang, Hưng Yên", 
        guests: 2, 
        description: "Căn hộ mới 100%, nội thất sang trọng, vị trí đẹp.",
        fullDescription: "Căn hộ mới hoàn toàn!\n\n✨ Nội thất mới 100%\n🛏️ Giường Hanssem cao cấp\n📺 Smart TV 55 inch\n🍳 Bếp từ Munchen\n🚿 Vòi sen nhiệt độ\n🌟 Đánh giá 5 sao hoàn hảo",
        amenities: [
            {icon: "fa-wifi", name: "Wi-fi", available: true},
            {icon: "fa-snowflake", name: "Điều hòa nhiệt độ", available: true},
            {icon: "fa-tv", name: "Smart TV 55 inch", available: true},
            {icon: "fa-kitchen-set", name: "Bếp từ cao cấp", available: true},
            {icon: "fa-hot-tub-person", name: "Vòi sen nhiệt độ", available: true},
            {icon: "fa-sparkles", name: "Nội thất mới 100%", available: true}
        ]
    }
];

// Export để sử dụng trong file khác (nếu sử dụng modules)
// Nếu không dùng modules, biến rooms sẽ tự động là global variable
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { rooms };
}

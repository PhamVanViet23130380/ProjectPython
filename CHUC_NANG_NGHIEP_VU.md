    # CHỨC NĂNG VÀ NGHIỆP VỤ - DỰ ÁN HOMNEST

    > **Hệ thống đặt phòng và quản lý chỗ ở (giống Airbnb)**  
    > **Báo cáo cuối kỳ - Tháng 2/2026**

    ---

    ## 🎯 TỔNG QUAN HỆ THỐNG

    **Homnest** là nền tảng cho thuê chỗ ở kết nối **Guest** (khách thuê) và **Host** (chủ nhà), có tích hợp **AI phân tích đánh giá** và **thanh toán trực tuyến**.

    ### **3 NHÓM NGƯỜI DÙNG:**
    1. **Guest** - Người tìm và đặt chỗ ở
    2. **Host** - Chủ nhà cho thuê  
    3. **Admin** - Quản trị viên hệ thống

    ---

    ## 📌 CHỨC NĂNG CHI TIẾT

    ### **1. QUẢN LÝ TÀI KHOẢN** 👤

    #### **1.1. Đăng ký & Đăng nhập:**
    - Đăng ký tài khoản bằng email
    - Xác thực OTP qua email (6 số)
    - Đăng nhập bằng email + password
    - Quên mật khẩu (reset qua email)
    - Logout

    #### **1.2. Quản lý hồ sơ:**
    - Xem thông tin cá nhân
    - Chỉnh sửa: Họ tên, SĐT, avatar
    - Thống kê: Số booking, số review
    - Phân quyền: Guest / Host / Admin

    ---

    ### **2. CHỨC NĂNG CHO GUEST (KHÁCH THUÊ)** 🏠

    #### **2.1. Tìm kiếm chỗ ở:**
    - Tìm theo: Địa điểm, ngày, số khách
    - Lọc theo: Giá, loại phòng, tiện nghi
    - Hiển thị kết quả với:
    - Ảnh chỗ ở
    - Giá/đêm
    - Rating trung bình
    - Số đánh giá

    #### **2.2. Xem chi tiết chỗ ở:**
    - **Thông tin cơ bản:**
    - Tiêu đề, mô tả
    - Loại chỗ ở (nhà riêng, căn hộ, phòng...)
    - Số phòng ngủ, giường, phòng tắm
    - Số khách tối đa (người lớn + trẻ em + pets)
    
    - **Tiện nghi:**
    - Tiện nghi cơ bản (WiFi, TV, bếp...)
    - Tiện nghi nổi bật (Hồ bơi, Gym...)
    - Tiện nghi an toàn (Báo cháy, CCTV...)

    - **Bản đồ:**
    - Hiển thị vị trí trên Leaflet Map
    - Địa chỉ chi tiết (sau khi đặt)
    - Geocoding tự động

    - **Đánh giá:**
    - Xem review của khách cũ
    - Sao trung bình + tổng số review
    - AI phân loại: Tích cực / Tiêu cực / Trung tính
    - Ảnh/video review

    - **Thông tin host:**
    - Tên, avatar, ngày tham gia
    - Số điện thoại, email
    - Nút "Nhắn tin cho chủ nhà"

    #### **2.3. Đặt phòng:**
    - Chọn ngày nhận phòng / trả phòng
    - Chọn số khách
    - Kiểm tra tình trạng (available/booked)
    - Tính toán giá tự động:
    - Giá cơ bản = Giá/đêm × Số đêm
    - Phí dịch vụ: 350,000 VNĐ (cố định)
    - Tổng cộng

    #### **2.4. Thanh toán:**
    - **Phương thức:** VNPay Gateway
    - **Quy trình:**
    1. Tạo booking (status = pending)
    2. Redirect sang VNPay
    3. Nhập thông tin thanh toán
    4. VNPay xử lý
    5. Return về website
    6. Cập nhật status = confirmed
    7. Gửi email xác nhận

    #### **2.5. Quản lý booking:**
    - Xem lịch sử đặt phòng
    - Trạng thái: Pending / Confirmed / Completed / Cancelled
    - Chi tiết booking:
    - Thông tin chỗ ở
    - Ngày check-in / check-out
    - Tổng tiền đã thanh toán
    - Trạng thái thanh toán
    - Hủy booking (nếu chưa check-in)

    #### **2.6. Đánh giá:**
    - **Điều kiện:** Sau khi check-out
    - **Nội dung:**
    - Rating (1-5 sao)
    - Nhận xét văn bản
    - Upload ảnh/video (tùy chọn)
    - **AI xử lý:**
    - Phân tích cảm xúc (ViSoBERT)
    - Phát hiện spam:
        - Từ lặp lại
        - Chữ in hoa quá nhiều
        - Nội dung vô nghĩa
    - Gắn nhãn: Positive / Negative / Neutral

    #### **2.7. Khiếu nại:**
    - Gửi khiếu nại sau khi hoàn thành booking
    - Nội dung khiếu nại (≥10 ký tự)
    - Email thông báo cho admin
    - Theo dõi trạng thái: Open / Resolved

    #### **2.8. Chat với Host:**
    - Tạo cuộc hội thoại tự động khi booking
    - Gửi/nhận tin nhắn real-time
    - Đánh dấu đã đọc
    - Lịch sử chat

    ---

    ### **3. CHỨC NĂNG CHO HOST (CHỦ NHÀ)** 🏡

    #### **3.1. Đăng tin cho thuê (Wizard 3 bước):**

    **Bước 1: Thông tin cơ bản**
    - Chọn loại chỗ ở (12 loại)
    - Loại sử dụng (Toàn bộ nhà / Phòng riêng / Phòng chung)
    - Địa chỉ chi tiết + Bản đồ
    - Số lượng: Phòng ngủ, giường, phòng tắm
    - Số khách tối đa (người lớn, trẻ em, pets)

    **Bước 2: Tiện nghi & Ảnh**
    - Chọn tiện nghi (checkboxes)
    - Upload ảnh (tối thiểu 5 ảnh)
    - Chọn ảnh đại diện

    **Bước 3: Giá & Thời gian**
    - Đặt giá/đêm
    - Thời gian cho thuê (từ ngày - đến ngày)
    - Tiêu đề và mô tả
    - Xác nhận đăng

    **Kết quả:**
    - Listing tạo với status = "pending"
    - Chờ admin duyệt

    #### **3.2. Quản lý chỗ ở:**
    - Xem danh sách listing của mình
    - Chỉnh sửa thông tin
    - Bật/tắt hiển thị (is_active)
    - Xem thống kê:
    - Số lượt xem
    - Số booking
    - Doanh thu

    #### **3.3. Quản lý booking đến:**
    - Xem booking cho các listing của mình
    - Trạng thái booking
    - Thông tin khách
    - Ngày check-in / check-out
    - Tổng tiền nhận được

    #### **3.4. Chat với Guest:**
    - Trả lời tin nhắn từ khách
    - Hỗ trợ trước/trong/sau kỳ thuê

    ---

    ### **4. CHỨC NĂNG ADMIN (QUẢN TRỊ)** 👨‍💼

    #### **4.1. Quản lý người dùng:**
    - Danh sách tất cả users
    - Xem: ID, Email, Họ tên, Role, Avatar
    - Phân quyền: Guest / Host / Admin
    - Bật/tắt tài khoản (is_active)
    - Xóa người dùng (cascade)

    #### **4.2. Quản lý chỗ ở:**
    - **Duyệt listing:**
    - Xem listing pending
    - Actions: Approve / Reject
    - Set status: approved / rejected
    - Set is_active = True/False
    
    - **Quản lý tất cả listings:**
    - Xem: Tiêu đề, Host, Giá, Status
    - Lọc theo: Status, Host, Giá
    - Tìm kiếm
    - Chỉnh sửa chi tiết
    - Xóa listing

    #### **4.3. Quản lý booking:**
    - Xem tất cả bookings
    - Lọc theo: Status, User, Listing, Ngày
    - Chi tiết:
    - Guest, Host
    - Listing
    - Check-in / Check-out
    - Tổng tiền
    - Trạng thái booking & payment
    - Inline payment info

    #### **4.4. Quản lý thanh toán:**
    - Xem tất cả payments
    - Liên kết với booking
    - Amount, Method, Status
    - Transaction ID
    - Ngày thanh toán
    - Actions: Mark as paid

    #### **4.5. Quản lý review & AI:**
    - **Xem reviews:**
    - User, Listing, Rating, Comment
    - AI Analysis (Sentiment)
    - Spam status
    - **AI Analysis:**
    - Xem kết quả phân tích ViSoBERT
    - Sentiment: pos / neg / neu
    - Confidence score
    - **Spam Classification:**
    - Spam status (True/False)
    - Spam reason
    - Ẩn review spam

    #### **4.6. Quản lý khiếu nại:**
    - Danh sách complaints
    - User, Listing, Lý do
    - Status: Open / Resolved
    - Đánh dấu đã giải quyết
    - Gửi email phản hồi

    #### **4.7. Thống kê doanh thu:** 📊
    - **Biểu đồ:**
    - Doanh thu theo tháng (Chart.js)
    - Số booking theo tháng
    - Top listings có doanh thu cao
    
    - **Số liệu:**
    - Tổng doanh thu
    - Tổng booking
    - Tổng users
    - Tổng listings
    - Trung bình giá/đêm

    #### **4.8. Admin UI (Jazzmin):**
    - Giao diện admin đẹp
    - Màu theme: Warning (nâu/vàng)
    - Dashboard tổng quan
    - Search & filters
    - Custom actions

    ---

    ## 🔄 NGHIỆP VỤ CHÍNH

    ### **1. QUY TRÌNH ĐẶT PHÒNG:**
    ```
    1. Guest tìm kiếm chỗ ở
    2. Xem chi tiết listing
    3. Chọn ngày & số khách
    4. Kiểm tra availability (API)
    5. Tính giá (API)
    6. Tạo booking (status = pending)
    7. Redirect sang VNPay
    8. Thanh toán
    9. VNPay callback
    10. Update booking (status = confirmed)
    11. Tạo payment record
    12. Gửi email xác nhận
    13. Tạo conversation (chat)
    ```

    ### **2. QUY TRÌNH ĐĂNG TIN:**
    ```
    1. Host đăng nhập
    2. Điền form 3 bước
    3. Upload ảnh
    4. Submit
    5. Listing tạo (status = pending)
    6. Admin duyệt
    7. Status → approved
    8. is_active → True
    9. Hiển thị trên trang chủ
    ```

    ### **3. QUY TRÌNH ĐÁNH GIÁ + AI:**
    ```
    1. Booking completed
    2. Guest viết review
    3. Upload ảnh/video (optional)
    4. Submit
    5. Kiểm tra spam:
    - Từ lặp > 50%?
    - Chữ hoa > 70%?
    - Độ dài < 10?
    6. AI ViSoBERT phân tích:
    - Tokenize text
    - Predict sentiment
    - Calculate confidence
    7. Lưu ReviewAnalysis:
    - sentiment (pos/neg/neu)
    - confidence
    8. Lưu ReviewClassification:
    - spam_status
    - spam_reason
    9. Hiển thị review + badge
    ```

    ### **4. QUY TRÌNH THANH TOÁN:**
    ```
    1. Calculate total price
    2. Create VNPay URL:
    - vnp_Amount
    - vnp_OrderInfo
    - vnp_ReturnUrl
    - HMAC-SHA512 signature
    3. Redirect to VNPay
    4. User pays
    5. VNPay return callback
    6. Verify signature
    7. Update booking & payment
    8. Send email
    ```

    ---

    ## 💡 TÍNH NĂNG NỔI BẬT

    ### **1. AI Sentiment Analysis:**
    - Model: 5CD-ViSoBERT (120K Vietnamese reviews)
    - Framework: PyTorch + Transformers
    - Tự động phân loại cảm xúc review
    - Phát hiện spam thông minh

    ### **2. Real-time Chat:**
    - Host ↔ Guest messaging
    - Auto-create conversation khi booking
    - Mark as read
    - Django signals

    ### **3. Payment Integration:**
    - VNPay gateway (sandbox)
    - HMAC-SHA512 security
    - Transaction tracking
    - Email confirmation

    ### **4. Interactive Maps:**
    - Leaflet.js + OpenStreetMap
    - Nominatim geocoding API
    - Auto address → coordinates
    - Beautiful markers

    ### **5. Email Automation:**
    - OTP verification
    - Booking confirmation
    - Complaint notifications
    - Password reset

    ---

    ## 📊 THỐNG KÊ HỆ THỐNG

    | Thành phần | Số lượng |
    |-----------|---------|
    | **Views** | 40+ |
    | **Models** | 15+ |
    | **Templates** | 50+ |
    | **URLs** | 35+ |
    | **APIs** | 7+ |
    | **Email templates** | 4+ |
    | **Static files** | 30+ (CSS/JS) |

    ---

    ## 🎨 GIAO DIỆN

    ### **Guest:**
    - Trang chủ: Featured listings + search
    - Kết quả tìm kiếm: Grid layout + filters
    - Chi tiết chỗ ở: Gallery + map + reviews
    - Booking: Form + price calculation
    - Profile: Tabs (Info / Trips / Reviews)

    ### **Host:**
    - Dashboard: My listings + bookings
    - Create listing: 3-step wizard
    - Manage listings: Table view

    ### **Admin:**
    - Jazzmin theme (màu nâu)
    - Dashboard: Stats cards
    - Revenue charts: Chart.js
    - CRUD cho tất cả models

    ---

    ## ✅ KẾT LUẬN

    **Homnest** là hệ thống full-stack hoàn chỉnh với:
    - ✅ **Frontend:** Bootstrap responsive + Interactive maps
    - ✅ **Backend:** Django MVC + MySQL
    - ✅ **AI:** Vietnamese sentiment analysis
    - ✅ **Payment:** VNPay integration
    - ✅ **Email:** Automated notifications
    - ✅ **Chat:** Real-time messaging
    - ✅ **Admin:** Powerful management panel

    Hệ thống đã implement **đầy đủ nghiệp vụ** của một nền tảng cho thuê chỗ ở thực tế, sẵn sàng deploy production.

    ---

    *Dự án đã hoàn thành tất cả chức năng cốt lõi của Airbnb + AI*

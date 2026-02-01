# BÁO CÁO CUỐI KÌ - DỰ ÁN HOMNEST
> **Outline PowerPoint - 10 Slides**

---

## SLIDE 1: TRANG BÌA 📋
```
HOMNEST - HỆ THỐNG ĐẶT PHÒNG VÀ QUẢN LÝ CHỖ Ở

Sinh viên thực hiện: [Tên của bạn]
Lớp: [Lớp]
GVHD: [Tên giảng viên]

Tháng 2/2026
```

---

## SLIDE 2: TỔNG QUAN DỰ ÁN 🎯

**Giới thiệu:**
- Nền tảng cho thuê chỗ ở trực tuyến (giống Airbnb)
- Kết nối Guest (khách thuê) và Host (chủ nhà)
- Tích hợp AI phân tích đánh giá + Thanh toán trực tuyến

**Mục tiêu:**
- ✅ Quản lý booking tự động
- ✅ Thanh toán VNPay an toàn
- ✅ AI phân tích cảm xúc review (tiếng Việt)
- ✅ Chat real-time giữa Host-Guest
- ✅ Admin quản lý toàn hệ thống

**3 nhóm người dùng:** Guest | Host | Admin

---

## SLIDE 3: CÔNG NGHỆ SỬ DỤNG 💻

### **Backend & Database:**
- **Django 6.0** - Web framework (MVC pattern)
- **MySQL 8.0** - Relational database (15+ tables)
- **Python 3.11** - Programming language

### **AI & Machine Learning:**
- **ViSoBERT** - Vietnamese sentiment analysis
- **PyTorch + Transformers** - Deep learning framework
- **120,000 reviews** - Training dataset

### **Frontend:**
- **Bootstrap 5.3** - Responsive UI framework
- **Leaflet.js 1.9.4** - Interactive maps
- **jQuery 3.7.1** - JavaScript library

### **Payment & Email:**
- **VNPay Gateway 2.1.0** - Online payment
- **Gmail SMTP** - Email automation (OTP, confirmation)

---

## SLIDE 4: CHỨC NĂNG GUEST (KHÁCH THUÊ) 🏠

**1. Tìm kiếm & Đặt phòng:**
- Tìm theo: Địa điểm, ngày, số khách
- Lọc: Giá, loại phòng, tiện nghi
- Xem chi tiết: Ảnh, mô tả, bản đồ, review
- Đặt phòng online

**2. Thanh toán VNPay:**
- Tự động tính giá (Giá cơ bản + Phí dịch vụ)
- Thanh toán qua VNPay Gateway
- Email xác nhận booking

**3. Đánh giá + AI:**
- Rating 1-5 sao + Nhận xét
- Upload ảnh/video
- **AI tự động phân loại:** Tích cực / Tiêu cực / Trung tính
- **Phát hiện spam** thông minh

**4. Chat & Khiếu nại:**
- Nhắn tin real-time với Host
- Gửi khiếu nại nếu có vấn đề

---

## SLIDE 5: CHỨC NĂNG HOST (CHỦ NHÀ) 🏡

**1. Đăng tin cho thuê (3 bước):**
- **Bước 1:** Loại chỗ ở, địa chỉ, số phòng
- **Bước 2:** Tiện nghi, upload ảnh (min 5 ảnh)
- **Bước 3:** Đặt giá, thời gian, mô tả

**2. Quản lý chỗ ở:**
- Xem/sửa listing
- Bật/tắt hiển thị
- Thống kê: Lượt xem, booking, doanh thu

**3. Quản lý booking:**
- Xem booking đến
- Thông tin khách
- Tổng tiền nhận

**4. Chat với Guest:**
- Hỗ trợ khách trước/trong/sau kỳ thuê

---

## SLIDE 6: CHỨC NĂNG ADMIN (QUẢN TRỊ) 👨‍💼

**1. Quản lý Users:**
- CRUD người dùng
- Phân quyền: Guest / Host / Admin

**2. Duyệt & Quản lý Listings:**
- Duyệt listing mới (Approve/Reject)
- Quản lý tất cả chỗ ở

**3. Quản lý Bookings & Payments:**
- Theo dõi tất cả booking
- Kiểm tra thanh toán
- Xử lý tranh chấp

**4. Thống kê doanh thu:** 📊
- Biểu đồ doanh thu theo tháng
- Top listings có doanh thu cao
- Tổng users, bookings, listings

**5. Quản lý Review & AI:**
- Xem kết quả phân tích AI
- Ẩn review spam

---

## SLIDE 7: NGHIỆP VỤ CHÍNH 🔄

### **1. Quy trình ĐẶT PHÒNG:**
```
Tìm kiếm → Chọn listing → Chọn ngày/khách 
→ Kiểm tra availability → Tính giá 
→ Thanh toán VNPay → Xác nhận booking 
→ Gửi email → Tạo chat
```

### **2. Quy trình ĐĂNG TIN:**
```
Điền form 3 bước → Upload ảnh → Submit 
→ Admin duyệt → Approve 
→ Hiển thị trang chủ
```

### **3. Quy trình ĐÁNH GIÁ + AI:**
```
Booking hoàn thành → Viết review 
→ Kiểm tra spam (từ lặp, chữ hoa) 
→ AI ViSoBERT phân tích cảm xúc 
→ Lưu kết quả (pos/neg/neu + confidence) 
→ Hiển thị review + badge
```

---

## SLIDE 8: TÍNH NĂNG NỔI BẬT ⭐

**1. AI Sentiment Analysis (Độc quyền):**
- Model: **5CD-ViSoBERT** (120K reviews tiếng Việt)
- Tự động phân loại cảm xúc review
- Phát hiện spam: Từ lặp > 50%, Chữ hoa > 70%

**2. Bản đồ tương tác:**
- Leaflet.js + OpenStreetMap
- Tự động geocoding địa chỉ → tọa độ
- Hiển thị vị trí chính xác

**3. Thanh toán VNPay:**
- Payment gateway uy tín
- Bảo mật HMAC-SHA512
- Transaction tracking đầy đủ

**4. Email tự động:**
- OTP đăng ký (6 số)
- Xác nhận booking
- Thông báo khiếu nại

**5. Chat real-time:**
- Django signals tự động tạo conversation
- Đánh dấu đã đọc
- Lịch sử chat đầy đủ

---

## SLIDE 9: KẾT QUẢ ĐẠT ĐƯỢC ✅

### **Về kỹ thuật:**
| Thành phần | Số lượng |
|-----------|---------|
| Views | 40+ |
| Models | 15+ |
| Templates | 50+ |
| URLs | 35+ |
| APIs | 7+ |

### **Về chức năng:**
- ✅ Full-stack application (Frontend + Backend)
- ✅ AI integration (ViSoBERT sentiment analysis)
- ✅ Payment gateway (VNPay)
- ✅ Real-time chat
- ✅ Email automation
- ✅ Admin dashboard với thống kê

### **Về giao diện:**
- ✅ Responsive design (Bootstrap 5)
- ✅ Interactive maps (Leaflet)
- ✅ Modern admin panel (Jazzmin)
- ✅ Chart.js visualization

---

## SLIDE 10: DEMO & KẾT LUẬN 🎬

### **Demo chức năng chính:**
1. 🔍 **Tìm kiếm** → Kết quả listing + map
2. 💳 **Đặt phòng** → Thanh toán VNPay → Email
3. ⭐ **Đánh giá** → AI phân tích → Hiển thị badge
4. 💬 **Chat** → Host ↔ Guest messaging
5. 📊 **Admin** → Dashboard thống kê

### **Kết luận:**
**Homnest** là hệ thống cho thuê chỗ ở **hoàn chỉnh**, có:
- ✅ Đầy đủ nghiệp vụ như Airbnb
- ✅ Tích hợp AI phân tích tiếng Việt (độc đáo)
- ✅ Thanh toán trực tuyến an toàn
- ✅ Giao diện đẹp, responsive
- ✅ Sẵn sàng deploy production

**Cảm ơn thầy/cô và các bạn đã lắng nghe!**

---

## 📝 GHI CHÚ CHO NGƯỜI TRÌNH BÀY

### **Slide 1-2:** (2 phút)
- Giới thiệu bản thân
- Nêu vấn đề: Khó khăn khi tìm chỗ ở online
- Giải pháp: Xây dựng nền tảng Homnest

### **Slide 3:** (1.5 phút)
- Nhấn mạnh: AI ViSoBERT (điểm độc đáo)
- Công nghệ hiện đại: Django 6.0, Bootstrap 5

### **Slide 4-6:** (4 phút)
- Chia theo 3 nhóm user
- Nêu rõ workflow chính
- Có thể demo ngắn

### **Slide 7:** (2 phút)
- Giải thích quy trình đặt phòng end-to-end
- Vẽ diagram trên bảng nếu cần

### **Slide 8:** (2 phút)
- **Trọng tâm:** AI sentiment analysis
- Show kết quả demo (screenshot)

### **Slide 9:** (1.5 phút)
- Số liệu thống kê
- Nhấn mạnh độ hoàn thiện

### **Slide 10:** (3 phút)
- Demo live nếu có
- Hoặc video demo 2-3 phút
- Q&A

**Tổng thời gian:** ~15-18 phút

---

## 💡 MẸO TRÌNH BÀY

1. **Chuẩn bị demo:**
   - Video demo 2-3 phút (đặt phòng → thanh toán → review)
   - Hoặc demo live (chuẩn bị data sẵn)

2. **Screenshot quan trọng:**
   - Trang chủ với listings
   - Chi tiết listing + map
   - Kết quả AI analysis review
   - Admin dashboard với chart

3. **Câu hỏi có thể gặp:**
   - **Q:** Tại sao chọn ViSoBERT?  
     **A:** Model pre-trained trên 120K review tiếng Việt, phù hợp cho bài toán sentiment analysis Việt Nam.
   
   - **Q:** VNPay sandbox hay production?  
     **A:** Hiện tại dùng sandbox, nhưng code đã sẵn sàng chuyển production.
   
   - **Q:** Xử lý concurrent booking như thế nào?  
     **A:** Có availability check + database constraints để tránh double booking.
   
   - **Q:** Deploy ở đâu?  
     **A:** Có thể deploy lên Railway, Render, hoặc VPS với MySQL.

4. **Điểm cộng:**
   - Nhấn mạnh **AI tiếng Việt** (độc đáo)
   - Show **code clean, có comment**
   - Đề cập **scalability** (có thể thêm features)

---

**Chúc bạn báo cáo thành công! 🎓**

# CÔNG NGHỆ SỬ DỤNG - DỰ ÁN HOMNEST

> **Hệ thống đặt phòng và quản lý chỗ ở**  
> **Cập nhật:** Tháng 2/2026

---

## 🔥 TOP CÔNG NGHỆ CHÍNH

### **1. DJANGO 6.0** ⭐⭐⭐⭐⭐
- **Vai trò:** Backend Framework chính
- **Chức năng:** 
  - ORM quản lý database
  - Authentication & Authorization
  - Admin panel tự động
  - Template engine
  - CSRF protection

### **2. MYSQL** ⭐⭐⭐⭐⭐
- **Vai trò:** Cơ sở dữ liệu
- **Driver:** mysqlclient 2.2.7
- **Charset:** utf8mb4 (hỗ trợ emoji + tiếng Việt)
- **Số bảng:** 15+ (Users, Listings, Bookings, Payments, Reviews...)

### **3. VISOBERT + PYTORCH** ⭐⭐⭐⭐⭐
- **Vai trò:** AI phân tích cảm xúc đánh giá
- **Model:** 5CD-AI/visobert-14gb-corpus
- **Framework:** Transformers 4.57.3 + PyTorch
- **Dữ liệu:** 120,000 Vietnamese reviews
- **Chức năng:** 
  - Phân loại: Tích cực / Tiêu cực / Trung tính
  - Phát hiện spam review

### **4. BOOTSTRAP 5.3** ⭐⭐⭐⭐
- **Vai trò:** CSS Framework
- **Chức năng:** Responsive UI, Components (Cards, Modals, Forms)

### **5. LEAFLET.JS 1.9.4** ⭐⭐⭐⭐
- **Vai trò:** Bản đồ tương tác
- **Tích hợp:** OpenStreetMap + Nominatim API
- **Chức năng:** Hiển thị vị trí chỗ ở, geocoding

### **6. VNPAY GATEWAY** ⭐⭐⭐⭐
- **Vai trò:** Cổng thanh toán
- **Version:** 2.1.0 (Sandbox)
- **Mã hóa:** HMAC-SHA512

### **7. GMAIL SMTP** ⭐⭐⭐⭐
- **Vai trò:** Email service
- **Chức năng:** OTP, xác nhận booking, password reset

### **8. JQUERY 3.7.1** ⭐⭐⭐
- **Vai trò:** JavaScript library
- **Chức năng:** DOM manipulation, AJAX

### **9. FONT AWESOME 7.0** ⭐⭐⭐
- **Vai trò:** Icon library
- **Số lượng:** 1000+ icons

### **10. PYTHON 3.11** ⭐⭐⭐⭐⭐
- **Vai trò:** Ngôn ngữ lập trình
- **Modules:** json, datetime, decimal, hashlib, re

---

## 📊 THỐNG KÊ

| Loại | Số lượng |
|------|---------|
| Python Packages | 60+ |
| Frontend Libraries | 5+ |
| AI Models | 1 (ViSoBERT) |
| External APIs | 3 (VNPay, Gmail, Nominatim) |
| Database Tables | 15+ |

---

## 🎯 TECH STACK SUMMARY

```
Backend:    Django 6.0 + Python 3.11 + MySQL
AI/ML:      PyTorch + Transformers + ViSoBERT
Frontend:   Bootstrap 5 + jQuery + Leaflet.js
Payment:    VNPay Gateway (HMAC-SHA512)
Email:      Gmail SMTP (TLS)
Maps:       OpenStreetMap + Nominatim API
Admin:      Django-Jazzmin 3.0.1
```

---

## ✨ TÍNH NĂNG NỔI BẬT

### **AI/Machine Learning:**
- Phân tích cảm xúc review tiếng Việt (ViSoBERT)
- Tự động phát hiện spam review
- Training data: 120K reviews

### **Payment Integration:**
- VNPay sandbox gateway
- Real payment flow
- HMAC-SHA512 security

### **Maps & Geolocation:**
- Interactive maps (Leaflet.js)
- Address ↔ Coordinates (Nominatim API)
- OpenStreetMap tiles

### **Security:**
- CSRF protection
- Django ORM (SQL injection prevention)
- Password hashing
- Email OTP verification

---

*Tất cả công nghệ đều được sử dụng rộng rãi trong thực tế*

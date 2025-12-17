from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import *

User = get_user_model()

# Create your views here.
def home(request):
    return render(request, 'app/home.html')

def login_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if action == 'login':
            # Xử lý đăng nhập
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Đăng nhập thành công! Xin chào {user.full_name}')
                return redirect('home')
            else:
                messages.error(request, 'Email hoặc mật khẩu không chính xác')
        
        elif action == 'register':
            # Xử lý đăng ký
            full_name = request.POST.get('name')
            
            # Kiểm tra dữ liệu
            if not email or not password or not full_name:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin')
                return redirect('login')
            
            # Kiểm tra email đã tồn tại
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email này đã được đăng ký')
                return redirect('login')
            
            # Kiểm tra username đã tồn tại
            if User.objects.filter(username=email).exists():
                messages.error(request, 'Username này đã tồn tại')
                return redirect('login')
            
            # Kiểm tra mật khẩu
            if len(password) < 6:
                messages.error(request, 'Mật khẩu phải có ít nhất 6 ký tự')
                return redirect('login')
            
            # Tạo user mới
            try:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=full_name
                )
                user.save()
                print(f"✅ User created: {user.username}, ID: {user.id}")
                messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập')
                return redirect('login')
            except Exception as e:
                print(f"❌ Registration error: {str(e)}")
                messages.error(request, f'Lỗi đăng ký: {str(e)}')
    
    return render(request, 'app/login.html')

def taobaidang(request):
    # Kiểm tra đăng nhập
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập trước')
        return redirect('login')
    return render(request, 'app/taobaidang.html')

def chitietnoio(request):
    """Render the detail page template created by the user."""
    return render(request, 'app/chitietnoio.html')

def buoc1(request):
    return render(request, 'app/buoc1.html')

def thietlapgia(request):
    return render(request, 'app/thietlapgia.html')

def giacuoituan(request):
    return render(request, 'app/giacuoituan.html')

def chiasett(request):
    return render(request, 'app/chiasett.html')

def loaichoo(request):
    return render(request, 'app/loaichoo.html')

def trungtamtrogiup(request):
    return render(request, 'app/trungtamtrogiup.html')

def datphong(request):
    return render(request, 'app/datphong.html')

def phuongthucthanhtoan(request):
    return render(request, 'app/phuongthucthanhtoan.html')

def chinhsachdieukhoan(request):
    return render(request, 'app/chinhsachdieukhoan.html')

def buoc2(request):
    return render(request, 'app/buoc2.html')

def duocuse(request):
    return render(request, 'app/duocuse.html')

def themanh(request):
    return render(request, 'app/themanh.html')

def thongtincb(request):
    return render(request, 'app/thongtincb.html')

def tiennghii(request):
    return render(request, 'app/tiennghii.html')

def tieude(request):
    return render(request, 'app/tieude.html')

def diachi(request):
    return render(request, 'app/diachi.html')

def buoc3(request):
    return render(request, 'app/buoc3.html')

def thietlapgia(request):
    return render(request, 'app/thietlapgia.html')


def logout_view(request):
    # Django's logout function - xóa session automatically
    logout(request)
    messages.success(request, 'Đăng xuất thành công')
    return redirect('home')


# from .models import Listing, Review
# from .sentiment import analyze_sentiment
#
# def room_detail(request, room_id):
#     room = Room.objects.get(id=room_id)
#     reviews = Review.objects.filter(room=room)
#
#     if request.method == "POST":
#         if not request.user.is_authenticated:
#             return redirect("login")
#
#         text = request.POST.get("review_text")
#         senti = analyze_sentiment(text)
#
#         Review.objects.create(
#             user=request.user,
#             room=room,
#             text=text,
#             sentiment=senti,
#         )
#
#         return redirect("room_detail", room_id=room_id)
#
#     return render(request, "app/room_detail.html", {
#         "room": room,
#         "reviews": reviews
#     })
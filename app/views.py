from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from .models import *

User = get_user_model()

# Create your views here.
def home(request):
    return render(request, 'app/components/home.html')

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
<<<<<<< HEAD
=======
                messages.success(request, f'Đăng nhập thành công! Xin chào {user.first_name}')
>>>>>>> 114ca0588b9949224b74be0f04f585fa570bc996
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
                    full_name=full_name,
                    role='guest'
                )
<<<<<<< HEAD
=======

                guest_group = Group.objects.get(name='guest')
                user.groups.add(guest_group)

                user.save()
>>>>>>> 114ca0588b9949224b74be0f04f585fa570bc996
                print(f"✅ User created: {user.username}, ID: {user.id}")
                messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập')
                return redirect('login')
            except Exception as e:
                print(f"Registration error: {str(e)}")
                messages.error(request, f'Lỗi đăng ký: {str(e)}')
    
    return render(request, 'app/components/login.html')

def logout_view(request):
    """Đăng xuất người dùng"""
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công')
    return redirect('login')

def taobaidang(request):
    # 1. Chưa đăng nhập
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập trước')
        return redirect('login')
<<<<<<< HEAD
    return render(request, 'app/host/taobaidang.html')
=======

    # 2. Đã đăng nhập nhưng KHÔNG phải host
    if not request.user.groups.filter(name='host').exists():
        messages.error(request, 'Bạn phải là Host để tạo bài đăng')
        return redirect('home')

    # 3. Là host → cho vào
    return render(request, 'app/taobaidang.html')
>>>>>>> 114ca0588b9949224b74be0f04f585fa570bc996




@login_required(login_url='login')
def become_host(request):
    user = request.user

    # Nếu đã là host rồi thì thôi
    if user.groups.filter(name='host').exists():
        return redirect('home')

    guest_group = Group.objects.get(name='guest')
    host_group = Group.objects.get(name='host')

    user.groups.remove(guest_group)
    user.groups.add(host_group)

    messages.success(request, 'Bạn đã trở thành Host 🎉')
    return redirect('home')






def chitietnoio(request):
    """Render the detail page template created by the user."""
    return render(request, 'app/guest/chitietnoio.html')

def buoc1(request):
    return render(request, 'app/host/buoc1.html')

def thietlapgia(request):
    return render(request, 'app/host/thietlapgia.html')

def giacuoituan(request):
    return render(request, 'app/host/giacuoituan.html')

def chiasett(request):
    return render(request, 'app/host/chiasett.html')

def loaichoo(request):
    return render(request, 'app/host/loaichoo.html')

def trungtamtrogiup(request):
    return render(request, 'app/guest/trungtamtrogiup.html')

def datphong(request):
    return render(request, 'app/guest/datphong.html')

def phuongthucthanhtoan(request):
    return render(request, 'app/guest/phuongthucthanhtoan.html')

def chinhsachdieukhoan(request):
    return render(request, 'app/guest/chinhsachdieukhoan.html')

def buoc2(request):
    return render(request, 'app/host/buoc2.html')

def duocuse(request):
    return render(request, 'app/host/duocuse.html')

def themanh(request):
    return render(request, 'app/host/themanh.html')

def thongtincb(request):
    return render(request, 'app/host/thongtincb.html')

def tiennghii(request):
    return render(request, 'app/host/tiennghii.html')

def tieude(request):
    return render(request, 'app/host/tieude.html')

def diachi(request):
    return render(request, 'app/host/diachi.html')

def buoc3(request):
    return render(request, 'app/host/buoc3.html')

def thietlapgia(request):
    return render(request, 'app/host/thietlapgia.html')


def profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập để xem hồ sơ')
        return redirect('login')
    return render(request, 'app/components/profile.html')


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
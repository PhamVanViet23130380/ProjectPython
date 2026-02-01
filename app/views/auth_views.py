from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils import timezone
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
import random
from django.conf import settings   


User = get_user_model()


def login_view(request):
    """
    - Login bình thường
    - Register → gửi OTP → verify OTP mới tạo user
    """

    if request.method == 'POST':
        action = request.POST.get('action')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # ======================
        # LOGIN
        # ======================
        if action == 'login':
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                # Phân quyền: Admin → /admin/, Guest → home
                if user.is_staff or user.is_superuser:
                    return redirect('/admin/')
                return redirect('home')
            messages.error(request, 'Email hoặc mật khẩu không chính xác')
            return redirect('login')

        # ======================
        # REGISTER (GỬI OTP)
        # ======================
        elif action == 'register':
            full_name = request.POST.get('name')

            if not full_name or not email or not password:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin')
                return redirect('login')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email đã được đăng ký')
                return redirect('login')

            if len(password) < 6:
                messages.error(request, 'Mật khẩu phải có ít nhất 6 ký tự')
                return redirect('login')

            # Sinh OTP
            otp = str(random.randint(100000, 999999))

            # Lưu tạm vào session
            request.session['register_data'] = {
                'full_name': full_name,
                'email': email,
                'password': password,
                'otp': otp,
                'created_at': timezone.now().isoformat()
            }

            # Gửi email OTP
            send_mail(
                subject='Mã OTP đăng ký tài khoản',
                message=f'Mã OTP của bạn là: {otp}',
                from_email=settings.EMAIL_HOST_USER,   
                recipient_list=[email],
                fail_silently=False
            )

            messages.success(request, 'OTP đã được gửi tới email. Vui lòng xác nhận.')
            return redirect('verify_otp')

    return render(request, 'app/auth_template/login.html')


def logout_view(request):
    """Log out current user and redirect to login."""
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công')
    return redirect('login')





def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # 1. Kiểm tra email có trong DB không
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'Email không tồn tại trong hệ thống')
            return redirect('forgot_password')

        # 2. Có email → gửi mail reset
        form = PasswordResetForm({'email': email})
        if form.is_valid():
            form.save(
                request=request,
                email_template_name='registration/password_reset_email.html',
            )
            messages.success(
                request,
                'Hướng dẫn đặt lại mật khẩu đã được gửi. Vui lòng kiểm tra email.'
            )
        else:
            messages.error(request, 'Có lỗi xảy ra, vui lòng thử lại.')

        return redirect('forgot_password')

    return render(request, 'app/auth_template/forgot-password.html')


def verify_otp(request):
    data = request.session.get('register_data')

    if not data:
        messages.error(request, 'Phiên đăng ký đã hết hạn')
        return redirect('login')

    if request.method == 'POST':
        input_otp = request.POST.get('otp')

        if input_otp == data['otp']:
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['password']
            )

            if hasattr(user, 'full_name'):
                user.full_name = data['full_name']

            user.save()
            del request.session['register_data']

            messages.success(request, 'Đăng ký thành công! Mời đăng nhập.')
            return redirect('login')

        messages.error(request, 'OTP không đúng')

    return render(request, 'app/auth_template/verify_otp.html')


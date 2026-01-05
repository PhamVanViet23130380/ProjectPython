from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils import timezone
from django.contrib.auth.forms import PasswordResetForm

User = get_user_model()


def login_view(request):
    """Handle login and lightweight register actions.

    Renders the refactored template at `app/auth_template/login.html`.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        email = request.POST.get('email') or request.POST.get('username')
        password = request.POST.get('password')

        if action == 'login':
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            messages.error(request, 'Email hoặc mật khẩu không chính xác')

        elif action == 'register':
            full_name = request.POST.get('name') or request.POST.get('fullname')

            if not email or not password or not full_name:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin')
                return redirect('login')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email này đã được đăng ký')
                return redirect('login')

            if User.objects.filter(username=email).exists():
                messages.error(request, 'Username này đã tồn tại')
                return redirect('login')

            if len(password) < 6:
                messages.error(request, 'Mật khẩu phải có ít nhất 6 ký tự')
                return redirect('login')

            try:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                )
                # optional fields if your custom user supports them
                if hasattr(user, 'full_name'):
                    user.full_name = full_name
                if hasattr(user, 'role'):
                    try:
                        user.role = 'USER'
                    except Exception:
                        pass
                if hasattr(user, 'registered_time'):
                    user.registered_time = timezone.now()
                user.save()
                messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập')
                return redirect('login')
            except Exception as exc:
                messages.error(request, f'Lỗi đăng ký: {exc}')

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

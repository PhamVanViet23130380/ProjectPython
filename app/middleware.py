from django.shortcuts import redirect


class AdminRedirectMiddleware:
    """
    Middleware chặn admin (is_staff/is_superuser) truy cập trang user.
    Admin chỉ được phép vào /admin/ và các URL liên quan.
    """
    
    # Các URL prefix mà admin được phép truy cập
    ALLOWED_PREFIXES = [
        '/admin/',
        '/admin-api/',
        '/static/',
        '/media/',
        '/logout/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Kiểm tra nếu user đã đăng nhập và là admin
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            path = request.path
            
            # Cho phép truy cập các URL trong whitelist
            allowed = any(path.startswith(prefix) for prefix in self.ALLOWED_PREFIXES)
            
            if not allowed:
                # Redirect admin về trang admin
                return redirect('/admin/')
        
        response = self.get_response(request)
        return response

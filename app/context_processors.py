# app/context_processors.py

def is_host_context(request):
    """
    Context processor để kiểm tra user có phải là host không.
    User là host nếu có ít nhất 1 listing.
    """
    if request.user.is_authenticated:
        from app.models import Listing
        user_is_host = Listing.objects.filter(host=request.user).exists()
        return {'is_host': user_is_host}
    return {'is_host': False}

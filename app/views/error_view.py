from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)


def error_404(request, exception=None):
    """Custom 404 handler that renders the project's 404 template."""
    try:
        return render(request, 'app/error/404.html', status=404)
    except Exception:
        logger.exception('Rendering 404 failed')
        # fallback plain response
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound('Page not found')


def error_500(request):
    """Custom 500 handler that renders the project's 500 template."""
    try:
        return render(request, 'app/error/500.html', status=500)
    except Exception:
        logger.exception('Rendering 500 failed')
        from django.http import HttpResponseServerError
        return HttpResponseServerError('Server error')


def error_403(request, exception=None):
    """Custom 403 handler (permission denied)."""
    try:
        return render(request, 'app/error/403.html', status=403)
    except Exception:
        logger.exception('Rendering 403 failed')
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('Forbidden')

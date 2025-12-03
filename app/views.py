from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'app/home.html')

def login_view(request):
    return render(request, 'app/login.html')

def taobaidang(request):
    return render(request, 'app/taobaidang.html')

def chitietnoio(request):
    """Render the detail page template created by the user."""
    return render(request, 'app/chitietnoio.html')
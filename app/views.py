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

def buoc1(request):
    return render(request, 'app/buoc1.html')

def loaichoo(request):
    return render(request, 'app/loaichoo.html')

def trungtamtrogiup(request):
    return render(request, 'app/trungtamtrogiup.html')

def datphong(request):
    return render(request, 'app/datphong.html')

def timhosthotrop(request):
    return render(request, 'app/timhosthotrop.html')

def phuongthucthanhtoan(request):
    return render(request, 'app/phuongthucthanhtoan.html')

def chinhsachdieukhoản(request):
    return render(request, 'app/chinhsachdieukhoan.html')
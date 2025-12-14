from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
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
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse  # 이거 추가

def home(request):  # 간단한 홈 뷰
    return HttpResponse("Welcome to CareEat!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', home),  # 루트 경로에 대한 뷰 추가
]
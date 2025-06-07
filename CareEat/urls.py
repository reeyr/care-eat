from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from accounts.views import login_redirect
from django.contrib.auth.views import LogoutView

def home(request):  # 간단한 홈 뷰
    return HttpResponse("Welcome to CareEat!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', login_redirect, name='login_redirect'),  # 로그인 후 첫 경로
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),  # 로그아웃 경로
    path('home/', home, name='home'),  # 홈 페이지
    path('accounts/', include('accounts.urls')),  # 회원정보 등록/수정

    # API 경로
    path('api/diet/', include('diet.urls')),
    path('api/food/', include('food.urls')),
]
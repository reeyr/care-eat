from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from accounts.views import login_redirect, home
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),  # 회원정보 등록/수정
    path('', login_redirect, name='login_redirect'),  # 로그인 후 첫 경로
    path('logout/', LogoutView.as_view(next_page='/accounts/login/'), name='logout'),  # 로그아웃 경로
    path('main/', home, name='home'),  # 홈 페이지
      

    # API 경로
    path('api/diet/', include('diet.urls')),
    path('api/food/', include('food.urls')),
]
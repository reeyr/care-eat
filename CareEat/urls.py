
"""
URL configuration for CareEat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from accounts.views import login_redirect
from django.contrib.auth.views import LogoutView

def home(request):
    return HttpResponse("Welcome to CareEat!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/diet/', include('diet.urls')),
    path('api/food/', include('food.urls')),
    path('accounts/', include('allauth.urls')),
    path('', login_redirect, name='login_redirect'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('home/', home, name='home'),
    path('accounts/', include('accounts.urls')),
]

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse  # 이거 추가
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
]


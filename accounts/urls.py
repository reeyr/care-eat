app_name = 'accounts'
from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('login-redirect/', views.login_redirect, name='login_redirect'),
    path('login/', TemplateView.as_view(template_name='accounts/Login.html'), name='custom_login'),
    path('register_profile/', views.register_profile, name='profile_register'), # 회원정보 등록
    path('profile/edit/', views.edit_profile, name='edit_profile'), # 회원정보 수정
    path('delete/', views.delete_account, name='delete_account'), # 회원 탈퇴
    path('mypage/', views.mypage, name='mypage'),
    path('search/', views.search_view, name='search'),
    path('meal_add/', views.meal_add_view, name='meal_add'),
    path('meal-edit/', views.meal_edit_view, name='meal_edit'),
    path('main/', views.home, name='home'),

    
]
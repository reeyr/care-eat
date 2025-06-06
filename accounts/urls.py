from django.urls import path
from . import views

urlpatterns = [
    path('profile/register/', views.register_profile, name='profile_register'), # 회원정보 등록
    path('profile/edit/', views.edit_profile, name='edit_profile'), # 회원정보 수정
    path('delete/', views.delete_account, name='delete_account'), # 회원 탈퇴
]
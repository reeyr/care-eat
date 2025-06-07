from django.shortcuts import render, redirect
from .forms import UserProfileForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# 로그인 후 프로필 존재 여부 확인해서 리다이렉트
def login_redirect(request):
    if not request.user.is_authenticated:
        return redirect('account_login')  # allauth 기본 로그인 페이지

    try:
        profile = request.user.userprofile
        return redirect('home')  # 홈 페이지로 이동
    except UserProfile.DoesNotExist:
        return redirect('profile_register')  # 회원정보 입력 페이지로 이동

# 회원정보 등록(첫 로그인 시)
def register_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('home')
    else:
        form = UserProfileForm()
    return render(request, 'accounts/register_profile.html', {'form': form})

# 회원정보 수정(마이페이지)
def edit_profile(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

# 회원 탈퇴
@login_required
def delete_account(request):
    user = request.user
    user.delete() # 유저 삭제
    logout(request) # 로그아웃 처리
    return redirect('/')

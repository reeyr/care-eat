from django.shortcuts import render, redirect
from .forms import UserProfileForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import UserProfile 
from django.contrib import messages


def home(request):
    return render(request, 'accounts/main.html')

# 로그인 후 프로필 존재 여부 확인해서 리다이렉트
def login_redirect(request):
    if not request.user.is_authenticated:
        return redirect('account_login')  # allauth 기본 로그인 페이지

    try:
        profile = request.user.userprofile
        return redirect('home')  # 홈 페이지로 이동
    except UserProfile.DoesNotExist:
        return redirect('accounts:profile_register')  # 회원정보 입력 페이지로 이동

# 회원정보 등록(첫 로그인 시)
def register_profile(request):
    user = request.user

    
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "회원정보가 성공적으로 등록되었습니다!")
            return redirect('home')
        else:
            messages.error(request, "입력 정보를 다시 확인해주세요.")
    else:
        form = UserProfileForm()
    return render(request, 'accounts/register_profile.html', {'form': form})

def mypage(request):
    return render(request, 'accounts/mypage.html')

# 회원정보 수정(마이페이지)
@login_required
def edit_profile(request):
    user = request.user

    # UserProfile 객체 가져오기 (없으면 새로 생성 or 404 처리)
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        # 프로필이 없으면 새로 생성 (필요에 따라)
        profile = UserProfile.objects.create(user=user, gender='M', age=0, height=0, weight=0)

    if request.method == 'POST':
        # 폼에서 넘어온 값으로 업데이트
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        height = request.POST.get('height')
        weight = request.POST.get('weight')

        # 유효성 검사 추가 가능
        profile.gender = gender
        profile.age = int(age)
        profile.height = float(height)
        profile.weight = float(weight)
        profile.save()

        return redirect('/accounts/mypage/')  # 성공하면 홈으로 이동

    # GET 요청 시 기존 값 템플릿에 넘겨주기
    context = {
        'gender': profile.gender,
        'age': profile.age,
        'height': profile.height,
        'weight': profile.weight,
    }
    return render(request, 'accounts/edit_profile.html', context)

def search_view(request):
    meal = request.GET.get('meal')
    return render(request, 'accounts/search.html', {'meal': meal})

def meal_add(request):
    return render(request, 'accounts/meal_add.html')

def meal_add_view(request):
    return render(request, 'accounts/meal_add.html')

def meal_edit_view(request):
    return render(request, 'accounts/meal_add.html') 

    
# 회원 탈퇴
@login_required
def delete_account(request):
    user = request.user
    user.delete() # 유저 삭제
    logout(request) # 로그아웃 처리
    return redirect('account_login')
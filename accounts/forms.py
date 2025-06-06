from django import forms
from .models import UserProfile

# 회원정보 입력 폼
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['gender', 'age', 'height', 'weight']
        widgets = {
            'gender': forms.RadioSelect,
        }
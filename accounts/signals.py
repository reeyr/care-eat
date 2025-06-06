from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

# 회원 가입 후 자동으로 프로필 생성 확인
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # 새 유저 생성 시 profile은 만들지 않음 (입력 폼에서 받게 함)
        pass
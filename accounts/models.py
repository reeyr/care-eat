from django.contrib.auth.models import User
from django.db import models

# 유저 프로필 모델
class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.IntegerField(verbose_name='나이')
    height = models.FloatField(verbose_name='키 (cm)')
    weight = models.FloatField(verbose_name='몸무게 (kg)')

    def __str__(self):
        return f"{self.user.username}'s profile"

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from food.models import Food
#from userProfile.models import

class Diet(models.Model):

    TIME_CHOICES = [
        ('breakfast', '아침'),
        ('lunch', '점심'),
        ('dinner', '저녁'),
        ('snack', '간식'),
    ]

    #역참조 이름 설정
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='diets')
    food = models.ForeignKey(Food,
                             on_delete=models.CASCADE,
                             related_name='diet_records')
    time_slot = models.CharField(max_length=10, choices=TIME_CHOICES)

    #섭취량
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    date = models.DateField()  #날짜 필드
    memo = models.CharField(max_length=200, blank=True, null=True)  #메모 필드
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'time_slot']
        verbose_name = '식단 기록'
        verbose_name_plural = '식단 기록들'

    @property
    def total_kcal(self):
        #총 칼로리를 계산하는 프로퍼티-데이터 중복저장하지 않고 필요할 때 계산
        #음식 칼로리나 수량이 바뀌면 자동 반영
        return float(self.food.kcal_per_unit * self.quantity)

    def save(self, *args, **kwargs):
        #저장 시 날짜가 없으면 오늘 날짜로 설정
        #데이터 필드로 언제 먹었는지 구분 (일별 칼로리 통계 계산시 사용)
        if not self.date:
            from django.utils import timezone
            self.date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.get_time_slot_display()} - {self.food.name} ({self.date})"


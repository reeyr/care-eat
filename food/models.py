from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
#다른도메인 참조하기

class Food(models.Model):
    name = models.CharField(max_length=100, unique=True) #음식이름-중복방지
    kcal = models.DecimalField(max_digits=8,
                               decimal_places=2,
                               validators=[MinValueValidator(Decimal('0.01'))]
                               ) #단위당 칼로리
    units = models.CharField(max_length=20) #단위(g, 개, ml 등)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True) #음식 설명
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = '음식'
        verbose_name_plural = '음식들'

    def __str__(self):
        return f"{self.name} ({self.kcal_per_unit} kcal/{self.units})"

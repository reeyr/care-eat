from django.urls import path, include
from .views import (
    DietCreateAPIView, #식단등록
    DietListAPIView,  #전체조회
    DietDetailAPIView, #하루 식단 조회/수정/삭제
    DailyCaloriesAPIView #하루 섭취 칼로리 통계
)

urlpatterns = [
    path('create/', DietCreateAPIView.as_view(), name='diet-create'),
    path('', DietListAPIView.as_view(), name='diet-list'),
    path('<int:pk>/', DietDetailAPIView.as_view(), name='diet-detail'),
    path('calories/', DailyCaloriesAPIView.as_view(), name='diet-calories'),

]

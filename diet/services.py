from .models import Diet
from food.models import Food
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q
from typing import Optional
from datetime import date, timedelta

#식단 등록
def create_diet(user, food_id: int, time_slot: str, quantity: float,
                date: Optional[date] = None, memo: str = "") -> Diet:
    try:
        food = Food.objects.get(id=food_id)
    except Food.DoesNotExist:
        raise ValueError("해당 음식이 존재하지 않습니다.")

    if date is None:
        date = timezone.now().date()

    if quantity <= 0:
        raise ValueError("수량은 0보다 커야 합니다.")

    diet = Diet.objects.create(
        user=user,
        food=food,
        time_slot=time_slot,
        quantity=quantity,
        date=date,
        memo=memo
    )
    return diet

#식단 기록 수정 - None이 아닌 값만 업데이트
def update_diet(diet: Diet, food_id: Optional[int] = None,
                time_slot: Optional[str] = None, quantity: Optional[float] = None,
                date: Optional[date] = None, memo: Optional[str] = None) -> Diet:


    #food_id가 제공된 경우에만 음식 변경 가능
    if food_id is not None:
        try:
            food = Food.objects.get(id=food_id)
            diet.food = food
        except Food.DoesNotExist:
            raise ValueError("해당 음식이 존재하지 않습니다.")

    #각 필드를 개별적으로 업데이트
    if time_slot is not None:
        diet.time_slot = time_slot

    if quantity is not None:
        if quantity <= 0:
            raise ValueError("수량은 0보다 커야 합니다.")
        diet.quantity = quantity

    if date is not None:
        diet.date = date

    if memo is not None:
        diet.memo = memo

    diet.save()
    return diet

#일일 칼로리 통계 조회
def get_daily_calories(user, target_date: date) -> dict:

    diets = Diet.objects.filter(user=user, date=target_date).select_related('food')

    #시간대별 칼로리 계산
    calories_by_time = {
        'breakfast': 0,
        'lunch': 0,
        'dinner': 0,
        'snack': 0
    }

    total_calories = 0
    entries = []

    for diet in diets:
        kcal = diet.total_kcal
        total_calories += kcal
        calories_by_time[diet.time_slot] += kcal

        entries.append({
            "id": diet.id,
            "food_name": diet.food.name,
            "food_unit": diet.food.unit,
            "quantity": float(diet.quantity),
            "kcal_per_unit": float(diet.food.kcal_per_unit),
            "total_kcal": kcal,
            "time_slot": diet.time_slot,
            "time_slot_display": diet.get_time_slot_display(),
            "memo": diet.memo
        })

    return {
        "date": str(target_date),
        "total_calories": total_calories,
        "breakfast_calories": calories_by_time['breakfast'],
        "lunch_calories": calories_by_time['lunch'],
        "dinner_calories": calories_by_time['dinner'],
        "snack_calories": calories_by_time['snack'],
        "meal_count": len(entries),
        "entries": entries
    }

#주간 칼로리 통계 조회
def get_weekly_calories(user, start_date: date) -> dict:
    end_date = start_date + timedelta(days=6)

    diets = Diet.objects.filter(
        user=user,
        date__range=[start_date, end_date]
    ).select_related('food')

    #날짜별로 그룹화
    daily_data = {}
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        daily_data[current_date] = {
            'date': current_date,
            'total_calories': 0,
            'breakfast_calories': 0,
            'lunch_calories': 0,
            'dinner_calories': 0,
            'snack_calories': 0,
            'meal_count': 0
        }

    #데이터 집계
    for diet in diets:
        day_data = daily_data[diet.date]
        kcal = diet.total_kcal
        day_data['total_calories'] += kcal
        day_data[f'{diet.time_slot}_calories'] += kcal
        day_data['meal_count'] += 1

    week_total = sum(day['total_calories'] for day in daily_data.values())
    daily_average = week_total / 7 if week_total > 0 else 0

    return {
        "week_start": str(start_date),
        "week_end": str(end_date),
        "daily_data": list(daily_data.values()),
        "week_total": week_total,
        "daily_average": round(daily_average, 2)
    }

#월간 칼로리 통계 조회
def get_monthly_calories(user, year: int, month: int) -> dict:
    from calendar import monthrange

    #해당 월의 첫째 날과 마지막 날
    _, last_day = monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    diets = Diet.objects.filter(
        user=user,
        date__range=[start_date, end_date]
    ).select_related('food')

    #일별 칼로리 합계
    daily_calories = {}
    total_calories = 0

    for diet in diets:
        day = diet.date.day
        if day not in daily_calories:
            daily_calories[day] = 0

        kcal = diet.total_kcal
        daily_calories[day] += kcal
        total_calories += kcal

    #평균 계산 (기록이 있는 날만)
    recorded_days = len(daily_calories)
    daily_average = total_calories / recorded_days if recorded_days > 0 else 0

    return {
        "year": year,
        "month": month,
        "total_calories": total_calories,
        "daily_average": round(daily_average, 2),
        "recorded_days": recorded_days,
        "total_days": last_day,
        "daily_calories": daily_calories
    }

#식단 삭제
def delete_diet(user, diet_id: int) -> bool:
    try:
        diet = Diet.objects.get(id=diet_id, user=user)
        diet.delete()
        return True
    except Diet.DoesNotExist:
        raise ValueError("해당 식단 기록이 존재하지 않거나 권한이 없습니다.")

#사용자의 식단 기록 조회 (필터링 가능)
def get_user_diets(user, date_from: Optional[date] = None,
                   date_to: Optional[date] = None, time_slot: Optional[str] = None) -> list:
    queryset = Diet.objects.filter(user=user).select_related('food')

    if date_from:
        queryset = queryset.filter(date__gte=date_from)

    if date_to:
        queryset = queryset.filter(date__lte=date_to)

    if time_slot:
        queryset = queryset.filter(time_slot=time_slot)

    return queryset.order_by('-date', 'time_slot')
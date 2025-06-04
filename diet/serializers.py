from rest_framework import serializers
from .models import Diet
from food.models import Food
from django.contrib.auth.models import User
from food.serializers import FoodSerializer, FoodSimpleSerializer

#전체 정보 조회
class DietSerializer(serializers.ModelSerializer):
    """조회용 - 모든 정보 포함"""
    food = FoodSerializer(read_only=True)  #음식 정보를 객체 형태로 응답
    total_kcal = serializers.ReadOnlyField()
    username = serializers.CharField(source='user.username', read_only=True)
    time_slot_display = serializers.CharField(source='get_time_slot_display', read_only=True)

    class Meta:
        model = Diet
        fields = [
            'id', 'user', 'username', 'food', 'time_slot', 'time_slot_display',
            'quantity', 'date', 'memo', 'total_kcal',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'username', 'food', 'time_slot_display',
                            'total_kcal', 'created_at', 'updated_at']


class DietCreateUpdateSerializer(serializers.ModelSerializer):
    """생성/수정용 - food는 ID로 받음"""
    food_id = serializers.IntegerField(write_only=True)  # 음식 ID로 받기
    total_kcal = serializers.ReadOnlyField()

    class Meta:
        model = Diet
        fields = ['food_id', 'time_slot', 'quantity', 'date', 'memo', 'total_kcal']

    def validate_food_id(self, value):
        """음식 존재 여부 확인"""
        try:
            from food.models import Food
            food = Food.objects.get(id=value)
            return value
        except Food.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 음식입니다.")

    def validate_quantity(self, value):
        """수량 유효성 검증"""
        if value <= 0:
            raise serializers.ValidationError("수량은 0보다 커야 합니다.")
        return value

    def create(self, validated_data):
        """생성 시 food_id를 food 객체로 변경"""
        from food.models import Food
        food_id = validated_data.pop('food_id')
        food = Food.objects.get(id=food_id)
        validated_data['food'] = food
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """수정 시 food_id를 food 객체로 변경"""
        if 'food_id' in validated_data:
            from food.models import Food
            food_id = validated_data.pop('food_id')
            food = Food.objects.get(id=food_id)
            validated_data['food'] = food
        return super().update(instance, validated_data)


class DietListSerializer(serializers.ModelSerializer):
    """리스트용 - 간단한 음식 정보만"""
    food = FoodSimpleSerializer(read_only=True)
    total_kcal = serializers.ReadOnlyField()
    time_slot_display = serializers.CharField(source='get_time_slot_display', read_only=True)

    class Meta:
        model = Diet
        fields = [
            'id', 'food', 'time_slot', 'time_slot_display',
            'quantity', 'date', 'total_kcal', 'created_at'
        ]


# 통계용 serializer들
class DailyCalorieSerializer(serializers.Serializer):
    """일별 칼로리 통계"""
    date = serializers.DateField()
    total_calories = serializers.FloatField()
    breakfast_calories = serializers.FloatField(default=0)
    lunch_calories = serializers.FloatField(default=0)
    dinner_calories = serializers.FloatField(default=0)
    snack_calories = serializers.FloatField(default=0)
    meal_count = serializers.IntegerField()

class WeeklyCalorieSerializer(serializers.Serializer):
    """주간 칼로리 통계"""
    week_start = serializers.DateField()
    week_end = serializers.DateField()
    daily_data = DailyCalorieSerializer(many=True)
    week_total = serializers.FloatField()
    daily_average = serializers.FloatField()

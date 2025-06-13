from rest_framework import serializers
from .models import Food

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['id', 'name', 'kcal', 'unit', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

        def validate_name(self, value):
            # 음식 이름 중복 체크
            instance = self.instance
            if Food.objects.filter(name=value).exclude(id=instance.id if instance else None).exists():
                raise serializers.ValidationError('이미 존재하는 음식 이름입니다.')
            return value

        def validate_kcal_per_unit(self, value):
            # 칼로리 값 유효성 검증
            if value <= 0:
                raise serializers.ValidationError('칼로리는 0보다 커야 합니다.')
            return value

class FoodSimpleSerializer(serializers.ModelSerializer):
    #간단한 음식 정보만
    class Meta:
        model = Food
        fields = ['id', 'name', 'kcal', 'unit']
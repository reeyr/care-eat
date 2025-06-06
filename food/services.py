import os
import requests
import xml.etree.ElementTree as ET
from typing import Optional, List
from django.db.models import Q, Count
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from .models import Food

API_URL = "https://api.data.go.kr/openapi/tn_pubr_public_nutri_food_info_api"
API_KEY = os.getenv('FOOD_API_KEY', "HqkZncN4ctZWUQO6gcx3NBpyVq%2B%2Fu23Q7Z2JEmI2XP2DlsxuI%2FwFuaKnTMQCjoK6LcJebFvHhYzc9CDtmLCqyg%3D%3D")

#음식생성
def create_food(name: str, kcal_per_unit: float, unit: str,
                description: str = "") -> Food:
    #중복 이름 체크
    if Food.objects.filter(name__iexact=name).exists():
        raise ValueError("이미 존재하는 음식 이름입니다.")

    #유효성 검증
    if kcal_per_unit <= 0:
        raise ValueError("칼로리는 0보다 커야 합니다.")

    if not name.strip():
        raise ValueError("음식 이름은 필수입니다.")

    if not unit.strip():
        raise ValueError("단위는 필수입니다.")

    try:
        return Food.objects.create(
            name=name.strip(),
            kcal_per_unit=kcal_per_unit,
            unit=unit.strip(),
            description=description.strip()
        )
    except IntegrityError:
        raise ValueError("음식 생성 중 오류가 발생했습니다.")

#모든 음식 조회 (검색 기능 포함)
def get_all_foods(search: Optional[str] = None) -> List[Food]:
    queryset = Food.objects.all()

    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    return list(queryset.order_by('name'))

#ID로 음식 조회
def get_food_by_id(food_id: int) -> Food:
    try:
        return Food.objects.get(id=food_id)
    except Food.DoesNotExist:
        raise ValueError("해당 음식이 존재하지 않습니다.")

#음식 정보 수정
def update_food(food_id: int, name: Optional[str] = None,
                kcal_per_unit: Optional[float] = None,
                unit: Optional[str] = None,
                description: Optional[str] = None) -> Food:
    food = get_food_by_id(food_id)

    #이름 중복 체크 (자기 자신 제외)
    if name and name != food.name:
        if Food.objects.filter(name__iexact=name).exclude(id=food_id).exists():
            raise ValueError("이미 존재하는 음식 이름입니다.")
        food.name = name.strip()

    #칼로리 유효성 검증
    if kcal_per_unit is not None:
        if kcal_per_unit <= 0:
            raise ValueError("칼로리는 0보다 커야 합니다.")
        food.kcal_per_unit = kcal_per_unit

    #단위 유효성 검증
    if unit is not None:
        if not unit.strip():
            raise ValueError("단위는 필수입니다.")
        food.unit = unit.strip()

    #설명 업데이트
    if description is not None:
        food.description = description.strip()

    try:
        food.save()
        return food
    except IntegrityError:
        raise ValueError("음식 수정 중 오류가 발생했습니다.")

#음식 삭제 (식단 기록이 있으면 삭제 불가)
def delete_food(food_id: int) -> bool:
    food = get_food_by_id(food_id)

    #관련된 식단 기록이 있는지 확인
    if hasattr(food, 'diet_records') and food.diet_records.exists():
        raise ValueError("이 음식과 연관된 식단 기록이 있어 삭제할 수 없습니다.")

    food.delete()
    return True

#인기음식 조회(식단기록 횟수 기준)
def get_popular_foods(limit: int = 10) -> List[Food]:
    return list(
        Food.objects.annotate(
        usage_count=Count('diet_records')
        ).filter(usage_count__gt=0).order_by('-usage_count')[:limit]
    )

def foodApi(food_name: str):
    """외부 API 연동하여 음식 정보 가져오기 - JSON 버전"""
    try:
        existing = Food.objects.filter(name__icontains=food_name).first()
        if existing:
            return existing, False

        params = {
            'serviceKey': API_KEY,
            'desc_kor': food_name,
            'numOfRows': 1,
            'pageNo': 1,
            'type': 'json'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        print("📦 API 요청 파라미터:", params)

        response = requests.get(API_URL, params=params, headers=headers, timeout=10)

        print("📡 응답 상태 코드:", response.status_code)

        if response.status_code != 200:
            raise ValueError(f"API 요청 실패: {response.status_code}")

        data = response.json()
        print("🧾 JSON 응답 데이터:", data)

        items = data.get('body', {}).get('items', [])
        if not items:
            raise ValueError("해당 식품 정보를 찾을 수 없습니다.")

        item = items[0]

        name = item.get("DESC_KOR") or item.get("FOOD_NM_KR") or item.get("NAME")
        kcal = item.get("NUTR_CONT1") or item.get("AMT_NUM1")
        serving = item.get("SERVING_WT") or item.get("SERVING_SIZE")

        if not name or not kcal:
            raise ValueError("필수 정보 누락")

        carbs = item.get("NUTR_CONT2") or "0"
        protein = item.get("NUTR_CONT3") or "0"
        fat = item.get("NUTR_CONT4") or "0"


        try:
            kcal_float = float(str(kcal).replace(",", ""))
        except ValueError:
            raise ValueError(f"칼로리 값이 숫자가 아닙니다: {kcal}")

        food = Food.objects.create(
            name=name.strip(),
            kcal_per_unit=kcal_float,
            unit='100g',
            description=f"{serving}g 기준" if serving else "API에서 가져온 정보"
        )

        print(f"새로운 음식 생성: {food.name} ({food.kcal_per_unit}kcal/{food.unit})")
        return {
            "name": food.name,
            "kcal_per_unit": food.kcal_per_unit,
            "unit": food.unit,
            "carbohydrate": carbs,
            "protein": protein,
            "fat": fat,
            "description": food.description
        }, True

    except requests.exceptions.Timeout:
        raise ValueError("API 요청 시간 초과")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"API 요청 오류: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ValueError(f"예상치 못한 오류 발생: {str(e)}")
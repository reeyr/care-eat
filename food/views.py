import traceback

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from .models import Food
import os
from django.conf import settings
import urllib.parse
from .serializers import FoodSerializer, FoodSimpleSerializer
from .services import (
    get_all_foods,
    create_food,
    get_food_by_id,
    update_food,
    delete_food,
    get_popular_foods
)


class FoodListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    #음식 목록 조회
    def get(self, request):
        search = request.GET.get('search', '')
        foods = get_all_foods(search=search if search else None)
        serializer = FoodSerializer(foods, many=True)
        return Response(serializer.data)

    #음식 생성
    def post(self, request):
        serializer = FoodSerializer(data=request.data)
        if serializer.is_valid():
            try:
                food = create_food(
                    name=serializer.validated_data['name'],
                    kcal=serializer.validated_data['kcal'],
                    unit=serializer.validated_data['unit'],
                    description=serializer.validated_data.get('description', '')
                )
                return Response(FoodSerializer(food).data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {'error': f'음식 생성 중 오류가 발생했습니다: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodDetailView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    #음식 상세 조회
    def get(self, request, pk):
        try:
            food = get_food_by_id(pk)
            serializer = FoodSerializer(food)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    #음식 정보 수정
    def put(self, request, pk):
        serializer = FoodSerializer(data=request.data)
        if serializer.is_valid():
            try:
                food = update_food(
                    food_id=pk,
                    name=serializer.validated_data.get('name'),
                    kcal=serializer.validated_data.get('kcal'),
                    unit=serializer.validated_data.get('unit'),
                    description=serializer.validated_data.get('description')
                )
                return Response(FoodSerializer(food).data)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {'error': f'음식 수정 중 오류가 발생했습니다: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #음식 정보 부분 수정
    def patch(self, request, pk):
        try:
            food = get_food_by_id(pk)
            serializer = FoodSerializer(food, data=request.data, partial=True)
            if serializer.is_valid():
                updated_food = update_food(
                    food_id=pk,
                    name=serializer.validated_data.get('name'),
                    kcal=serializer.validated_data.get('kcal'),
                    unit=serializer.validated_data.get('unit'),
                    description=serializer.validated_data.get('description')
                )
                return Response(FoodSerializer(updated_food).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    #음식삭제
    def delete(self, request, pk):
        try:
            delete_food(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PopularFoodsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    #음식 인기 조회
    def get(self, request):

        limit = int(request.GET.get('limit', 10))
        foods = get_popular_foods(limit=limit)
        serializer = FoodSimpleSerializer(foods, many=True)
        return Response(serializer.data)

#API 연결용 뷰
class ExternalFoodImportView(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.GET.get('query')
        if not query:
            return Response({'error': '검색어가 필요합니다.'}, status=400)

        api_key = os.getenv('FOOD_API_KEY')
        base_url = settings.FOOD_API_URL

        print("✅ settings에서 불러온 FOOD_API_URL:", settings.FOOD_API_URL)
        print("🌐 사용할 BASE URL:", base_url)

        params = {
            'serviceKey': urllib.parse.quote_plus(os.getenv("FOOD_API_KEY")),
            'desc_kor': query,
            'pageNo': 1,
            'numOfRows': 10,
            'type': 'json'
        }
        try:
            response = requests.get(
                base_url,
                params=params,
                timeout=30
            )

            print("🌐 응답 상태 코드:", response.status_code)
            print("📄 응답 본문 내용 (일부):", response.text[:300])

            if response.status_code != 200:
                return Response({'error': f'API 요청 실패: {response.status_code}'}, status=500)

            data = response.json()
            items = data.get('body', {}).get('items', [])
            if not items:
                return Response({
                    'error': '해당 식품 정보를 찾을 수 없습니다.'
                }, status=404)

            # For simplicity, take the first item
            item = items[0]

            name = item.get('DESC_KOR')
            kcal = item.get('NUTR_CONT1')
            serving = item.get('SERVING_WT')
            protein = item.get('NUTR_CONT2')
            fat = item.get('NUTR_CONT3')
            carbs = item.get('NUTR_CONT4')

            try:
                food, created = Food.objects.get_or_create(
                    name=name,
                    defaults={
                        'kcal': float(kcal) if kcal else 0,
                        'unit': serving or '100g',
                        'description': '외부 API에서 가져온 식품 정보'
                    }
                )

                return Response({
                    'success': True,
                    'created': created,
                    'data': {
                        'id': food.id,
                        'name': name,
                        'kcal': float(kcal) if kcal else 0,
                        'serving': serving,
                        'protein': float(protein) if protein else 0,
                        'fat': float(fat) if fat else 0,
                        'carbohydrates': float(carbs) if carbs else 0,
                    }
                })

            except Exception as db_error:
                return Response({
                    'success': True,
                    'created': False,
                    'warning': f'DB 저장 실패: {str(db_error)}',
                    'data': {
                        'name': name,
                        'kcal': float(kcal) if kcal else 0,
                        'serving': serving,
                        'protein': float(protein) if protein else 0,
                        'fat': float(fat) if fat else 0,
                        'carbohydrates': float(carbs) if carbs else 0,
                    }
                })

        except ValueError as e:
            return Response({
                'error': f'JSON 파싱 에러: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except requests.exceptions.RequestException as e:
            return Response({
                'error': f'네트워크 요청 에러: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            traceback.print_exc()
            return Response({
                'error': f'알 수 없는 오류: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

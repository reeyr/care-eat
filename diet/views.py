# diet/views.py
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date, datetime
from .serializers import (
    DietCreateUpdateSerializer,
    DietSerializer,
    DietListSerializer,
    DailyCalorieSerializer
)
from .models import Diet
from .services import create_diet, update_diet, get_daily_calories
from rest_framework import permissions


#식단등록
class DietCreateAPIView(APIView):
    #로그인 기능 구현되면 여기에 인증토큰사용
    #로그인-토큰 발급
    #permission_classes = [permissions.IsAuthenticated] #로그인 인증해야 접근 가능
    permission_classes = [AllowAny] #인증 없이 접근 허용(테스트용)


    def post(self, request):
        serializer = DietCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                diet = create_diet(
                    user=request.user,
                    food_id=serializer.validated_data['food_id'],
                    time_slot=serializer.validated_data['time_slot'],
                    quantity=serializer.validated_data['quantity'],
                    date=serializer.validated_data.get('date'),
                    memo=serializer.validated_data.get('memo', "")
                )
                return Response(DietSerializer(diet).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': f'식단 생성 중 오류가 발생했습니다: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#사용자 식단 전체 조회
class DietListAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

    def get(self, request):
        #쿼리 파라미터로 필터링
        if not request.user or not request.user.is_authenticated:
            return Response([], status=status.HTTP_200_OK)

        queryset = Diet.objects.filter(user=request.user)

        #날짜 필터링
        date_param = request.GET.get('date')
        if date_param:
            try:
                filter_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                queryset = queryset.filter(date=filter_date)
            except ValueError:
                return Response(
                    {'error': '날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        #시간대 필터링
        time_slot = request.GET.get('time_slot')
        if time_slot:
            queryset = queryset.filter(time_slot=time_slot)

        #정렬
        queryset = queryset.order_by('-date', 'time_slot')

        serializer = DietListSerializer(queryset, many=True)
        return Response(serializer.data)

#식단 상세 조회/수정/삭제
class DietDetailAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk, user):
        return get_object_or_404(Diet, pk=pk, user=user)

    #조회
    def get(self, request, pk):
        diet = self.get_object(pk, request.user)
        serializer = DietSerializer(diet)
        return Response(serializer.data)

    #수정
    def put(self, request, pk):
        diet = self.get_object(pk, request.user)
        serializer = DietCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                updated_diet = update_diet(
                    diet=diet,
                    food_id=serializer.validated_data.get('food_id'),
                    time_slot=serializer.validated_data.get('time_slot'),
                    quantity=serializer.validated_data.get('quantity'),
                    date=serializer.validated_data.get('date'),
                    memo=serializer.validated_data.get('memo')
                )
                return Response(DietSerializer(updated_diet).data)
            except Exception as e:
                return Response(
                    {'error': f'식단 수정 중 오류가 발생했습니다: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #삭제
    def delete(self, request, pk):
        diet = self.get_object(pk, request.user)
        diet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#통계 관련 뷰
class DailyCaloriesAPIView(APIView):
    #permission_classes = [permissions.IsAuthenticated]
    permission_classes = [AllowAny]

    #실제서비스용
    # def get(self, request):
    #     date_param = request.GET.get('date', str(date.today()))
    #     try:
    #         target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
    #     except ValueError:
    #         return Response(
    #             {'error': '날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #
    #     daily_data = get_daily_calories(request.user, target_date)
    #     return Response(daily_data)

    #테스트용
    def get(selfself, request):
        date_param = request.GET.get('date', str(date.today()))
        try:
            target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error':'날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        daily_data = get_daily_calories(request.user, target_date)
        return Response(daily_data)


from django.urls import path
from .views import ExternalFoodImportView, FoodListCreateView

urlpatterns = [
    path('foods/', FoodListCreateView.as_view(), name='food-list-create'),
    path('import-external/', ExternalFoodImportView.as_view(), name='import-external-food'),
]
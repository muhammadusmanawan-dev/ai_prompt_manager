from django.urls import path
from .views import AIGenerateView, AIImproveView, AIUsageView

urlpatterns = [
    path('improve/', AIImproveView.as_view(), name='ai_improve'),
    path('generate/', AIGenerateView.as_view(), name='ai_generate'),
    path('usage/', AIUsageView.as_view(), name='ai_usage'),
]
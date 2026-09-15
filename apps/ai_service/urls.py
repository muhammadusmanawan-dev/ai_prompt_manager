from django.urls import path
from .views import AIImproveView, AIGenerateView

urlpatterns = [
    path('improve/', AIImproveView.as_view(), name='ai_improve'),
    path('generate/', AIGenerateView.as_view(), name='ai_generate'),
]
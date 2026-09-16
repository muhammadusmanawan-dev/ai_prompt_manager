from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, PromptViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'prompts', PromptViewSet, basename='prompt')

urlpatterns = router.urls
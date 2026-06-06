from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, QuestionViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('questions',  QuestionViewSet, basename='question')

urlpatterns = [path('', include(router.urls))]

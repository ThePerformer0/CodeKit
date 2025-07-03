from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TechnologyViewSet, ProjectTemplateViewSet, ProjectGenerateAPIView

router = DefaultRouter()
router.register(r'technologies', TechnologyViewSet)
router.register(r'project-templates', ProjectTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-project/', ProjectGenerateAPIView.as_view(), name='generate_project'),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import api_views

router = DefaultRouter()
router.register(r'projects', api_views.ProjectViewSet)
router.register(r'tasks', api_views.TaskViewSet)
router.register(r'teams', api_views.TeamViewSet)
router.register(r'users', api_views.UserViewSet)

urlpatterns = [
    # Endpoints d'authentification JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Endpoints spécifiques à l'application
    path('login/', api_views.login_api, name='api_login'),
    path('profile/', api_views.user_profile_api, name='api_profile'),
    path('comments/', api_views.CommentListView.as_view(), name='api_comments'),
    path('', include(router.urls)),
]
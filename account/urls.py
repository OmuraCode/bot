from django.urls import path, include
from account import views
from dj_rest_auth.views import LoginView, LogoutView
from rest_framework.routers import DefaultRouter

from account import views

router = DefaultRouter()
router.register('', views.UserViewSet)

urlpatterns = [
    path('register/', views.UserRegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', views.CustomLogoutView.as_view()),
    path('', include(router.urls)),
]
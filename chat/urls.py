from django.urls import path
from .views import ChatbotView, train_model, select_model

urlpatterns = [
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
    path('train_model/', train_model, name='train_model'),
    path('select_model/', select_model, name='select_model')
]

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import ChatbotViewSet, train_model
# router = DefaultRouter()
# router.register(r'chatbot', ChatbotViewSet, basename='chatbot')
#
# urlpatterns = [
#     path('', include(router.urls)),
#     path('train_model/', train_model, name='train_model'),
# ]

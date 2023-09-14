from django.urls import path
from .views import ChatbotView, train_model

urlpatterns = [
    path('chatbot/', ChatbotView.as_view()),
    path('train_model/', train_model, name='train_model'),
]
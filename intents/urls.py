from django.urls import path
from .views import IntentCreateView, IntentDetailView, IntentListView

urlpatterns = [
    path('create-intent/', IntentCreateView.as_view(), name='create-intent'),
    path('intents/', IntentListView.as_view(), name='intent-list'),
    path('intents/<int:pk>/', IntentDetailView.as_view(), name='intent-detail'),
]
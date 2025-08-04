from django.urls import path
from .views import AdminLogListCreateView

urlpatterns = [
    path('', AdminLogListCreateView.as_view()),
]

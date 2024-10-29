from django.urls import path
from .views import register, CustomAuthToken, logout

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('logout/', logout, name='logout'),
]

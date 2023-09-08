from django.urls import path
from . import views

urlpatterns = [
    path('',  views.getRoutes),
    path('rooms/', views.getRooms),
    path('rooms/<str:pk>', views.getRoom),
    path('users/', views.getUsers),
    path('users/<str:pk>', views.getUser),
]

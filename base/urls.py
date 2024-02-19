from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('', views.home, name="home"),
    path('pinned/<str:pk>/', views.pinRoom, name="pinit"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('change-password/', views.changePassword, name="change-password"),

    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('subscribe-room/<str:pk>/', views.subscribeRoom, name="subscribe-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
    path('upvote-message/<str:pk>/', views.upvoteMessage, name="upvote-message"),

    path('update-user/', views.updateUser, name="update-user"),
    path('delete-user/', views.deleteUser, name="delete-user"),

    path('topics/', views.topicsPage, name="topics"),
    path('activity/', views.activityPage, name="activity"),
    
    path('error/', views.fallback, name="fallback"),
    path('new-class/', views.newClass, name="new-class"),
    path('email-response/<str:pk>/<str:password>/', views.mailResponse, name="mail-response"),
]

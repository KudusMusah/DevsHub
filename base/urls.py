from django.urls import path
from .views import (
    home,
    rooms,
    update_room,
    create_room,
    delete_room,
    delete_message,
    login_view,
    logout_view,
    register,
    exit_room,
    profile_view,
    created_rooms
)

urlpatterns = [
    path("", home, name="home"),
    path("rooms/<str:pk>/", rooms, name="room"),
    path("update-room/<str:pk>/", update_room, name="edit-room"),
    path("create-room/", create_room, name="create-room"),
    path("created-rooms/", created_rooms, name="created-rooms"),
    path("delete-room/<str:pk>/", delete_room, name="delete-room"),
    path("delete-message/<str:pk>/", delete_message, name="delete-message"),
    path("login/", login_view, name="login"),
    path("register/", register, name="register"),
    path("logout/", logout_view, name="logout"),
    path('room/<str:pk>/exit/', exit_room, name="exit-room"),
    path('profile/<str:pk>/', profile_view, name="profile"),
]

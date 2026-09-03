from django.urls import path
from archive import views

urlpatterns = [
    path('', views.song_list, name='home'),
    path('songs/', views.song_list, name='song_list'),
    path('songs/<int:pk>/', views.song_detail, name='song_detail'),
    path('artists/', views.artist_list, name='artist_list'),
    path('artists/<int:pk>/', views.artist_detail, name='artist_detail'),
    path('search/', views.search, name='search'),
]

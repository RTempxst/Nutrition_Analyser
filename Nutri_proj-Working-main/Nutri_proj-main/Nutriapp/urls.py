from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_ingredient, name='search_ingredient'),
    path('clear/', views.clear_list, name='clear_list'),
    path('about/', views.about, name='Nutriapp-about'),
    
]

from django.urls import path
from django.views.generic.base import View
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/',views.SearchView.as_view(), name='search'),

]
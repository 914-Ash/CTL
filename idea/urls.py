from django.urls import path
from django.views.generic.base import View
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('tag/<int:id>', views.TagView.as_view(),name='tag'),
    path('search/',views.SearchView.as_view(), name='search'),

]
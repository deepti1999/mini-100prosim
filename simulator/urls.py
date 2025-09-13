from django.urls import path
from . import views

app_name = 'simulator'

urlpatterns = [
    path('', views.home, name='home'),       # Page 1
    path('results/', views.results, name='results'),  # Page 2
]

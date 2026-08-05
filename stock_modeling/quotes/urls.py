from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name="home"),
	path('about.html', views.about, name="about"),
	path('model.html', views.model, name="model"),
	path('model-status/<str:slug>/', views.model_status, name="model_status"),
]
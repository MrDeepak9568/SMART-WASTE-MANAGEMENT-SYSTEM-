from django.conf import settings
from django.contrib import admin
from django.urls import path
from Accounts import views
from django.conf.urls.static import static

urlpatterns = [
    path('user_login',views.user_login,name="user_login"),
    path('suser_login',views.suser_login,name="suser_login"),
    path('logout',views.logout,name="logout"),
    path('profile/', views.profile, name='profile'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
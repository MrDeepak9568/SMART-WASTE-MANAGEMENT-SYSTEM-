from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Services import views

urlpatterns = [
    path('report/', views.report, name='report'),
    path('rewards/', views.rewards, name='rewards'),
    path('collect/', views.collect, name='collect'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('mark-collected/<int:report_id>/', views.mark_collected, name='mark_collected'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sessions', views.sessions, name='sessions'),
    path('logged_in', views.login_view, name='login_view'),
    path('services/', views.services, name='service'),
    path('sessions/<int:session_id>/', views.sessions, name='sessions'),
    path('auth/', views.auth, name='auth'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('gen_report/', views.report_gen, name='report_gen'),

]

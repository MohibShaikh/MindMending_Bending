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
    path('register_patient/', views.register_patient, name='register_patient'),
    path('training/', views.training, name='training'),
    path('book/<int:therapist_id>/', views.booking, name='book'),
    # path('book_session/<int:session_id>/', views.book_session, name='book_session'),
    # path('paypal-return/', views.paypal_return, name='paypal-return'),
    # path('paypal-cancel/', views.paypal_cancel, name='paypal-cancel'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sessions', views.sessions, name='sessions'),
    path('logged_in', views.login_view, name='login_view'),
    path('services/', views.services, name='service'),
    path('sessions/<int:session_id>/', views.sessions, name='sessions'),
    path('unviewed-feedbacks/', views.unviewed_feedbacks, name='unviewed_feedbacks'),
    path('auth/', views.auth, name='auth'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('gen_report/', views.report_gen, name='report_gen'),
    path('register_patient/', views.register_patient, name='register_patient'),
    path('training/', views.training, name='training'),
    path('book/<int:therapist_id>/', views.booking, name='book'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
    path('view-report/', views.view_report, name='view_report'),
    path('therapist/unviewed-feedbacks/', views.therapist_unviewed_feedbacks, name='therapist_unviewed_feedbacks'),
    path('therapist/provide-feedback/<int:feedback_id>/', views.provide_feedback, name='provide_feedback'),
    path('mark-notifications-as-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    # path('feedback-form/', views.feedback_view, name='feedback_form'),
    path('feedback-view/<int:feedback_id>/', views.feedback_view, name='feedback_view'),
    path('cancel_booking/<int:booked_session_id>/', views.cancel_booking, name='cancel_booking'),
    # path('submit-feedback/<int:session_id>/', views.submit_feedback, name='submit_feedback'),
    # path('book_session/<int:session_id>/', views.book_session, name='book_session'),
    # path('paypal-return/', views.paypal_return, name='paypal-return'),
    # path('paypal-cancel/', views.paypal_cancel, name='paypal-cancel'),
]

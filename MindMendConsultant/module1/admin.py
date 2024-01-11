from django.contrib import admin
from .models import Patient, Therapist, Sessions, Feedback, BookedSession, ComplainForm, \
    CustomerReport, Notification

admin.site.register(Patient)
admin.site.register(Therapist)
admin.site.register(Sessions)
admin.site.register(Feedback)
admin.site.register(BookedSession)
admin.site.register(ComplainForm)
admin.site.register(CustomerReport)
admin.site.register(Notification)

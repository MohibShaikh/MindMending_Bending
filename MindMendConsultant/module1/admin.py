from django.contrib import admin
from .models import Patient, Therapist, Sessions, PatientFeedback, TherapistFeedback, BookedSession, ComplainForm, \
    CustomerReport

admin.site.register(Patient)
admin.site.register(Therapist)
admin.site.register(Sessions)
admin.site.register(PatientFeedback)
admin.site.register(TherapistFeedback)
admin.site.register(BookedSession)
admin.site.register(ComplainForm)
admin.site.register(CustomerReport)

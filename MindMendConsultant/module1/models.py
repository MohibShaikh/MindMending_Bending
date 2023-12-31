# models.py
from django.contrib.auth.models import User
from django.db import models


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    dob = models.CharField(max_length=3)
    phone_no = models.CharField(max_length=20)
    age = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.user.username}"


class Therapist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    phone_no = models.CharField(max_length=15)
    specialization = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"


class Sessions(models.Model):
    therapist = models.ManyToManyField(Therapist, blank=True)
    session_id = models.AutoField(primary_key=True)
    facility = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)

    def __str__(self):
        return f'{self.facility}'


class PatientFeedback(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    answer1 = models.IntegerField()
    answer2 = models.IntegerField()
    answer3 = models.IntegerField()
    answer4 = models.IntegerField()
    answer5 = models.IntegerField()


class TherapistFeedback(models.Model):
    patient_feedback = models.OneToOneField(PatientFeedback, on_delete=models.CASCADE)
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    description = models.TextField()


class BookedSession(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    session_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class ComplainForm(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    phone = models.CharField(max_length=15)


class CustomerReport(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    assessment_observation = models.TextField()

    def generate_report(self):
        # Logic to generate a report based on feedback and therapist's descriptions
        # Return the generated report
        pass

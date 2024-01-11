from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

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
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=1000.0)

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"


class Sessions(models.Model):
    therapist = models.ManyToManyField(Therapist, blank=True)
    session_id = models.AutoField(primary_key=True)
    facility = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    default_datetime = models.DateTimeField(default="2006-10-25 14:30:59")


    def __str__(self):
        return f'{self.facility}'

class BookedSession(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    session_type = models.CharField(max_length=50, default="Regular", blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    selected_time = models.DateTimeField(max_length=10, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='nayapay')


class Feedback(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    booked_session = models.ForeignKey(BookedSession, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    answer1 = models.TextField()
    answer2 = models.TextField()
    answer3 = models.TextField()
    answer4 = models.TextField()
    answer5 = models.TextField()
    is_viewed = models.BooleanField(default=False)
    created_at=models.DateTimeField(default=timezone.now)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class ComplainForm(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    phone = models.CharField(max_length=15)


class CustomerReport(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def generate_report(self):
        # Logic to generate a report based on feedback and therapist's descriptions
        # Return the generated report
        pass

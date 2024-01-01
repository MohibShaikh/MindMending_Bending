# views.py
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

from module1.models import Patient, Therapist, Sessions, BookedSession


# Create your views here.
def index(request):
    sessions = Sessions.objects.all()  # Fetch all sessions from the database
    return render(request, 'index.html', {'sessions': sessions})


def training(request):
    return render(request, 'training.html')

def book_session(request, session_id):
    if request.method == 'POST':
        therapist_id = request.POST.get('therapist_id')
        session_id = request.POST.get('session_id')
        payment_method = request.POST.get('payment_method')
        date_time = request.POST.get('date_time')

        therapist = Therapist.objects.get(id=therapist_id)
        session = Sessions.objects.get(session_id=session_id)

        # Create a BookedSession instance
        booked_session = BookedSession.objects.create(
            therapist=therapist,
            patient=request.user.patient,
            session_type=session.facility,
            amount=session.price,
            date_time=date_time
        )

        # Send notification to therapist
        # Implement your notification logic here, e.g., sending an email or using a messaging system

        messages.success(request, 'Session booked successfully.')
        return redirect('index')

    return render(request, 'book_session.html', {'session_id': session_id})  # Handle other cases as needed

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful.')
    return redirect('index')

def sessions(request, session_id):
    # Retrieve the session
    session = get_object_or_404(Sessions, session_id=session_id)

    # Retrieve therapists related to the session
    therapists = Therapist.objects.filter(sessions=session)

    context = {
        'session': session,
        'therapists': therapists,
    }
    return render(request, 'sessions.html', context)


def services(request):
    facilit = Sessions.objects.all()
    context = {
        'facilit': facilit,
    }
    return render(request, 'service.html', context)


def training(request):
    return render(request, 'training.html')


def report_gen(request):
    return render(request, 'gen_report.html')


def Booking(request):
    return render(request, 'Book.html')


# def auth(request):
#     return render(request,"auth.html")

def auth(request):
    if request.method == 'POST':
        # Your authentication logic here
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')

            # Redirect to the home page or a default page
            return redirect('services')

        else:
            messages.error(request, 'Invalid login credentials.')

    return render(request, 'auth.html')
def profile(request):
    user = request.user  # Get the logged-in user
    context = {'user': user}
    return render(request, 'patient_profile.html', context)

@login_required(login_url='auth')
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = authenticate(request, username=username, password=password)
        print(user)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')

            # Check if the user is a therapist
            if hasattr(user, 'therapist'):
                therapist = user.therapist
                context = {
                    'therapist': therapist,
                    'is_patient': False,
                }
                return render(request, 'userprofile.html', context)

            # Check if the user is a patient
            elif hasattr(user, 'patient'):
                patient = user.patient
                context = {
                    'patient': patient,
                    'is_patient': True,
                }
                return render(request, 'patient_profile.html', context)

        else:
            messages.error(request, 'Invalid login credentials.')

    return redirect('/')

def register_patient(request):
    if request.method == 'POST':
        # Extract form data
        username = request.POST['username']
        email = request.POST['email']
        gender = request.POST['gender']
        dob_str = request.POST['dob']
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        age = request.POST['age']
        phone_no = request.POST['phone_no']
        print(f'Extracted Date: {dob}')
        password = request.POST['password']


        # Create a User
        user = User.objects.create_user(username=username, email=email, password=password)
        print(user.username,user.email,user.password)
        # Create a Patient
        patient = Patient(user=user, gender=gender, dob=dob, age=age, phone_no=phone_no)
        print(patient.gender,patient.dob)
        patient.save()

        # Redirect to a success page or login page
        return redirect('service')

    return render(request, 'auth.html')
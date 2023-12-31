# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from module1.models import Patient, Therapist, Sessions


# Create your views here.
def index(request):
    sessions = Sessions.objects.all()  # Fetch all sessions from the database
    return render(request, 'index.html', {'sessions': sessions})




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
    return render(request, 'userprofile.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username,password)
        user = authenticate(request, username=username, password=password)
        print(user)

        if user is not None:
            login(request, user)
            # for key, value in request.session.items():
            #     print(f"{key}: {value}")
            messages.success(request, 'Login successful.')
            therapist = Therapist.objects.get(user=user)
            # print(therapist)
            # for key, value in request.session.items():
            #     print(f"{key}: {value}")
            context = {
                'therapist': therapist,
            }
            return render(request, 'userprofile.html', context)
        else:
            messages.error(request, 'Invalid login credentials.')

    return redirect('/')

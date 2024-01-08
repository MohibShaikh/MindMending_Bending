# views.py
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from module1.models import Patient, Therapist, Sessions, BookedSession, Notification
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse


# Create your views here.
def index(request):
    sessions = Sessions.objects.all()  # Fetch all sessions from the database
    return render(request, 'index.html', {'sessions': sessions})


def training(request):
    return render(request, 'training.html')


# def book_session(request, session_id):
#     if request.method == 'POST':
#         therapist_id = request.POST.get('therapist_id')
#         session_id = request.POST.get('session_id')
#         payment_method = request.POST.get('payment_method')
#         date_time = request.POST.get('date_time')
#
#         therapist = Therapist.objects.get(id=therapist_id)
#         session = Sessions.objects.get(session_id=session_id)
#
#         # Create a BookedSession instance
#         booked_session = BookedSession.objects.create(
#             therapist=therapist,
#             patient=request.user.patient,
#             session_type=session.facility,
#             amount=session.price,
#             date_time=date_time
#         )
#
#         # Send notification to therapist
#         # Implement your notification logic here, e.g., sending an email or using a messaging system
#
#         messages.success(request, 'Session booked successfully.')
#         return redirect('index')
#
#     return render(request, 'book_session.html', {'session_id': session_id})  # Handle other cases as needed
#
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


# Working one
# def booking(request, therapist_id):
#     therapist = Therapist.objects.get(pk=therapist_id)
#     session_id = request.GET.get('session_id')
#
#
#     if request.method == 'POST':
#         # Process the form data and save the booked session
#         patient = request.user.patient  # Assuming the logged-in user is a patient
#         session_type = request.POST.get('session_type')
#         amount = 9000
#         selected_time_str = request.POST.get('time_slot')
#         selected_time = datetime.strptime(selected_time_str, "%Y-%m-%dT%H:%M")
#
#         print(selected_time)
#         payment_method = request.POST.get('payment_method', 'nayapay')
#
#         booked_sessions = BookedSession.objects.create(
#             therapist=therapist,
#             patient=patient,
#             session_type=session_type,
#             amount=amount,
#             selected_time=selected_time,
#             payment_method=payment_method
#         )
#
#         # Update therapist earnings
#         therapist.earnings += booked_sessions.amount
#         therapist.save()
#
#         return render(request, 'patient_profile.html', {'booked_sessions': booked_sessions})
#
#     return render(request, 'Book.html', {'therapist': therapist})
def booking(request, therapist_id):
    therapist = Therapist.objects.get(pk=therapist_id)
    session_id = request.GET.get('session_id')
    session_type = request.POST.get('session_type')

    if request.method == 'POST':
        # Process the form data and save the booked session
        patient = request.user.patient  # Assuming the logged-in user is a patient
        amount = 9000
        selected_time_str = request.POST.get('time_slot')
        selected_time = datetime.strptime(selected_time_str, "%Y-%m-%dT%H:%M")
        # print(selected_time)
        payment_method = request.POST.get('payment_method', 'nayapay')
        # Create a notification for the therapist
        therapist_notification = Notification.objects.create(
            user=therapist.user,
            content=f"New session booked by patient {patient.user.username},/n on {selected_time}."
        )

        # Create a notification for the patient (optional)
        patient_notification = Notification.objects.create(
            user=patient.user,
            content=f"Session booked with therapist {therapist.user.username},/n on {selected_time}."
        )

        booked_session = BookedSession.objects.create(
            therapist=therapist,
            patient=patient,
            session_type=session_type,
            amount=amount,
            selected_time=selected_time,
            payment_method=payment_method
        )

        # Update therapist earnings
        therapist.earnings += booked_session.amount
        therapist.save()

        # Send email notifications
        send_email_to_therapist(therapist, booked_session, selected_time_str=selected_time_str)
        send_email_to_patient(patient, booked_session, selected_time_str=selected_time_str)

        return render(request, 'patient_profile.html', {'booked_sessions': [booked_session]})
    next_three_days = [timezone.now() + timezone.timedelta(days=i) for i in range(3)]
    context = {
        'therapist': therapist,
        'next_three_days': next_three_days,
        'time_slots': ['10:00 AM', '02:00 PM', '05:00 PM', '08:00 PM'],
        'session_type': session_type,

    }


    return render(request, 'Book.html', context)


def send_email_to_therapist(therapist, booked_session, selected_time_str):
    subject = 'New Session Booked'
    selected_time = selected_time = datetime.strptime(selected_time_str, "%Y-%m-%dT%H:%M")
    message = f"Dear {therapist.user.username},\n\n" \
              f"Patient: {booked_session.patient.user.username}\n" \
              f"Date: {booked_session.selected_time.strftime('%d-%b-%Y')}\n" \
              f"Timing: {booked_session.selected_time.strftime('%H:%M')} - {selected_time.strftime('%H:%M')}"

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = therapist.user.email

    send_mail(subject, message, from_email, [to_email])


def mark_notifications_as_read(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        # Mark all notifications as read for the current user
        Notification.objects.filter(user=user).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


#
def send_email_to_patient(patient, booked_session, selected_time_str):
    selected_time = selected_time = datetime.strptime(selected_time_str, "%Y-%m-%dT%H:%M")
    subject = 'Session Booked Confirmation'
    message = f"Dear {patient.user.username},\n\nYour session has been booked successfully.\n\nTherapist: {booked_session.therapist.user.username}\nDate: {selected_time.strftime('%d-%b-%Y')}\n\nTiming: {booked_session.selected_time.strftime('%H:%M')} - {selected_time.strftime('%H:%M')}\n\nThank you for choosing our service!"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = patient.user.email

    send_mail(subject, message, from_email, [to_email])


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
    user = request.user
    recent_notifications = Notification.objects.filter(user=user, is_read=False)[:10]
    patient = user.patient
    print(patient)
    booked_sessions = patient.bookedsession_set.all()
    print(user)
    # for i in recent_notifications:
    #     print(i.content)
    context = {'user': user, 'booked_sessions': booked_sessions, 'notif': recent_notifications}
    print(context)
    return render(request, 'patient_profile.html', context)


@csrf_exempt
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
                recent_notifications = Notification.objects.filter(user=user, is_read=False)[:3]
                booked_sessions = BookedSession.objects.filter(therapist=therapist)
                context = {
                    'therapist': therapist,
                    'booked_sessions': booked_sessions,
                    'is_patient': False,
                    'notif': recent_notifications,
                }
                return render(request, 'userprofile.html', context)

            # Check if the user is a patient
            elif hasattr(user, 'patient'):
                patient = user.patient
                recent_notifications = Notification.objects.filter(user=user, is_read=False)[:10]
                booked_sessions = BookedSession.objects.filter(patient=patient)
                context = {
                    'patient': patient,
                    'is_patient': True,
                    'notif': recent_notifications,
                    'booked_sessions': booked_sessions,
                }
                return render(request, 'patient_profile.html', context)

        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('auth/')
    return redirect('auth/')


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
        message = 'We thank you for choosing us. Welcome onboard to your ever improvement journey oof mental health.'
        send_mail('MindMend Consultant', message, [email], fail_silently=False)
        # Create a User
        user = User.objects.create_user(username=username, email=email, password=password)
        print(user.username, user.email, user.password)
        # Create a Patient
        patient = Patient(user=user, gender=gender, dob=dob, age=age, phone_no=phone_no)
        print(patient.gender, patient.dob)
        patient.save()

        # Redirect to a success page or login page
        return redirect('service')

    return render(request, 'auth.html')


# Configure the PayPal SDK with your client ID and secret
# import paypalrestsdk

# paypalrestsdk.configure({
#     "mode": "sandbox",  # Change to "live" for production
#     "client_id": "Ac01X0mWsgl2rVBYSF4fb3LJS5Hb0nD0aKjkkpVLjSeQohjXCuQg72BeKu9Hpc76F1D7dxFSEh5yc0PJ",
#     "client_secret": "EAmonbHMrwqX6xocgv1aLbOIubwQCGkmCXfw93KXN_LWIUciPnJlW1ZLV3Rxi1fqpHaIxyrPZSn2x1sX",
# })


# def create_payment(amount, return_url, cancel_url):
#     payment = Payment({
#         "intent": "sale",
#         "payer": {
#             "payment_method": "paypal",
#         },
#         "transactions": [
#             {
#                 "amount": {
#                     "total": str(amount),
#                     "currency": "USD",  # Change to "PKR" for Pakistani Rupees
#                 },
#                 "description": "Session Booking Payment",
#             }
#         ],
#         "redirect_urls": {
#             "return_url": return_url,
#             "cancel_url": cancel_url,
#         },
#     })
#
#     if payment.create():
#         return payment
#     else:
#         print(payment.error)
#         return None


# @login_required
# def book_session(request, session_id):
#     if request.method == 'POST':
#         therapist_id = request.POST.get('therapist_id')
#         session_id = request.POST.get('session_id')
#         date_time = request.POST.get('date_time')
#
#         # Store values in the session
#         request.session['therapist_id'] = therapist_id
#         request.session['session_id'] = session_id
#         request.session['date_time'] = date_time
#
#         therapist = Therapist.objects.get(id=therapist_id)
#         session = Sessions.objects.get(session_id=session_id)
#         print(session)
#
#         # Create a PayPal payment
#         payment = create_payment(session.price, request.build_absolute_uri('paypal-return'),
#                                  request.build_absolute_uri('paypal-cancel'))
#
#         if payment:
#             # Redirect to PayPal for payment
#             return redirect(payment.links[1].href)
#
#         messages.error(request, 'Failed to initiate payment. Please try again.')
#         return redirect('index')  # Handle the error case as needed
#
#     return render(request, 'book_session.html', {'session_id': session_id})
#

#
# def book_session(request, session_id):
#     if request.method == 'POST':
#         therapist_id = request.POST.get('therapist_id')
#         session_id = request.POST.get('session_id')
#         date_time = request.POST.get('date_time')
#
#         therapist = Therapist.objects.get(id=therapist_id)
#         session = Sessions.objects.get(session_id=session_id)
#
#         # Create a PayPal payment
#         payment = create_payment(session.price, request.build_absolute_uri('paypal-return'), request.build_absolute_uri('paypal-cancel'))
#
#         if payment:
#             # Redirect to PayPal for payment
#             return redirect(payment.links[1].href)
#
#         messages.error(request, 'Failed to initiate payment. Please try again.')
#         return redirect('index')  # Handle the error case as needed
#
#     return render(request, 'book_session.html', {'session_id': session_id})


# def paypal_return(request):
#     print("Reached PayPal Return View")
#     therapist_id = request.session.get('therapist_id')
#     session_id = request.session.get('session_id')
#     date_time = request.session.get('date_time')
#
#     print(f"Therapist ID: {therapist_id}, Session ID: {session_id}, Date Time: {date_time}")
#
#     payment_id = request.GET.get('paymentId')
#     payer_id = request.GET.get('PayerID')
#     payment = Payment.find(payment_id)
#
#     if payment.execute({"payer_id": payer_id}):
#         # Payment successful, continue with session booking logic
#         therapist_id = request.session.get('therapist_id')
#         session_id = request.session.get('session_id')
#         date_time = request.session.get('date_time')
#
#         therapist = Therapist.objects.get(id=therapist_id)
#         session = Sessions.objects.get(session_id=session_id)
#
#         # Create a BookedSession instance
#         booked_session = BookedSession.objects.create(
#             therapist=therapist,
#             patient=request.user.patient,
#             session_type=session.facility,
#             amount=session.price,
#             date_time=date_time,
#             paypal_payment_id=payment_id,
#             selected_time="10:00 AM"  # Replace with the actual selected time
#         )
#
#         # Send notification to therapist (you need to implement this logic)
#         therapist_email = therapist.user.email
#         send_mail(
#             'New Booking',
#             f'You have a new booking from {request.user.username} for {session.facility}.',
#             'MindMend.com',
#             [therapist_email],
#             fail_silently=False,
#         )
#
#         # Send confirmation email to the patient
#         patient_email = request.user.email
#         send_mail(
#             'Booking Confirmation',
#             f'Thank you for booking a session for {session.facility} on {date_time}.',
#             'MindMend.com',
#             [patient_email],
#             fail_silently=False,
#         )
#
#         messages.success(request, 'Session booked successfully.')
#         return redirect('profile')  # Redirect to the patient's profile page
#
#     messages.error(request, 'Failed to execute payment. Please try again.')
#     return redirect('index')  # Handle the error case as needed
# from django.urls import reverse
#
# def paypal_return(request):
#     print("Reached PayPal Return View")
#     therapist_id = request.session.get('therapist_id')
#     session_id = request.session.get('session_id')
#     date_time = request.session.get('date_time')
#     print(f"Therapist ID: {therapist_id}, Session ID: {session_id}, Date Time: {date_time}")
#
#     payment_id = request.GET.get('paymentId')
#     payer_id = request.GET.get('PayerID')
#
#     payment = Payment.find(payment_id)
#
#     if payment.execute({"payer_id": payer_id}):
#         print("Transaction completed by John")
#         therapist = Therapist.objects.get(id=therapist_id)
#         session = Sessions.objects.get(session_id=session_id)
#
#         # Create a BookedSession instance
#         booked_session = BookedSession.objects.create(
#             therapist=therapist,
#             patient=request.user.patient,
#             session_type=session.facility,
#             amount=session.price,
#             date_time=date_time,
#             paypal_payment_id=payment_id,
#             selected_time="10:00 AM"  # Replace with the actual selected time
#         )
#
#         # Send notification to therapist (you need to implement this logic)
#         therapist_email = therapist.user.email
#         send_mail(
#             'New Booking',
#             f'You have a new booking from {request.user.username} for {session.facility}.',
#             'MindMend.com',
#             [therapist_email],
#             fail_silently=False,
#         )
#
#         # Send confirmation email to the patient
#         patient_email = request.user.email
#         send_mail(
#             'Booking Confirmation',
#             f'Thank you for booking a session for {session.facility} on {date_time}.',
#             'MindMend.com',
#             [patient_email],
#             fail_silently=False,
#         )
#
#         messages.success(request, 'Session booked successfully.')
#         return redirect('profile')  # Redirect to the patient's profile page
#
#     else:
#         print(f"Payment execution failed: {payment.error}")
#         messages.error(request, 'Failed to execute payment. Please try again.')
#         return redirect('index')  # Handle the error case as needed
#
#
# def paypal_cancel(request):
#     messages.info(request, 'Payment canceled.')
#     return redirect('index')  # Redirect to the home page or another appropriate page

def feedback_form_view(request):
    questions = [
        {
            'question': 'How would you rate your overall satisfaction with the session?',
            'options': ['Excellent', 'Good', 'Average', 'Poor'],
        },
        {
            'question': 'What specific aspects of the session did you find most helpful?',
            'options': ["Therapist's approach", 'Session topics', 'Techniques used', 'Other'],
        },
        {
            'question': 'Were there any challenges or concerns during the session?',
            'options': ['Yes', 'No'],
        },
        {
            'question': 'How well did the therapist address your needs and concerns?',
            'options': ['Excellent', 'Good', 'Average', 'Poor'],
        },
        {
            'question': 'Do you feel more positive or optimistic after the session?',
            'options': ['Positive', 'Optimistic'],
        },
        {
            'question': 'What topics or issues would you like to focus on in future sessions?',
            'options': [],
        },
    ]
    return render(request, 'feedback_form.html', {'questions': questions})

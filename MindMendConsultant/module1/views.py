# views.py
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Patient, Therapist, Sessions, BookedSession, Notification, Feedback
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .tasks import create_feedback


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
        print(selected_time_str)
        selected_time = datetime.strptime(selected_time_str, "%Y-%m-%d %I:%M %p")
        payment_method = request.POST.get('payment_method', 'nayapay')

        # Print statements for debugging
        print(f"Therapist ID: {therapist_id}")
        print(f"Session Type: {session_type}")
        print(f"Selected Time: {selected_time}")
        print(f"Payment Method: {payment_method}")
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
        patient_notification.save()
        therapist_notification.save()
        feedback = Feedback.objects.create(
            therapist=therapist,
            patient=patient,
            booked_session=booked_session,
            description=f"Feedback for session with {therapist.user.username}",
            answer1="",
            answer2="",
            answer3="",
            answer4="",
            answer5="",
            total_percentage=0,
            created_at=timezone.now(),
        )
        feedback.save()
        # result = create_feedback.apply_async(
        #     args=[therapist_id, patient.id, booked_session.id],
        #     countdown=10
        # )
        #
        # Wait for the result and get the outcome
        # feedback_result = result.get()
        # print(f"Feedback task result: {feedback_result}")
        # print()
        print('happened')
        # Send email notifications
        send_email_to_therapist(therapist, booked_session, selected_time_str=selected_time)
        send_email_to_patient(patient, booked_session, selected_time_str=selected_time)

        return render(request, 'patient_profile.html', {'booked_sessions': [booked_session]})
    next_three_days = [timezone.now() - timezone.timedelta(days=i) for i in range(3)]
    context = {
        'therapist': therapist,
        'next_three_days': next_three_days,
        'time_slots': ['10:00 AM', '02:00 PM', '05:00 PM', '08:00 PM'],
        'session_type': session_type,

    }

    return render(request, 'Book.html', context)


def send_email_to_therapist(therapist, booked_session, selected_time_str):
    subject = 'New Session Booked'
    selected_time = selected_time_str
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
    selected_time = selected_time_str
    subject = 'Session Booked Confirmation'
    message = f"Dear {patient.user.username},\n\nYour session has been booked successfully.\n\nTherapist: {booked_session.therapist.user.username}\nDate: {selected_time.strftime('%d-%b-%Y')}\n\nTiming: {booked_session.selected_time.strftime('%H:%M')} - {selected_time.strftime('%H:%M')}\n\nThank you for choosing our service!"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = patient.user.email

    send_mail(subject, message, from_email, [to_email])


def send_registration_confirmation_email(patient, subject, message):
    """
    Sends a registration confirmation email to the patient.
    """
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

    recent_notifications = Notification.objects.filter(user=user)[:3]
    patient = get_object_or_404(Patient, user=user)
    print(patient)
    booked_sessions = BookedSession.objects.filter(patient=patient)
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
                recent_notifications = Notification.objects.filter(user=user)[:3]
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
                recent_notifications = Notification.objects.filter(user=user)
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
        selected_time = timezone.now()
        password = request.POST['password']
        # Create a User
        user = User.objects.create_user(username=username, email=email, password=password)
        print(user.username, user.email, user.password)
        # Create a Patient
        patient = Patient(user=user, gender=gender, dob=dob, age=age, phone_no=phone_no)
        print(patient.gender, patient.dob)
        patient.save()
        subject = 'Registration Confirmation'
        message = f"Dear {patient.user.username},\n\nThank you for registering with MindMend Consultant. Welcome to our community!\n\n"
        message += "We look forward to helping you on your journey to better mental health.\n\n"
        message += "If you have any questions or need assistance, feel free to contact us.\n\n"
        message += "Best regards,\nMindMend Consultant"
        send_registration_confirmation_email(patient, subject, message)

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
    # Assuming the logged-in user is a patient
    patient = request.user.patient

    # Get all booked sessions for the patient
    booked_sessions = BookedSession.objects.filter(patient=patient).order_by('selected_time')

    # Check if there are any booked sessions
    if booked_sessions:
        # Get the earliest booked session
        earliest_session = booked_sessions[0]
        # Check if it's at least two hours since the earliest session
        unlock_time = earliest_session.selected_time + timedelta(hours=2)
        if timezone.now() >= unlock_time:
            # Feedback form is unlocked, handle form submission
            if request.method == 'POST':
                therapist_id = earliest_session.therapist.id
                answer1 = request.POST.get('answer1')
                answer2 = request.POST.get('answer2')
                answer3 = request.POST.get('answer3')
                answer4 = request.POST.get('answer4')
                answer5 = request.POST.get('answer5')

                # print(answer1, answer2, answer3, answer4, answer5)
                # print(request.POST)
                percentage_mapping = {
                    'Excellent': 20,
                    'Good': 15,
                    'Average': 10,
                    'Poor': 5,
                    'Yes': 20,
                    'No': 10,
                    'Positive': 30,
                    'Optimistic': 20,
                }
                total_percentage = (
                        percentage_mapping.get(answer1, 0) +
                        percentage_mapping.get(answer2, 0) +
                        percentage_mapping.get(answer3, 0) +
                        percentage_mapping.get(answer4, 0) +
                        percentage_mapping.get(answer5, 0)
                )
                # Before incrementing
                print(f"Initial progress_percentage: {patient.progress_percentage}")

                # Increment based on total_percentage
                patient.progress_percentage += total_percentage
                patient.save()

                # After incrementing
                print(f"Final progress_percentage: {patient.progress_percentage}")
                patient.save()
                # Create a Feedback instance and save it
                Feedback.objects.create(
                    therapist_id=therapist_id,
                    description='',
                    patient=patient,
                    answer1=answer1,
                    answer2=answer2,
                    answer3=answer3,
                    answer4=answer4,
                    answer5=answer5,
                    is_viewed=False,
                    total_percentage=total_percentage
                )

                # Redirect to some success page or handle the queuing logic
                therapist_notification = Notification.objects.create(
                    user=earliest_session.therapist.user,
                    content=f"New feedback submitted by patient {patient.user.username}."
                )
                therapist_notification.save()
                return redirect('/')

            # Render the feedback form
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
            context = {
                'questions': questions,
                'earliest_session': earliest_session,
            }
            return render(request, 'feedback_form.html', context)
        else:
            # Feedback form is locked
            context = {
                'unlock_time': unlock_time,
            }
            return render(request, 'feedback_locked.html', context)
    else:
        # No booked sessions, handle accordingly (e.g., show a message)
        return render(request, 'no_booked_sessions.html')


@require_POST
def cancel_booking(request, booked_session_id):
    booking_id = request.POST.get('booking_id')

    try:
        booked_session = BookedSession.objects.get(id=booking_id)
        # Perform your cancellation logic here
        booked_session.delete()

        # Notify the therapist about the cancellation
        therapist_notification = Notification.objects.create(
            user=booked_session.therapist.user,
            content=f"Patient {booked_session.patient.user.username} canceled the session on {timezone.now()}."
        )
        therapist_notification.save()
        # Assuming cancellation was successful
        return redirect('profile')
    except BookedSession.DoesNotExist:
        # Handle the case where the booking does not exist
        return render(request, 'error_404.html')

    # Handle other exceptions or errors as needed
    return render(request, 'error_404.html')


def therapist_feedback_queue(request):
    # Get all patient feedback forms that haven't been viewed by therapists
    pending_feedback = Feedback.objects.filter(is_viewed=False)

    context = {'pending_feedback': pending_feedback}
    return render(request, 'therapist_feedback_form.html', context)


def provide_feedback(request, feedback_id):
    patient_feedback = get_object_or_404(Feedback, pk=feedback_id, is_viewed=False)

    if request.method == 'POST':
        therapist_description = request.POST.get('therapist_description')

        # Update the Feedback instance with therapist's description and set is_viewed to True
        patient_feedback.description = therapist_description
        patient_feedback.is_viewed = True
        patient_feedback.save()

        # Additional logic if needed

        return render(request, 'sessions.html')  # Redirect to a success page or handle accordingly

    context = {'patient_feedback': patient_feedback}

    return render(request, 'therapist_feedback_form.html', context)


# def unviewed_feedbacks(request):
#     # Assuming the logged-in user is a patient#
#     patient = request.user.patient
#
#     # Get unviewed feedbacks for the patient
#     unviewed_feedbacks = Feedback.objects.filter(patient=patient, is_viewed=False)
#
#     context = {'unviewed_feedbacks': unviewed_feedbacks}
#     return render(request, 'base_fb.html', context)


def unviewed_feedbacks(request):
    # Assuming the logged-in user is a patient
    patient = request.user.patient

    # Get feedbacks with total_percentage < 0 and is_viewed=True
    feedbacks_to_create = Feedback.objects.filter(
        Q(patient=patient, total_percentage__lt=100, is_viewed=False) &
        (Q(answer1='') | Q(answer1__isnull=True)) &
        (Q(answer2='') | Q(answer2__isnull=True)) &
        (Q(answer3='') | Q(answer3__isnull=True))
    )

    # Create new feedback objects with desired values
    for feedback_to_create in feedbacks_to_create:
        # Customize the feedback values based on your requirements
        new_feedback = Feedback.objects.create(
            therapist=feedback_to_create.therapist,
            patient=feedback_to_create.patient,
            booked_session=feedback_to_create.booked_session,
            description=f"Feedback for session with {feedback_to_create.therapist.user.username}",
            answer1="",  # Add your fields here
            answer2="",  # Add your fields here
            answer3="",  # Add your fields here
            answer4="",  # Add your fields here
            answer5="",  # Add your fields here
            total_percentage=0,
            created_at=feedback_to_create.created_at,
            is_viewed=False  # Set is_viewed to False for the new feedback
        )

        # Save the new feedback
        new_feedback.save()

    # Get updated unviewed feedbacks for the patient
    unviewed_feedbacks = Feedback.objects.filter(patient=patient, is_viewed=False)

    context = {'unviewed_feedbacks': unviewed_feedbacks}
    return render(request, 'base_fb.html', context)


def therapist_unviewed_feedbacks(request):
    # Assuming the logged-in user is a therapist
    therapist = request.user.therapist

    # Get unviewed feedbacks for the therapist
    unviewed_feedbacks = Feedback.objects.filter(therapist=therapist, is_viewed=False)

    context = {'unviewed_feedbacks': unviewed_feedbacks}
    return render(request, 'therapist_unviewed_feedbacks.html', context)


def feedback_view(request, feedback_id):
    # Get the feedback object
    patient = request.user.patient
    feedback = Feedback.objects.get(id=feedback_id)
    booked_session = feedback.booked_session
    print(booked_session)
    # Feedback form is unlocked, handle form submission
    if request.method == 'POST':
        therapist_id = booked_session.therapist.id
        answer1 = request.POST.get('answer1')
        answer2 = request.POST.get('answer2')
        answer3 = request.POST.get('answer3')
        answer4 = request.POST.get('answer4')
        answer5 = request.POST.get('answer5')
        percentages = {
            'Excellent': 10,
            'Good': 15,
            'Average': 10,
            'Poor':5,
            "Therapist's Approach":20,
            # Define percentages for other options as needed
        }
        # Calculate percentages for each answer
        percentage1 = percentages.get(answer1, 1)  # Default to 0 if answer is not in the dictionary
        percentage2 = percentages.get(answer2, 0)
        percentage3 = percentages.get(answer3, 0)
        percentage4 = percentages.get(answer4, 0)
        percentage5 = percentages.get(answer5, 5)

        # Calculate the total percentage based on answers
        total_percentage = (percentage1 + percentage2 + percentage3 + percentage4 + percentage5) / 5
        # print(answer1, answer2, answer3, answer4, answer5)
        # print(request.POST)
        # Create a Feedback instance and save it
        feedback.answer1 = answer1
        feedback.answer2 = answer2
        feedback.answer3 = answer3
        feedback.answer4 = answer4
        feedback.answer5 = answer5
        feedback.total_percentage = total_percentage
        feedback.save()
        print(total_percentage)
        # Redirect to some success page or handle the queuing logic
        therapist_notification = Notification.objects.create(
            user=booked_session.therapist.user,
            content=f"New feedback submitted by patient {patient.user.username}."
        )
        therapist_notification.save()
        return redirect('/')

    # Render the feedback form
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
    context = {
        'questions': questions,
        'booked_session': booked_session,
    }
    return render(request, 'feedback_form.html', context)


def view_report(request):
    # Assuming the logged-in user is a patient
    patient = request.user.patient

    # Get the latest viewed feedback for the patient
    latest_feedback = Feedback.objects.filter(patient=patient, is_viewed=True).latest('created_at')

    context = {'latest_feedback': latest_feedback}
    return render(request, 'gen_report.html', context)


def download_pdf(request):
    template_path = 'gen_report.html'
    patient = request.user.patient
    # Get the latest viewed feedback for the patient
    latest_feedback = Feedback.objects.filter(patient=patient, is_viewed=True).latest('created_at')
    context = {'latest_feedback': latest_feedback}
    # Pass the data needed for the PDF

    # Create a Django response object with appropriate PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="medical_report.pdf"'

    # Create a PDF object and write it to the response
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response

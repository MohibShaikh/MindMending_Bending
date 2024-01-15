# module1/tasks.py

from celery import shared_task
from django.utils import timezone
from .models import Therapist, Patient, BookedSession, Feedback
import logging

logger = logging.getLogger(__name__)

@shared_task
def create_feedback(therapist_id, patient_id, booked_session_id):
    try:
        therapist = Therapist.objects.get(pk=therapist_id)
        patient = Patient.objects.get(pk=patient_id)
        booked_session = BookedSession.objects.get(pk=booked_session_id)

        # Check if feedback already exists for this session
        existing_feedback = Feedback.objects.filter(
            therapist=therapist, patient=patient, booked_session=booked_session
        ).first()

        if existing_feedback:
            logger.warning("Feedback already created for this session.")
            return  # Feedback already created

        # Log information about the objects
        logger.info(f"Therapist: {therapist}")
        logger.info(f"Patient: {patient}")
        logger.info(f"Booked Session: {booked_session}")

        # Create the feedback
        feedback = Feedback.objects.create(
            therapist=therapist,
            patient=patient,
            booked_session=booked_session,
            description=f"Feedback for session with {therapist.user.username}",
            answer1="",  # Add your fields here
            answer2="",  # Add your fields here
            answer3="",  # Add your fields here
            answer4="",  # Add your fields here
            answer5="",  # Add your fields here
            total_percentage=0,
            created_at=timezone.now(),
            is_viewed=False
        )
        feedback.save()
        # Log success message
        logger.info(f"Feedback created successfully. Feedback ID: {feedback.id}")

        # You can perform additional actions here if needed
        return feedback.id  # Return the feedback ID if needed

    except Exception as e:
        logger.exception(f"Error in create_feedback task: {e}")

import json
import logging
from venv import logger
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import CareTeam, Chat, ChatUserRole, Doctor, HealthJournalEntry, Patient, Profile
from .models import Consultation, Patient, Message
from django.utils import timezone
from datetime import datetime, time
from django.http import JsonResponse
from .google_meet_integration import create_google_meet_link
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.db.models import Q
from datetime import datetime, date
from django.utils.timezone import localtime
from django.core.files.storage import FileSystemStorage
from django.http import Http404



# Signup View
def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Check if username or email is already in use
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("signup")

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        messages.success(request, "Account created successfully! You can now log in.")
        return redirect("login")

    return render(request, "core/auth/signup.html")



#Login View
# Set up logging
logger = logging.getLogger(__name__)
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            try:
                # Ensure profile exists
                profile = user.profile  # Get the user's profile
                logger.debug(f"User {user.username} has profile with role: {profile.role}")

                if profile.role == 'doctor':
                    # Log the redirect action for debugging
                    logger.debug(f"Redirecting {user.username} to doctor dashboard")
                    return redirect("doctor_patient_list")  
                elif profile.role == 'patient':
                    # Log the redirect action for debugging
                    logger.debug(f"Redirecting {user.username} to patient dashboard")
                    return redirect("patient_messages")  
                else:
                    logger.error(f"Invalid user type for {user.username}. Contact support.")
                    messages.error(request, "Invalid user type. Contact support.")
                    return redirect("login")  

            except Profile.DoesNotExist:
                logger.error(f"Profile not found for user {user.username}. Contact support.")
                messages.error(request, "Profile not found. Contact support.")
                return redirect("login")  

        else:
            logger.error(f"Invalid username or password for {username}")
            messages.error(request, "Invalid username or password.")
            return render(request, "core/auth/login.html", {"messages": messages.get_messages(request)})


    return render(request, "core/auth/login.html")


# Logout View
def logout_view(request):
    logout(request)
    return redirect("login")


# Doctor Dashboard Views
@login_required
def doctor_dashboard(request):
    return render(request, "core/dashboard/doctor/dashboard.html")


@login_required
def doctor_appointments(request):
    return render(request, "core/dashboard/doctor/appointments.html")


@login_required
def doctor_messages(request):
    return render(request, "core/dashboard/doctor/messages.html",{"user_id": request.user.id})


@login_required
def doctor_health_logs(request):
    return render(request, "core/dashboard/doctor/health_logs.html")


@login_required
def doctor_patient_details(request):
    return render(request, "core/dashboard/doctor/patient_details.html")


@login_required
def doctor_virtual_consultations(request):
    return render(request, "core/dashboard/doctor/virtual_consultations.html")


@login_required
def doctor_patient_list(request):
    return render(request, "core/dashboard/doctor/patient_list.html")

@login_required
def doctor_profile(request):
    doctor = Doctor.objects.get(user=request.user)
    return render(request, 'core/dashboard/doctor/doctor_profile.html', {'doctor': doctor})

# Patient Dashboard Views
@login_required
def patient_dashboard(request):
    return render(request, "core/dashboard/patient/dashboard.html")


@login_required
def patient_messages(request):
    return render(request, "core/dashboard/patient/messages.html")


@login_required
def patient_health_journal(request):
    return render(request, "core/dashboard/patient/health_journal.html")


@login_required
def patient_health_reminders(request):
    return render(request, "core/dashboard/patient/health_reminders.html")


@login_required
def patient_virtual_visits(request):
    return render(request, "core/dashboard/patient/virtual_visits.html")

@login_required
def patient_profile(request):
    patient = Patient.objects.get(user=request.user)
    return render(request, 'core/dashboard/patient/profile.html', {'patient': patient})


@login_required
def patient_account_settings(request):
    return render(request, "core/dashboard/patient/account_settings.html")


# Support Center View
@login_required
def support_center(request):
    return render(request, "core/support/help.html")


@login_required
def privacy_policy(request):
    return render(request, "core/support/privacy_policy.html")


@login_required
def settings(request):
    return render(request, "core/support/settings.html")

# Consultations
# Doctor appointments
@login_required
def search_patient(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.filter(user__username__icontains=query)
    return render(request, 'core/dashboard/doctor/virtual_consultations.html', {'patients': patients, 'query': query})


@login_required
def schedule_consultation(request):
    if request.method == 'POST':
        try:
            data = request.POST
            print("Received Data:", data)  # Debugging

            patient_id = data.get('patient_id')
            scheduled_date = data.get('scheduled_date')
            scheduled_time = data.get('scheduled_time')
            consult_type = data.get('consult_type')
            condition = request.POST.get("condition")

            # Validate received data
            if not (patient_id and scheduled_date and scheduled_time and consult_type):
                return JsonResponse({'success': False, 'message': 'Missing required fields.'}, status=400)

            # Validate and convert date/time
            try:
                scheduled_date = datetime.strptime(scheduled_date, "%Y-%m-%d").date()
                scheduled_time = datetime.strptime(scheduled_time, "%H:%M").time()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid date or time format.'}, status=400)

            # Get patient object safely (Corrected)
            patient = get_object_or_404(Patient, id=patient_id)

            # Check if the logged-in user is a doctor
            try:
                doctor_instance = Doctor.objects.get(user=request.user)
            except Doctor.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Doctor profile not found. Please create one.'}, status=403)

            # Create a Google Meet session
            google_meet_link = create_google_meet_link(scheduled_date, scheduled_time)

            # Create consultation
            consultation = Consultation(
                doctor=doctor_instance,
                patient=patient,  # Corrected to pass a Patient instance
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                consult_type=consult_type,
                condition=condition,
                google_meet_link=google_meet_link
            )

            consultation.full_clean()  # Validate model fields
            consultation.save()

            return JsonResponse({
                'success': True,
                'google_meet_link': google_meet_link,
                'message': f'Consultation scheduled for {patient.user.username} on {scheduled_date} at {scheduled_time}.'
            })
        
        except Exception as e:
            print("Error:", str(e))  # Debugging
            return JsonResponse({'success': False, 'message': 'Something went wrong.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
def get_consultations(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Doctor profile not found.'}, status=403)

    upcoming = Consultation.objects.filter(doctor=doctor, scheduled_date__gte=datetime.today().date()).order_by('scheduled_date', 'scheduled_time')
    past = Consultation.objects.filter(doctor=doctor, scheduled_date__lt=datetime.today().date()).order_by('-scheduled_date', '-scheduled_time')

    def serialize(consult):
        return {
            "id": consult.id,
            "patient": consult.patient.user.username,
            "date": consult.scheduled_date.strftime("%Y-%m-%d"),
            "time": consult.scheduled_time.strftime("%H:%M"),
            "type": consult.consult_type,
            "condition": consult.condition,
            "link": consult.google_meet_link
        }

    return JsonResponse({
        "success": True,
        "upcoming": [serialize(c) for c in upcoming],
        "past": [serialize(c) for c in past]
    })


@login_required
def get_consultation_details(request, id):
    consult = get_object_or_404(Consultation, id=id, doctor__user=request.user)
    return JsonResponse({
        "patient": consult.patient.user.username,
        "date": consult.scheduled_date.strftime("%Y-%m-%d"),
        "time": consult.scheduled_time.strftime("%H:%M"),
        "type": consult.consult_type,
        "feedback": consult.feedback
    })

@csrf_exempt
@login_required
def save_feedback(request, id):
    consult = get_object_or_404(Consultation, id=id, doctor__user=request.user)
    data = json.loads(request.body)
    consult.feedback = data.get("feedback", "")
    consult.save()
    return JsonResponse({"success": True})


# Patient appointments
from datetime import date
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Consultation, Patient


@login_required
def patient_consultations_api(request):
    user = request.user

    try:
        patient = Patient.objects.get(user=user)
    except Patient.DoesNotExist:
        return JsonResponse({"success": False, "message": "Patient profile not found."}, status=404)

    today = date.today()

    upcoming_consultations = Consultation.objects.filter(
        patient=patient,
        scheduled_date__gte=today
    ).order_by("scheduled_date", "scheduled_time")

    past_consultations = Consultation.objects.filter(
        patient=patient,
        scheduled_date__lt=today
    ).order_by("-scheduled_date", "-scheduled_time")

    def serialize(c):
        return {
            "id": c.id,
            "doctor": f"Dr. {c.doctor.first_name} {c.doctor.last_name}",
            "date": c.scheduled_date.strftime("%Y-%m-%d"),
            "time": c.scheduled_time.strftime("%H:%M"),
            "type": c.consult_type,
            "link": c.google_meet_link,
            "condition": c.condition,
            "feedback": c.feedback,
        }

    return JsonResponse({
        "success": True,
        "upcoming": [serialize(c) for c in upcoming_consultations],
        "past": [serialize(c) for c in past_consultations],
    })




#Health Journal
from .models import HealthJournalEntry
from .forms import HealthJournalEntryForm

@login_required
def patient_health_journal(request):
    if request.method == 'POST':
        form = HealthJournalEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.patient = request.user.patient  # Associate the entry with the logged-in patient
            entry.save()
            return redirect('patient_health_journal')
    else:
        form = HealthJournalEntryForm()
    
    entries = HealthJournalEntry.objects.filter(patient=request.user.patient).order_by('-date_time')
    return render(request, 'core/dashboard/patient/health_journal.html', {
        'form': form,
        'entries': entries,
    })


from django.shortcuts import render, redirect
from .models import HealthJournalEntry, Doctor, Patient
from django.contrib.auth.decorators import login_required

@login_required
def doctor_patient_list(request):
    # Get the doctor related to the logged-in user
    doctor = Doctor.objects.get(user=request.user)

    # Get the list of consultations for this doctor
    consultations = Consultation.objects.filter(doctor=doctor)

    # Use a set to track unique patients and avoid duplicates
    patient_data = []

    # Create a set to track already processed patients by their patient ID
    processed_patients = set()

    for consultation in consultations:
        patient = consultation.patient
        # If patient has already been processed, skip
        if patient.id in processed_patients:
            continue
        processed_patients.add(patient.id)

        # Get the health journal entries for that patient where the condition matches the consultation
        entries = HealthJournalEntry.objects.filter(patient=patient, condition=consultation.condition).order_by('-date_time')

        for entry in entries:
            patient_data.append({
                'patient': patient,
                'entry': entry,
                'severity': entry.pain_severity,
            })

    return render(request, 'core/dashboard/doctor/patient_list.html', {
        'patient_data': patient_data,
        'doctor': doctor,
    })



def get_feedback(request, entry_id):
    try:
        entry = HealthJournalEntry.objects.get(id=entry_id)
        return JsonResponse({'feedback': entry.doctor_feedback or ""})
    except HealthJournalEntry.DoesNotExist:
        return JsonResponse({'feedback': ""}, status=404)


@csrf_exempt 
def save_docfeedback(request, entry_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            feedback = data.get("feedback", "")

            entry = HealthJournalEntry.objects.get(id=entry_id)
            entry.doctor_feedback = feedback
            entry.save()

            return JsonResponse({"message": "Feedback saved successfully"})
        except HealthJournalEntry.DoesNotExist:
            return JsonResponse({"error": "Entry not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)



#Messages
@login_required
def search_conversation(request):
    query = request.GET.get("q", "").strip().lower()

    # Initialize the filtered list
    filtered_users = []

    # Check if the user is a patient
    try:
        patient = request.user.patient
        # Get unique doctors the patient has consulted
        doctor_ids = Consultation.objects.filter(patient=patient).values_list("doctor_id", flat=True).distinct()
        doctors = Doctor.objects.filter(id__in=doctor_ids).select_related("user")
        
        # Filter doctors based on query
        filtered_users = [
            {
                "id": doctor.user.id,
                "name": f"Dr. {doctor.first_name} {doctor.last_name}",
                "specialty": doctor.specialty,
                "username": doctor.user.username,
                "profile_picture": doctor.profile_picture.url if doctor.profile_picture else "/static/core/img/default-doctor.jpg",
                "role": "doctor"
            }
            for doctor in doctors if query in doctor.first_name.lower() or 
                                    query in doctor.last_name.lower() or 
                                    query in doctor.user.username.lower()
        ]
    except Patient.DoesNotExist:
        pass  # If not a patient, skip to checking if they are a doctor

    # Check if the user is a doctor
    try:
        doctor = request.user.doctor
        # Doctors can search for other doctors and patients
        doctors = Doctor.objects.all().select_related("user")
        patients = Patient.objects.all().select_related("user")

        # Filter doctors based on query
        filtered_users += [
            {
                "id": doctor.user.id,
                "name": f"Dr. {doctor.first_name} {doctor.last_name}",
                "specialty": doctor.specialty,
                "username": doctor.user.username,
                "profile_picture": doctor.profile_picture.url if doctor.profile_picture else "/static/core/img/default-doctor.jpg",
                "role": "doctor"
            }
            for doctor in doctors if query in doctor.first_name.lower() or 
                                        query in doctor.last_name.lower() or 
                                        query in doctor.user.username.lower()
        ]

        # Filter patients based on query
        filtered_users += [
            {
                "id": patient.user.id,
                "name": f"{patient.first_name} {patient.last_name}",
                "username": patient.user.username,
                "profile_picture": patient.profile_picture.url if patient.profile_picture else "/static/core/img/default-patient.png",
                "role": "patient"
            }
            for patient in patients if query in patient.first_name.lower() or 
                                          query in patient.last_name.lower() or 
                                          query in patient.user.username.lower()
        ]
    except Doctor.DoesNotExist:
        pass  # If not a doctor, skip this part

    # Return filtered users
    return JsonResponse({"users": filtered_users})



def get_chat_id(user1, user2):
    # Retrieve the chat between the two users, assuming there is only one chat between them
    chat = Chat.objects.filter(participants=user1).filter(participants=user2).first()
    return chat.id if chat else None


#API to send and receive messages
#This endpoint is called to fetch the current user’s ID, which is then stored in CURRENT_USER_ID
@login_required
def current_user(request):
    return JsonResponse({'user_id': request.user.id})


#This endpoint is used in the loadChat(contactId) function to fetch messages for a specific chat with a contact.
def get_chat_messages(request, contact_id):
    try:
        chat = Chat.objects.get(id=contact_id)
    except Chat.DoesNotExist:
        return JsonResponse({'messages': []})  # No messages yet for this chat

    # Determine the role of the current user (doctor or patient)
    user_role = ChatUserRole.objects.get(chat=chat, user=request.user).role

    # Filter messages based on the sender and receiver
    messages = chat.messages.select_related('sender', 'receiver').all()

    message_list = [
        {
            'sender': message.sender.id,  # Changed to sender ID
            'receiver': message.receiver.id,  # Added receiver ID
            'content': message.content,
            'timestamp':localtime(message.timestamp).strftime("%I:%M %p"),
            'file': message.file.url if message.file else None
        }
        for message in messages if (message.sender == request.user) or (message.receiver == request.user)
    ]

    return JsonResponse({'messages': message_list})


#This is also used for starting a new chat, to load the initial messages between the current user and another user.
def get_chat_messages_with_user(request, user_id):
    chat = get_object_or_404(Chat, user1=request.user, user2_id=user_id)  # Assuming a two-user chat model
    messages = chat.messages.all().values('sender', 'content', 'timestamp', 'file')
    return JsonResponse({'messages': list(messages)})


def recent_chats(request):
    recent_chats = Chat.objects.filter(participants=request.user).exclude(participants__is_staff=True, participants__is_superuser=True).order_by('-created_at')[:10]
    
    chats = []
    for chat in recent_chats:
        last_message = chat.messages.order_by('-timestamp').first()
        last_message_content = last_message.content if last_message else 'No messages yet'

        other_user = chat.participants.exclude(id=request.user.id).first()

        if other_user and not (other_user.is_staff or other_user.is_superuser):
            # Check if the other user is a Doctor or Patient and access their profile picture
            if hasattr(other_user, 'doctor'):  # If the other user is a doctor
                profile_picture = other_user.doctor.profile_picture.url if other_user.doctor.profile_picture else "/static/core/img/default-doctor.jpg"
            elif hasattr(other_user, 'patient'):  # If the other user is a patient
                profile_picture = other_user.patient.profile_picture.url if other_user.patient.profile_picture else "/static/core/img/default-patient.png"
            else:  # Default case if the user is neither a doctor nor a patient
                profile_picture = "/static/core/img/default-user.png"
            
            chats.append({
                'chat_id': chat.id,
                'user_id': other_user.id,
                'name': other_user.username,
                'last_message': last_message_content,
                'profile_picture': profile_picture
            })

    return JsonResponse({'chats': chats})



#Create chat view
@csrf_exempt
def create_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('userId')

        current_user = request.user

        try:
            user = User.objects.get(id=user_id)  # Retrieve the User instance
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "User not found"})

        # Ensure current_user and user are distinct
        if current_user.id == user.id:
            return JsonResponse({"success": False, "message": "Cannot create chat with yourself"})

        # Check if a chat already exists between current_user and the target user
        existing_chat = Chat.objects.filter(participants=current_user).filter(participants=user).first()
        if existing_chat:
            return JsonResponse({'success': True, 'chat_id': existing_chat.id})


        # Create a new chat if no existing chat found
        new_chat = Chat.objects.create()

        # Add users to the chat
        new_chat.participants.add(current_user, user)

        # Get the roles from the Profile model
        current_user_role = current_user.profile.role  # Get role from Profile
        user_role = user.profile.role  # Get role from Profile

        # Dynamically assign roles based on the Profile model roles
        if current_user_role == 'doctor' and user_role == 'doctor':
            # If both are doctors, assign both as 'doctor' roles
            ChatUserRole.objects.create(chat=new_chat, user=current_user, role='doctor')
            ChatUserRole.objects.create(chat=new_chat, user=user, role='doctor')
        elif current_user_role == 'doctor' and user_role == 'patient':
            # If current user is a doctor and the other is a patient
            ChatUserRole.objects.create(chat=new_chat, user=current_user, role='doctor')
            ChatUserRole.objects.create(chat=new_chat, user=user, role='patient')
        elif current_user_role == 'patient' and user_role == 'doctor':
            # If current user is a patient and the other is a doctor
            ChatUserRole.objects.create(chat=new_chat, user=current_user, role='patient')
            ChatUserRole.objects.create(chat=new_chat, user=user, role='doctor')
        elif current_user_role == 'patient' and user_role == 'patient':
            # This case should not happen as per your business logic (patients can't message each other)
            return JsonResponse({"success": False, "message": "Patients cannot message each other"})
        
        # Handle file upload if provided
        file = request.FILES.get('file')
        # Inside your create_chat view
        if file:
            fs = FileSystemStorage(location='uploads/messages/')
            filename = f"message_{int(time.time())}_{file.name}"  # Unique filename
            file_path = fs.save(filename, file)
            
            # Construct the correct URL for the frontend
            file_url = f"/media/uploads/messages/{filename}"
            
            message = Message.objects.create(
                chat=new_chat,
                sender=current_user,
                receiver=user,
                content=data.get('content', ''),
                file=file_path,
                filename=filename  # Store original filename
            )
            return JsonResponse({
                "success": True, 
                "chat_id": new_chat.id, 
                "file_url": file_url,
                "filename": filename
            })

        return JsonResponse({"success": True, "chat_id": new_chat.id, "file_url": file_url})

    return JsonResponse({"success": False, "message": "Invalid method."})



# Doctor Profile 
@csrf_exempt
def update_doctor_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')

        doctor = Doctor.objects.get(user=request.user)
        setattr(doctor, field, value)
        doctor.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
def update_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile-picture'):
        doctor = Doctor.objects.get(user=request.user)
        doctor.profile_picture = request.FILES['profile-picture']
        doctor.save()
        return JsonResponse({'success': True, 'new_image_url': doctor.profile_picture.url})
    return JsonResponse({'success': False}, status=400)



# Patient Profile
@csrf_exempt
def update_patient_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')

        patient = Patient.objects.get(user=request.user)
        setattr(patient, field, value)
        patient.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def update_patient_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile-picture'):
        patient = Patient.objects.get(user=request.user)
        patient.profile_picture = request.FILES['profile-picture']
        patient.save()
        return JsonResponse({'success': True, 'new_image_url': patient.profile_picture.url})
    return JsonResponse({'success': False}, status=400)

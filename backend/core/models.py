from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

#Profile Model
class Profile(models.Model):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')  # Default to patient

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    


#Patient model
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    contact_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='patient_pics/', blank=True, null=True)  # Optional profile picture
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_number = models.CharField(max_length=15)
    medical_record_number = models.CharField(max_length=50, unique=True, default="TEMP123")
    blood_type = models.CharField(max_length=3, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    chronic_conditions = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username})"

    @property
    def age(self):
        today = date.today()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1  # Adjust age if the birthday hasn't occurred yet this year
        return age


#Doctor model
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User model
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    specialty = models.CharField(max_length=100)  # Doctor's specialty (e.g., cardiology, dermatology)
    profile_picture = models.ImageField(upload_to='doctor_pics/', blank=True, null=True)  # Optional profile picture
    contact_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    qualifications = models.CharField(max_length=255, blank=True, null=True)  # Doctor's qualifications
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)  # Years of experience
    affiliations = models.CharField(max_length=255, blank=True, null=True)  # Doctor's affiliations

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.specialty}"
    

#CareTeam model
class CareTeam(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    

#Consultation model
class Consultation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="doctor_consultations")  
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="patient_consultations")  
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    consult_type = models.CharField(
        max_length=50,
        choices=[("follow-up", "Follow-up Consultation"), ("urgent", "Urgent Consultation")]
    )
    google_meet_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    feedback = models.TextField(blank=True, null=True)
    condition = models.CharField(max_length=255)


    def __str__(self):
        return f"Consultation with {self.patient.user.username} on {self.scheduled_date} at {self.scheduled_time}"

    

class HealthJournalEntry(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    symptom = models.CharField(max_length=100)  # e.g., Headache, Fatigue
    pain_severity = models.IntegerField(blank=True, null=True)  # 0 to 10 scale
    details = models.TextField()
    attachment = models.FileField(upload_to='journal_attachments/', blank=True, null=True)
    doctor_feedback = models.TextField(blank=True, null=True)
    condition = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.patient.first_name} - {self.symptom} ({self.date_time})"


# Chat Model
class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name="chats") # Users in the chat
    created_at = models.DateTimeField(auto_now_add=True) # Timestamp when chat was created

    # Return the participants' names as a string
    def __str__(self):
        return ", ".join([user.username for user in self.participants.all()])
    
#Message Model
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    file = models.FileField(upload_to="uploads/messages/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def formatted_time(self):
        local_time = self.timestamp.astimezone(timezone.get_current_timezone())
        return local_time.strftime("%I:%M %p")
    
#Chat User Role Model
class ChatUserRole(models.Model):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)  # Link to the Chat model
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)  # Role in the chat (doctor or patient)

    def __str__(self):
        return f"{self.user.username} as {self.role} in Chat {self.chat.id}"


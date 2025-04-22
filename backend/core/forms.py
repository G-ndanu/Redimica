from django import forms
from django.contrib.auth.models import User

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hash password
        if commit:
            user.save()
        return user


from django import forms
from .models import HealthJournalEntry, Consultation

class HealthJournalEntryForm(forms.ModelForm):
    class Meta:
        model = HealthJournalEntry
        fields = ['symptom', 'pain_severity', 'details', 'attachment', 'condition']  
        # Provide a list of conditions for the patient to choose from
        condition = forms.ChoiceField(
            choices=[(consultation.condition, consultation.condition) for consultation in Consultation.objects.all()],
            required=True
        )
        widgets = {
            'pain_severity': forms.NumberInput(attrs={
                'type': 'range', 'min': 0, 'max': 10, 'step': 1, 'id': 'id_pain_severity', 'class': 'slider'  # Custom styling for slider
            }),
        }

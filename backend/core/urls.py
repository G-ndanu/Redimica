from django.urls import include, path
from . import views
from .views import schedule_consultation
from django.contrib.auth import views as auth_views
from django.urls import re_path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Doctor Dashboard URLs
    path('dashboard/doctor/dashboard', views.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('dashboard/doctor/messages/', views.doctor_messages, name='doctor_messages'),
    path('dashboard/doctor/health_logs/', views.doctor_health_logs, name='doctor_health_logs'),
    path('dashboard/doctor/patient_details/', views.doctor_patient_details, name='doctor_patient_details'),
    path('dashboard/doctor/virtual_consultations/', views.doctor_virtual_consultations, name='doctor_virtual_consultations'),
    path('dashboard/doctor/patient_list/', views.doctor_patient_list, name='doctor_patient_list'),
    path('dashboard/doctor/profile/', views.doctor_profile, name='doctor_profile'),
  

    # Patient Dashboard URLs
    path('dashboard/patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/patient/messages/', views.patient_messages, name='patient_messages'),
    path('dashboard/patient/health_journal/', views.patient_health_journal, name='patient_health_journal'),
    path('dashboard/patient/health_reminders/', views.patient_health_reminders, name='patient_health_reminders'),
    path('dashboard/patient/virtual_visits/', views.patient_virtual_visits, name='patient_virtual_visits'),
    path('dashboard/patient/account_settings/', views.patient_account_settings, name='patient_account_settings'),


    #Consultations
    path('doctor/search/', views.search_patient, name='search_patient'),
    path("schedule-consultation/", views.schedule_consultation, name="schedule_consultation"),
    path('api/consultations/', views.get_consultations, name='get_consultations'),
    path("api/consultation-details/<int:id>/", views.get_consultation_details, name="consultation-details"),
    path("api/save-feedback/<int:id>/", views.save_feedback, name="save-feedback"),
    path("api/patient-consultations/", views.patient_consultations_api, name="patient-consultations-api"),


    #Health Journal 
    path('patient/health-journal/', views.patient_health_journal, name='patient_health_journal'),
    path('dashboard/doctor/patient_list/', views.doctor_patient_list, name='doctor_patient_list'),
    path('api/feedback/<int:entry_id>/', views.get_feedback, name='get_feedback'),
    path('api/save-docfeedback/<int:entry_id>/', views.save_docfeedback, name='save_docfeedback'),


    #Messages
    path("search_conversation/", views.search_conversation, name="search_conversation"),
    path('api/current-user/', views.current_user, name='current_user'),  # Get current user ID
    path('get_chat_messages/<int:contact_id>/', views.get_chat_messages, name='get_chat_messages'),  # Get messages for a specific chat
    path('get_chat_messages/<int:user_id>/', views.get_chat_messages_with_user, name='get_chat_messages_with_user'),  # Get messages with a user
    path('recent-chats/', views.recent_chats, name='recent_chats'),  # Get recent chats for the user
    path('api/create_chat/', views.create_chat, name='create_chat'),


    # Profiles
    # Doctor profile
    path('doctor-profile/', views.doctor_profile, name='doctor-profile'),
    path('update-doctor-info/', views.update_doctor_info, name='update_doctor_info'),
    path('update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),

    # Patient profile
    path('dashboard/patient/profile/', views.patient_profile, name='patient-profile'),
    path('update-patient-info/', views.update_patient_info, name='update_patient_info'),
    path('update-patient-profile-picture/', views.update_patient_profile_picture, name='update_patient_profile_picture'),




] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



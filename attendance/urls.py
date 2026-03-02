from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Students — specific paths FIRST, dynamic paths LAST
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/bulk-upload/', views.bulk_upload_students, name='bulk_upload_students'),
    path('students/<int:student_id>/upload-photo/', views.upload_photo, name='upload_photo'),

    # Attendance
    path('attendance/take/', views.take_attendance, name='take_attendance'),
    path('attendance/session/<int:pk>/', views.session_detail, name='session_detail'),
    path('attendance/my/', views.student_attendance, name='student_attendance'),

    # Tickets
    path('tickets/', views.teacher_tickets, name='teacher_tickets'),
    path('tickets/raise/<int:attendance_id>/', views.raise_ticket, name='raise_ticket'),
    path('tickets/resolve/<int:pk>/', views.resolve_ticket, name='resolve_ticket'),

    # Analytics & Reports
    path('analytics/', views.analytics, name='analytics'),
    path('report/<int:student_id>/', views.download_report, name='download_report'),
]

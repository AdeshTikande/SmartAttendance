from django.contrib import admin
from .models import (
    Department, Teacher, Student,
    AttendanceSession, Attendance, AttendanceTicket,
    Subject, LectureSlot
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'phone']
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'name', 'department', 'phone', 'created_at']
    search_fields = ['roll_number', 'name']
    list_filter = ['department']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'teacher']
    list_filter = ['department']


@admin.register(LectureSlot)
class LectureSlotAdmin(admin.ModelAdmin):
    list_display = ['subject', 'lecture_number', 'time_slot', 'room_number', 'date']
    list_filter = ['subject', 'date']


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'department', 'teacher', 'date', 'processed']
    list_filter = ['department', 'date', 'processed']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'status', 'marked_at']
    list_filter = ['status', 'session__date']
    search_fields = ['student__name', 'student__roll_number']


@admin.register(AttendanceTicket)
class AttendanceTicketAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'status', 'created_at', 'resolved_by']
    list_filter = ['status']
    search_fields = ['student__name']
  
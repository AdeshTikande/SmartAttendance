from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Department(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.get_full_name()


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    roll_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    reference_image = models.ImageField(
        upload_to='student_photos/',
        blank=True, null=True
    )
    face_encoding = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.roll_number} - {self.name}"

class Subject(models.Model):
    SUBJECT_TYPE = [
        ('theory', 'Theory'),
        ('lab', 'Lab'),
    ]
    name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=20, default='000000')
    subject_type = models.CharField(max_length=10, choices=SUBJECT_TYPE, default='theory')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.department}"


class LectureSlot(models.Model):
    SLOT_CHOICES = [
        ('09:00-10:00', '9:00 AM - 10:00 AM'),
        ('10:00-11:00', '10:00 AM - 11:00 AM'),
        ('11:00-12:00', '11:00 AM - 12:00 PM'),
        ('12:00-13:00', '12:00 PM - 1:00 PM'),
        ('13:00-14:00', '1:00 PM - 2:00 PM'),
        ('14:00-15:00', '2:00 PM - 3:00 PM'),
        ('15:00-16:00', '3:00 PM - 4:00 PM'),
        ('16:00-17:00', '4:00 PM - 5:00 PM'),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    time_slot = models.CharField(max_length=20, choices=SLOT_CHOICES)
    lecture_number = models.PositiveIntegerField()
    room_number = models.CharField(max_length=20)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.subject.name} | Lecture {self.lecture_number} | {self.time_slot}"


class AttendanceSession(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    subject = models.ForeignKey(
        Subject, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    lecture_slot = models.ForeignKey(
        LectureSlot, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    date = models.DateField(default=timezone.now)
    group_photo = models.ImageField(upload_to='group_photos/')
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        subject_name = self.subject.name if self.subject else "No Subject"
        return f"{subject_name} - {self.date}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'session')

    def __str__(self):
        return f"{self.student.name} - {self.status}"


class AttendanceTicket(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE)
    reason = models.TextField()
    proof_image = models.ImageField(upload_to='ticket_proofs/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def deadline(self):
        return self.created_at + timedelta(hours=48)

    @property
    def is_expired(self):
        return timezone.now() > self.deadline and self.status == 'pending'

    @property
    def hours_remaining(self):
        remaining = self.deadline - timezone.now()
        return max(0, remaining.total_seconds() / 3600)

    def __str__(self):
        return f"Ticket - {self.student.name} ({self.status})"

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import (
    Department, Teacher, Student,
    AttendanceSession, Attendance, AttendanceTicket,
    Subject, LectureSlot
)
from .face_utils import encode_student_face, process_group_photo
from django.http import HttpResponse
from .reports import generate_student_report
import openpyxl
from django.db import models
from .notifications import (
    notify_ticket_raised,
    notify_ticket_resolved,
    notify_low_attendance
)


# ─── AUTH ─────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
    return render(request, 'attendance/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ─── DASHBOARD ────────────────────────────────────────────────

@login_required
def dashboard(request):
    if request.user.is_superuser or Teacher.objects.filter(user=request.user).exists():
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            teacher = None

        if teacher:
            sessions = AttendanceSession.objects.filter(
                teacher=teacher).order_by('-date')[:5]
            pending_tickets = AttendanceTicket.objects.filter(
                session__teacher=teacher,
                status='pending'
            ).count()
        else:
            sessions = AttendanceSession.objects.order_by('-date')[:5]
            pending_tickets = AttendanceTicket.objects.filter(
                status='pending'
            ).count()

        context = {
            'teacher': teacher,
            'sessions': sessions,
            'pending_tickets': pending_tickets,
            'is_teacher': True,
        }

    else:
        try:
            student = Student.objects.get(user=request.user)
            tickets = AttendanceTicket.objects.filter(
                student=student
            ).order_by('-created_at')[:5]
            context = {
                'student': student,
                'tickets': tickets,
                'is_teacher': False,
            }
        except Student.DoesNotExist:
            context = {
                'is_teacher': False,
                'student': None,
                'tickets': [],
            }

    return render(request, 'attendance/dashboard.html', context)


# ─── STUDENTS ─────────────────────────────────────────────────
@login_required
def student_list(request):
    if request.user.is_superuser:
        students = Student.objects.all().order_by('roll_number')
    else:
        teacher = get_object_or_404(Teacher, user=request.user)
        students = Student.objects.filter(
            department=teacher.department
        ).order_by('roll_number')

    # Search
    search = request.GET.get('search', '')
    if search:
        students = students.filter(
            models.Q(name__icontains=search) |
            models.Q(roll_number__icontains=search) |
            models.Q(phone__icontains=search) |
            models.Q(email__icontains=search)
        )

    # Filter by face status
    face_filter = request.GET.get('face', '')
    if face_filter == 'encoded':
        students = students.exclude(face_encoding__isnull=True).exclude(
            face_encoding=''
        )
    elif face_filter == 'pending':
        students = students.filter(
            models.Q(face_encoding__isnull=True) |
            models.Q(face_encoding='')
        )

    return render(request, 'attendance/student_list.html', {
        'students': students,
        'search': search,
        'face_filter': face_filter,
        'total': students.count(),
        'is_teacher': True,
    })
@login_required
def add_student(request):
    if request.user.is_superuser:
        departments = Department.objects.all()
    else:
        teacher = get_object_or_404(Teacher, user=request.user)
        departments = Department.objects.filter(id=teacher.department.id)

    if request.method == 'POST':
        department_id = request.POST.get('department')
        department = get_object_or_404(Department, id=department_id)
        student = Student.objects.create(
            roll_number=request.POST['roll_number'],
            name=request.POST['name'],
            phone=request.POST['phone'],
            department=department,
            reference_image=request.FILES['reference_image']
        )
        success = encode_student_face(student)
        if success:
            messages.success(request, f'{student.name} added & face encoded!')
        else:
            messages.warning(request, f'{student.name} added but face not detected!')
        return redirect('student_list')

    return render(request, 'attendance/add_student.html', {
        'departments': departments,
        'is_teacher': True,
    })


# ─── ATTENDANCE ───────────────────────────────────────────────
@login_required
def take_attendance(request):
    from django.utils import timezone
    import datetime

    if request.user.is_superuser:
        teacher = Teacher.objects.first()
    else:
        teacher = get_object_or_404(Teacher, user=request.user)
        subjects = Subject.objects.filter(department=teacher.department)

    # Auto detect current time slot
    import pytz
    ist = pytz.timezone('Asia/Kolkata')
    now = timezone.now().astimezone(ist)
    current_hour = now.hour
    current_minute = now.minute
    current_time = now.strftime("%I:%M %p")
    current_day = now.strftime("%A")
    today = now.strftime("%Y-%m-%d")

    # Time slot mapping
    slot_map = [
        ('9:15-10:10',   9,  15, 10, 10),
        ('10:10-11:05', 10,  10, 11,  5),
        ('11:05-12:00', 11,   5, 12,  0),
        ('12:45-1:40',  12,  45, 13, 40),
        ('1:40-2:35',   13,  40, 14, 35),
        ('2:45-3:40',   14,  45, 15, 40),
        ('3:40-4:35',   15,  40, 16, 35),
    ]

    current_slot_value = ''
    current_slot = 'No active slot'

    for slot_value, sh, sm, eh, em in slot_map:
        start = datetime.time(sh, sm)
        end = datetime.time(eh, em)
        now_time = datetime.time(current_hour, current_minute)
        if start <= now_time <= end:
            current_slot_value = slot_value
            current_slot = slot_value
            break

    # Auto increment lecture number per subject
    # Will be updated via JS when subject is selected
    next_lecture_number = 1

    # Default room from timetable
    default_room = '301'

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        time_slot = request.POST.get('time_slot')
        lecture_number = request.POST.get('lecture_number')
        room_number = request.POST.get('room_number')

        subject = get_object_or_404(Subject, id=subject_id)

        # Auto get lecture number for this subject
        existing = LectureSlot.objects.filter(
            subject=subject
        ).count()
        if not lecture_number:
            lecture_number = existing + 1

        lecture_slot = LectureSlot.objects.create(
            subject=subject,
            time_slot=time_slot,
            lecture_number=lecture_number,
            room_number=room_number,
            date=timezone.now().date()
        )

        session = AttendanceSession.objects.create(
            teacher=teacher,
            department=teacher.department,
            subject=subject,
            lecture_slot=lecture_slot,
            date=timezone.now().date(),
            group_photo=request.FILES['group_photo']
        )

        students = Student.objects.filter(department=teacher.department)
        for student in students:
            Attendance.objects.get_or_create(
                student=student,
                session=session,
                defaults={'status': 'absent'}
            )

        print("=== Starting Face Recognition ===")
        present_count = process_group_photo(session)
        print(f"=== Done! {present_count} present ===")

        messages.success(
            request,
            f'✅ Attendance taken! Subject: {subject.name} | '
            f'Lecture {lecture_number} | Room {room_number} | '
            f'{present_count} students present!'
        )
        return redirect('session_detail', pk=session.pk)

    return render(request, 'attendance/take_attendance.html', {
        'subjects': subjects,
        'slot_choices': LectureSlot.SLOT_CHOICES,
        'current_slot': current_slot,
        'current_slot_value': current_slot_value,
        'current_time': current_time,
        'current_day': current_day,
        'today': today,
        'next_lecture_number': next_lecture_number,
        'default_room': default_room,
        'is_teacher': True,
        'pending_tickets': AttendanceTicket.objects.filter(
            status='pending'
        ).count(),
    })
@login_required
def session_detail(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    attendances = Attendance.objects.filter(
        session=session
    ).select_related('student')
    present = attendances.filter(status='present').count()
    absent = attendances.filter(status='absent').count()
    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'attendances': attendances,
        'present': present,
        'absent': absent,
        'is_teacher': True,
        'pending_tickets': AttendanceTicket.objects.filter(
            status='pending'
        ).count(),
    })
# ─── STUDENT ATTENDANCE ───────────────────────────────────────

@login_required
def student_attendance(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'No student profile found!')
        return redirect('dashboard')

    subjects = Subject.objects.filter(department=student.department)
    theory_data = []
    lab_data = []

    for subject in subjects:
        sessions = AttendanceSession.objects.filter(subject=subject)
        total = sessions.count()
        if total == 0:
            continue

        present = Attendance.objects.filter(
            student=student,
            session__in=sessions,
            status='present'
        ).count()

        percentage = round((present / total) * 100, 2)

        date_records = Attendance.objects.filter(
            student=student,
            session__in=sessions
        ).select_related('session').order_by('session__date')

        subject_data = {
            'subject': subject,
            'total': total,
            'present': present,
            'absent': total - present,
            'percentage': percentage,
            'date_records': date_records,
        }

        if subject.subject_type == 'theory':
            theory_data.append(subject_data)
        else:
            lab_data.append(subject_data)

    return render(request, 'attendance/student_attendance.html', {
        'student': student,
        'theory_data': theory_data,
        'lab_data': lab_data,
        'is_teacher': False,
    })


# ─── TICKETS ──────────────────────────────────────────────────

@login_required
def teacher_tickets(request):
    if request.user.is_superuser:
        tickets = AttendanceTicket.objects.all().order_by('-created_at')
    else:
        try:
            teacher = Teacher.objects.get(user=request.user)
            tickets = AttendanceTicket.objects.filter(
                session__teacher=teacher
            ).order_by('-created_at')
        except Teacher.DoesNotExist:
            student = get_object_or_404(Student, user=request.user)
            tickets = AttendanceTicket.objects.filter(
                student=student
            ).order_by('-created_at')

    return render(request, 'attendance/teacher_tickets.html', {
        'tickets': tickets,
        'is_teacher': Teacher.objects.filter(user=request.user).exists()
                      or request.user.is_superuser,
    })


@login_required
def raise_ticket(request, attendance_id):
    attendance = get_object_or_404(Attendance, pk=attendance_id)
    existing = AttendanceTicket.objects.filter(
        student=attendance.student,
        session=attendance.session
    ).exists()
    if existing:
        messages.warning(request, 'Ticket already raised for this session!')
        return redirect('dashboard')

    if request.method == 'POST':
        AttendanceTicket.objects.create(
            student=attendance.student,
            session=attendance.session,
            reason=request.POST['reason'],
            proof_image=request.FILES.get('proof_image')
        )
        messages.success(request, 'Ticket raised! Teacher will review in 48 hours.')
        return redirect('dashboard')

    return render(request, 'attendance/raise_ticket.html', {
        'attendance': attendance,
        'is_teacher': False,
    })


@login_required
def resolve_ticket(request, pk):
    ticket = get_object_or_404(AttendanceTicket, pk=pk)

    if request.user.is_superuser:
        teacher = Teacher.objects.first()
    else:
        teacher = get_object_or_404(Teacher, user=request.user)

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'approve':
            ticket.status = 'approved'
            Attendance.objects.filter(
                student=ticket.student,
                session=ticket.session
            ).update(status='present')
            messages.success(
                request,
                f"{ticket.student.name}'s attendance marked present!"
            )
        elif action == 'reject':
            ticket.status = 'rejected'
            messages.warning(request, 'Ticket rejected.')

        ticket.resolved_at = timezone.now()
        ticket.resolved_by = teacher
        ticket.save()
        return redirect('teacher_tickets')

    return render(request, 'attendance/resolve_ticket.html', {
        'ticket': ticket,
        'is_teacher': True,
    })
@login_required
def download_report(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    buffer = generate_student_report(student)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="attendance_{student.roll_number}.pdf"'
    )
    return response


@login_required
def analytics(request):
    if request.user.is_superuser:
        teacher = Teacher.objects.first()
    else:
        teacher = get_object_or_404(Teacher, user=request.user)

    students = Student.objects.filter(department=teacher.department)
    subjects = Subject.objects.filter(department=teacher.department)

    low_attendance = []
    all_student_data = []

    for student in students:
        total_present = 0
        total_classes = 0
        student_subjects = []

        for subject in subjects:
            sessions = AttendanceSession.objects.filter(subject=subject)
            total = sessions.count()
            if total == 0:
                continue
            present = Attendance.objects.filter(
                student=student,
                session__in=sessions,
                status='present'
            ).count()
            percentage = round((present / total) * 100, 2)
            total_present += present
            total_classes += total
            student_subjects.append({
                'subject': subject,
                'percentage': percentage,
                'present': present,
                'total': total,
            })

        overall = round(
            (total_present / total_classes * 100), 2
        ) if total_classes > 0 else 0

        student_info = {
            'student': student,
            'overall': overall,
            'subjects': student_subjects,
            'total_present': total_present,
            'total_classes': total_classes,
        }
        all_student_data.append(student_info)

        if overall < 60:
            low_attendance.append(student_info)
            try:
                for subj in student_subjects:
                    if subj['percentage'] < 60:
                        notify_low_attendance(
                            student,
                            subj['subject'],
                            subj['percentage']
                        )
            except Exception as e:
                print(f"Alert failed: {e}")

    subject_stats = []
    for subject in subjects:
        sessions = AttendanceSession.objects.filter(subject=subject)
        total_sessions = sessions.count()
        if total_sessions == 0:
            continue
        total_present = Attendance.objects.filter(
            session__in=sessions,
            status='present'
        ).count()
        total_possible = total_sessions * students.count()
        avg = round(
            (total_present / total_possible * 100), 2
        ) if total_possible > 0 else 0
        subject_stats.append({
            'subject': subject.name,
            'average': avg,
        })

    return render(request, 'attendance/analytics.html', {
        'low_attendance': low_attendance,
        'all_student_data': all_student_data,
        'subject_stats': subject_stats,
        'is_teacher': True,
        'pending_tickets': AttendanceTicket.objects.filter(
            status='pending'
        ).count(),
    })

@login_required
def bulk_upload_students(request):
    if request.user.is_superuser:
        departments = Department.objects.all()
    else:
        teacher = get_object_or_404(Teacher, user=request.user)
        departments = Department.objects.filter(
            id=teacher.department.id
        )

    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')

        if not excel_file:
            messages.error(request, 'Please upload an Excel file!')
            return redirect('bulk_upload_students')

        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'Only .xlsx files allowed!')
            return redirect('bulk_upload_students')

        try:
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active

            success_count = 0
            error_count = 0
            errors = []
            successes = []

            for row_idx, row in enumerate(
                ws.iter_rows(min_row=2, values_only=True), 2
            ):
                if not any(row):
                    continue

                try:
                    roll_number = str(row[0]).strip() if row[0] else ''
                    name = str(row[1]).strip() if row[1] else ''
                    phone = str(row[2]).strip() if row[2] else ''
                    email = str(row[3]).strip() if row[3] else ''
                    dept_name = str(row[4]).strip() if row[4] else ''

                    if not roll_number:
                        errors.append(f'Row {row_idx}: Roll number missing')
                        error_count += 1
                        continue

                    if not name:
                        errors.append(f'Row {row_idx}: Name missing')
                        error_count += 1
                        continue

                    if not phone:
                        errors.append(f'Row {row_idx}: Phone missing')
                        error_count += 1
                        continue

                    # Check duplicate
                    if Student.objects.filter(
                        roll_number=roll_number
                    ).exists():
                        errors.append(
                            f'Row {row_idx}: {roll_number} already exists!'
                        )
                        error_count += 1
                        continue

                    # Get department
                    try:
                        dept = Department.objects.get(name=dept_name)
                    except Department.DoesNotExist:
                        if not request.user.is_superuser:
                            dept = teacher.department
                        else:
                            errors.append(
                                f'Row {row_idx}: Department '
                                f'"{dept_name}" not found!'
                            )
                            error_count += 1
                            continue

                    # Create student
                    Student.objects.create(
                        roll_number=roll_number,
                        name=name,
                        phone=phone,
                        email=email if email != 'None' else '',
                        department=dept,
                    )
                    success_count += 1
                    successes.append(
                        f'✅ {roll_number} - {name} added!'
                    )

                except Exception as e:
                    errors.append(f'Row {row_idx}: Error — {str(e)}')
                    error_count += 1

            if success_count > 0:
                messages.success(
                    request,
                    f'{success_count} students added successfully!'
                )
            if error_count > 0:
                messages.warning(
                    request,
                    f'{error_count} rows had errors!'
                )

            return render(
                request,
                'attendance/bulk_upload_result.html',
                {
                    'successes': successes,
                    'errors': errors,
                    'success_count': success_count,
                    'error_count': error_count,
                    'is_teacher': True,
                }
            )

        except Exception as e:
            messages.error(request, f'Error reading file: {str(e)}')
            return redirect('bulk_upload_students')

    return render(request, 'attendance/bulk_upload_students.html', {
        'departments': departments,
        'is_teacher': True,
    })
@login_required
def upload_photo(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    if request.method == 'POST':
        if 'reference_image' in request.FILES:
            student.reference_image = request.FILES['reference_image']
            student.save()
            success = encode_student_face(student)
            if success:
                messages.success(
                    request,
                    f'Photo uploaded & face encoded for {student.name}!'
                )
            else:
                messages.warning(
                    request,
                    f'Photo uploaded but face not detected for {student.name}!'
                )
        return redirect('student_list')

    return render(request, 'attendance/upload_photo.html', {
        'student': student,
        'is_teacher': True,
    })

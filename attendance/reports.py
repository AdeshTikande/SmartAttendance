from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer
)
from reportlab.lib.units import inch
from io import BytesIO
from .models import Student, Attendance, AttendanceSession, Subject


def generate_student_report(student):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=inch*0.5, leftMargin=inch*0.5,
        topMargin=inch*0.5, bottomMargin=inch*0.5
    )
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(
        "<b>TRINITY COLLEGE OF ENGINEERING</b>",
        styles['Title']
    ))
    elements.append(Paragraph(
        "Department of Computer Engineering",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        "<b>Student Attendance Report</b>",
        styles['Heading2']
    ))
    elements.append(Spacer(1, 0.2*inch))

    # Student Info Table
    info_data = [
        ['Name', student.name, 'Roll No', student.roll_number],
        ['Department', str(student.department), 'Phone', student.phone],
    ]
    info_table = Table(info_data, colWidths=[
        1.2*inch, 2.5*inch, 1*inch, 1.5*inch
    ])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a237e')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))

    # Subject wise attendance
    subjects = Subject.objects.filter(department=student.department)
    total_overall_present = 0
    total_overall_classes = 0

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
        absent = total - present
        percentage = round((present / total) * 100, 2)
        total_overall_present += present
        total_overall_classes += total

        # Color based on percentage
        if percentage >= 75:
            color = colors.HexColor('#e8f5e9')
        elif percentage >= 60:
            color = colors.HexColor('#fff8e1')
        else:
            color = colors.HexColor('#ffebee')

        elements.append(Paragraph(
            f"<b>{subject.name}</b> "
            f"({subject.subject_code}) — "
            f"<b>{percentage}%</b>",
            styles['Heading3']
        ))

        # Date wise table
        data = [['Date', 'Lecture No', 'Time Slot', 'Room', 'Status']]
        records = Attendance.objects.filter(
            student=student,
            session__in=sessions
        ).select_related('session').order_by('session__date')

        for record in records:
            status = 'Present ✓' if record.status == 'present' else 'Absent ✗'
            data.append([
                str(record.session.date),
                str(record.session.lecture_slot.lecture_number
                    if record.session.lecture_slot else '—'),
                str(record.session.lecture_slot.time_slot
                    if record.session.lecture_slot else '—'),
                str(record.session.lecture_slot.room_number
                    if record.session.lecture_slot else '—'),
                status,
            ])

        # Summary row
        data.append([
            '', '', '', 'Total',
            f'{present}/{total} ({percentage}%)'
        ])

        table = Table(data, colWidths=[
            1.2*inch, 1*inch, 1.5*inch, 0.8*inch, 1.3*inch
        ])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2),
             [colors.white, colors.HexColor('#f5f5f5')]),
            ('BACKGROUND', (0, -1), (-1, -1),
             colors.HexColor('#e8eaf6')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.25*inch))

    # Overall Summary
    overall = round(
        (total_overall_present / total_overall_classes * 100), 2
    ) if total_overall_classes > 0 else 0

    elements.append(Spacer(1, 0.2*inch))
    summary_data = [
        ['Overall Attendance Summary', '', '', ''],
        ['Total Classes', 'Total Present',
         'Total Absent', 'Overall %'],
        [
            str(total_overall_classes),
            str(total_overall_present),
            str(total_overall_classes - total_overall_present),
            f'{overall}%'
        ],
    ]
    summary_table = Table(summary_data, colWidths=[
        1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch
    ])
    summary_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#283593')),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 2), (-1, 2),
         colors.HexColor('#e8f5e9') if overall >= 75
         else colors.HexColor('#ffebee')),
    ]))
    elements.append(summary_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

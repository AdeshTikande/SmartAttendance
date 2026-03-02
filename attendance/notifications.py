from twilio.rest import Client
from django.conf import settings


def send_whatsapp(to_phone, message):
    try:
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        msg = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f'whatsapp:+91{to_phone}',
            body=message
        )
        print(f"✅ WhatsApp sent: {msg.sid}")
        return True
    except Exception as e:
        print(f"❌ WhatsApp failed: {e}")
        return False


def notify_attendance_marked(student, session):
    message = (
        f"✅ Attendance Marked!\n"
        f"Hello {student.name},\n"
        f"Subject: {session.subject.name if session.subject else 'N/A'}\n"
        f"Date: {session.date}\n"
        f"Time: {session.lecture_slot.time_slot if session.lecture_slot else 'N/A'}\n"
        f"Room: {session.lecture_slot.room_number if session.lecture_slot else 'N/A'}\n"
        f"Status: PRESENT ✅\n\n"
        f"SmartAttend System"
    )
    return send_whatsapp(student.phone, message)


def notify_ticket_raised(teacher, ticket):
    message = (
        f"🎫 New Ticket Raised!\n"
        f"Student: {ticket.student.name}\n"
        f"Roll No: {ticket.student.roll_number}\n"
        f"Date: {ticket.session.date}\n"
        f"Reason: {ticket.reason}\n"
        f"Please review within 48 hours!\n\n"
        f"SmartAttend System"
    )
    return send_whatsapp(teacher.phone, message)


def notify_ticket_resolved(student, ticket):
    status = "APPROVED ✅" if ticket.status == 'approved' else "REJECTED ❌"
    message = (
        f"🎫 Ticket Update!\n"
        f"Dear {student.name},\n"
        f"Your ticket is {status}\n"
        f"Date: {ticket.session.date}\n\n"
        f"SmartAttend System"
    )
    return send_whatsapp(student.phone, message)


def notify_low_attendance(student, subject, percentage):
    message = (
        f"⚠️ Low Attendance Alert!\n"
        f"Dear {student.name},\n"
        f"Subject: {subject.name}\n"
        f"Attendance: {percentage}%\n"
        f"Required: 75%\n"
        f"Please attend regularly!\n\n"
        f"SmartAttend System"
    )
    return send_whatsapp(student.phone, message)


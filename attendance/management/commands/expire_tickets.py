from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import AttendanceTicket
from attendance.notifications import send_whatsapp


class Command(BaseCommand):
    help = 'Expire pending tickets older than 48 hours'

    def handle(self, *args, **kwargs):
        pending = AttendanceTicket.objects.filter(status='pending')
        expired_count = 0

        for ticket in pending:
            if ticket.is_expired:
                ticket.status = 'expired'
                ticket.save()
                expired_count += 1
                self.stdout.write(
                    f'Expired ticket for {ticket.student.name}'
                )
                try:
                    message = (
                        f"⏰ Ticket Expired!\n"
                        f"Dear {ticket.student.name},\n"
                        f"Your ticket for {ticket.session.date} "
                        f"has expired.\n"
                        f"Teacher did not respond in 48 hours.\n"
                        f"Please contact teacher directly.\n\n"
                        f"SmartAttend System"
                    )
                    send_whatsapp(ticket.student.phone, message)
                except Exception as e:
                    self.stdout.write(f'Notification failed: {e}')

        self.stdout.write(self.style.SUCCESS(
            f'✅ Expired {expired_count} tickets!'
        ))

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import Department, Teacher, Subject


class Command(BaseCommand):
    help = 'Load TE-B timetable data into database'

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.WARNING('\nLoading TE-B Timetable...\n'))

        # ───────────────────────────────────────────────
        # 1️⃣ Create Department
        # ───────────────────────────────────────────────
        dept, _ = Department.objects.update_or_create(
            name='Computer Engineering TE-B'
        )
        self.stdout.write(self.style.SUCCESS(f'✅ Department: {dept.name}'))

        # ───────────────────────────────────────────────
        # 2️⃣ Create Teachers
        # ───────────────────────────────────────────────
        teachers_data = [
            {'username': 'spm', 'first_name': 'SPM', 'last_name': 'Teacher', 'phone': '9000000001', 'password': 'teacher123'},
            {'username': 'pib', 'first_name': 'PIB', 'last_name': 'Teacher', 'phone': '9000000002', 'password': 'teacher123'},
            {'username': 'skm', 'first_name': 'SKM', 'last_name': 'Teacher', 'phone': '9000000003', 'password': 'teacher123'},
            {'username': 'gn',  'first_name': 'GN',  'last_name': 'Teacher', 'phone': '9000000004', 'password': 'teacher123'},
            {'username': 'rrk', 'first_name': 'RRK', 'last_name': 'Teacher', 'phone': '9000000005', 'password': 'teacher123'},
            {'username': 'syk', 'first_name': 'SYK', 'last_name': 'Teacher', 'phone': '9000000006', 'password': 'teacher123'},
        ]

        teacher_objects = {}

        for t in teachers_data:

            # Create or update User
            user, created = User.objects.get_or_create(
                username=t['username'],
                defaults={
                    'first_name': t['first_name'],
                    'last_name': t['last_name'],
                }
            )

            if created:
                user.set_password(t['password'])
                user.save()

            # Create or update Teacher
            teacher, _ = Teacher.objects.update_or_create(
                user=user,
                defaults={
                    'department': dept,
                    'phone': t['phone']
                }
            )

            teacher_objects[t['username']] = teacher
            self.stdout.write(self.style.SUCCESS(f'✅ Teacher: {t["username"]}'))

        # ───────────────────────────────────────────────
        # 3️⃣ Create Subjects
        # ───────────────────────────────────────────────
        subjects_data = [
            {'name': 'Artificial Intelligence', 'subject_code': '310251',  'subject_type': 'theory', 'teacher_key': 'spm'},
            {'name': 'Cloud Computing', 'subject_code': '310252', 'subject_type': 'theory', 'teacher_key': 'pib'},
            {'name': 'Data Science and Big Data Analytics', 'subject_code': '310253', 'subject_type': 'theory', 'teacher_key': 'skm'},
            {'name': 'Web Technology', 'subject_code': '310254', 'subject_type': 'theory', 'teacher_key': 'gn'},
            {'name': 'Web Technology Lab', 'subject_code': '310254L', 'subject_type': 'lab', 'teacher_key': 'rrk'},
            {'name': 'Cloud Computing Lab', 'subject_code': '310252L', 'subject_type': 'lab', 'teacher_key': 'pib'},
            {'name': 'DSBDA Lab', 'subject_code': '310253L', 'subject_type': 'lab', 'teacher_key': 'skm'},
            {'name': 'AI Lab', 'subject_code': '310251L', 'subject_type': 'lab', 'teacher_key': 'spm'},
            {'name': 'Sports & T&P', 'subject_code': 'TP001', 'subject_type': 'theory', 'teacher_key': 'rrk'},
        ]

        for s in subjects_data:

            teacher = teacher_objects.get(s['teacher_key'])

            if not teacher:
                self.stdout.write(self.style.ERROR(
                    f"❌ Teacher not found for key: {s['teacher_key']}"
                ))
                continue

            subject, created = Subject.objects.update_or_create(
                subject_code=s['subject_code'],
                defaults={
                    'name': s['name'],
                    'subject_type': s['subject_type'],
                    'department': dept,
                    'teacher': teacher
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created Subject: {subject.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'♻ Updated Subject: {subject.name}'))

        # ───────────────────────────────────────────────
        # 4️⃣ Summary
        # ───────────────────────────────────────────────
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('✅ Timetable loaded successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Departments: {Department.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Teachers: {Teacher.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Subjects: {Subject.objects.count()}'))
        self.stdout.write('=' * 50)

        self.stdout.write('\nTeacher Login Credentials:')
        self.stdout.write('-' * 30)

        for t in teachers_data:
            self.stdout.write(
                f"Username: {t['username']} | Password: {t['password']}"
            )

        self.stdout.write(self.style.SUCCESS('\n🎯 Done!\n'))

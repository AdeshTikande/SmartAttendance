# 🎓 SmartAttend — AI-Powered Smart Attendance System

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6.0-green?logo=django)
![DeepFace](https://img.shields.io/badge/DeepFace-AI-orange)
![Twilio](https://img.shields.io/badge/Twilio-WhatsApp-brightgreen?logo=twilio)
![License](https://img.shields.io/badge/License-MIT-yellow)

> An intelligent attendance management system using **Face Recognition**, **WhatsApp Notifications**, and **Analytics Dashboard** — built with Django and DeepFace.

---

## 📸 Screenshots

| Dashboard | Take Attendance | Analytics |
|-----------|----------------|-----------|
| Teacher dashboard with stats | Upload group photo | Charts + Low attendance alerts |

---

## ✨ Features

### 👨‍🏫 Teacher Features
- ✅ **Face Recognition Attendance** — Upload group photo, AI detects present students
- ✅ **Subject & Lecture Tracking** — Track theory and lab subjects separately
- ✅ **Ticket System** — Approve/reject student attendance disputes
- ✅ **WhatsApp Notifications** — Auto alerts via Twilio API
- ✅ **Analytics Dashboard** — Charts, low attendance alerts, subject-wise stats
- ✅ **PDF Report Generation** — Download student attendance reports
- ✅ **Bulk Student Upload** — Add 74+ students via Excel file
- ✅ **Auto Ticket Expiry** — Tickets expire after 48 hours

### 👨‍🎓 Student Features
- ✅ **View Attendance** — Subject-wise theory & lab attendance
- ✅ **Raise Tickets** — Dispute incorrect attendance with proof
- ✅ **WhatsApp Alerts** — Receive low attendance notifications

---

## 🛠️ Tech Stack

| Technology | Usage |
|-----------|-------|
| **Django 6.0** | Backend Framework |
| **Python 3.13** | Programming Language |
| **DeepFace** | Face Recognition AI |
| **OpenCV** | Image Processing |
| **TensorFlow** | Deep Learning Backend |
| **Twilio** | WhatsApp Notifications |
| **ReportLab** | PDF Generation |
| **Chart.js** | Analytics Charts |
| **openpyxl** | Excel File Processing |
| **SQLite** | Database |
| **Bootstrap 5** | Frontend UI |

---

## 📁 Project Structure

```
SmartAttendance/
├── attendance/
│   ├── models.py              # Database models
│   ├── views.py               # Business logic
│   ├── urls.py                # URL routing
│   ├── face_utils.py          # Face recognition logic
│   ├── notifications.py       # WhatsApp via Twilio
│   ├── reports.py             # PDF generation
│   ├── management/
│   │   └── commands/
│   │       ├── load_timetable.py    # Auto-load timetable
│   │       ├── expire_tickets.py    # Auto-expire tickets
│   │       └── create_sample_excel.py
│   └── templates/
│       └── attendance/
│           ├── base.html
│           ├── dashboard.html
│           ├── student_list.html
│           ├── take_attendance.html
│           ├── analytics.html
│           └── ...
├── core/
│   ├── settings.py
│   └── urls.py
├── media/                     # Uploaded photos
├── manage.py
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/SmartAttendance.git
cd SmartAttendance
```

### 2. Install Dependencies
```bash
pip install django
pip install deepface
pip install opencv-python
pip install tensorflow
pip install twilio
pip install reportlab
pip install openpyxl
pip install tf-keras
```

### 3. Configure Settings
In `core/settings.py` add your Twilio credentials:
```python
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User
```bash
python manage.py createsuperuser
```

### 6. Load Timetable Data
```bash
python manage.py load_timetable
```

### 7. Run Server
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

---

## 👥 Default Credentials

### Admin
| Username | Password |
|----------|----------|
| admin | admin123 |

### Teachers (TE-B Department)
| Username | Teacher | Password |
|----------|---------|----------|
| skm | SKM | teacher123 |
| spm | SPM | teacher123 |
| pib | PIB | teacher123 |
| gn | Dr. Geetika Narang | teacher123 |
| rrk | RRK | teacher123 |
| syk | Swati Mohite | teacher123 |

---

## 📚 Subjects (TE-B Computer Engineering)

| Code | Subject | Type |
|------|---------|------|
| 310251 | Artificial Intelligence | Theory |
| 310252 | Cloud Computing | Theory |
| 310253 | Data Science & Big Data Analytics | Theory |
| 310254 | Web Technology | Theory |
| 310251L | AI Lab | Lab |
| 310252L | Cloud Computing Lab | Lab |
| 310253L | DSBDA Lab | Lab |
| 310254L | Web Technology Lab | Lab |
| — | Sports & T&P | Other |

---

## 🔄 Management Commands

```bash
# Load timetable subjects and teachers
python manage.py load_timetable

# Expire pending tickets older than 48 hours
python manage.py expire_tickets

# Create sample Excel template for bulk upload
python manage.py create_sample_excel
```

---

## 📱 WhatsApp Notifications

Notifications are sent automatically for:
- ✅ Attendance marked (to student)
- ✅ Ticket raised (to teacher)
- ✅ Ticket resolved (to student)
- ✅ Low attendance alert < 60% (to student)

**Setup:** Join Twilio sandbox by sending `join travel-living` to `+14155238886` on WhatsApp.

---

## 📊 Analytics Dashboard

- Subject-wise average attendance chart
- Students below 60% attendance alert
- Color-coded progress bars (Green ≥75%, Yellow ≥60%, Red <60%)
- PDF report download per student

---

## 🚀 Key URLs

| URL | Description |
|-----|-------------|
| `/` | Dashboard |
| `/students/` | Student List |
| `/students/bulk-upload/` | Bulk Upload via Excel |
| `/attendance/take/` | Take Attendance |
| `/tickets/` | Ticket Management |
| `/analytics/` | Analytics Dashboard |
| `/report/<id>/` | Download PDF Report |
| `/admin/` | Django Admin Panel |

---

## 🧠 How Face Recognition Works

1. Teacher uploads **group photo** of classroom
2. OpenCV detects all faces in photo
3. DeepFace compares each face with **student reference photos**
4. Matched students are marked **Present**
5. Unmatched students remain **Absent**
6. WhatsApp notification sent to present students

---

## 📝 Bulk Student Upload

1. Download sample Excel template from `/students/bulk-upload/`
2. Fill columns: Roll Number, Name, Phone, Email, Department
3. Upload the Excel file
4. All students added instantly with validation

---

## 🎯 Interview Highlights

This project demonstrates:
- **AI/ML Integration** — Real-world face recognition
- **API Integration** — Twilio WhatsApp API
- **Django Advanced** — Management commands, custom views, file handling
- **Data Visualization** — Chart.js analytics
- **PDF Generation** — ReportLab reports
- **Role-Based Access** — Teacher vs Student permissions
- **Automation** — Auto ticket expiry, auto face encoding

---

## 👨‍💻 Developer

**Adesh Tikande**
- Trinity College of Engineering, Pune
- Computer Engineering TE-B
- Roll No: CO3145

---

## 📄 License

This project is licensed under the MIT License.

---

⭐ **Star this repo if you found it helpful!**

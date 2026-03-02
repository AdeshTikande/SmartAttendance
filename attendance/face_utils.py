import json
import numpy as np
import cv2
import os
import shutil
from deepface import DeepFace
from .models import Student, Attendance
from .notifications import notify_attendance_marked

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("DeepFace not available - face recognition disabled")


def encode_student_face(student):
    if not DEEPFACE_AVAILABLE:
        return False
    # ... rest of existing code
# def encode_student_face(student):
#     try:
#         image_path = student.reference_image.path
#         result = DeepFace.represent(
#             img_path=image_path,
#             model_name="Facenet",
#             enforce_detection=False
#         )
#         if result:
#             encoding = result[0]["embedding"]
#             student.face_encoding = json.dumps(encoding)
#             student.save()
#             print(f"✅ Face encoded for {student.name}")
#             return True
#         return False
#     except Exception as e:
#         print(f"❌ Error encoding: {e}")
#         return False


# def cosine_similarity(a, b):
#     a = np.array(a)
#     b = np.array(b)
#     norm_a = np.linalg.norm(a)
#     norm_b = np.linalg.norm(b)
#     if norm_a == 0 or norm_b == 0:
#         return 0
#     return np.dot(a, b) / (norm_a * norm_b)


# def extract_faces_from_image(image_path):
#     img = cv2.imread(image_path)
#     if img is None:
#         print("Could not load image!")
#         return []

#     height, width = img.shape[:2]
#     if width > 1200:
#         scale = 1200 / width
#         img = cv2.resize(img, (int(width * scale), int(height * scale)))

#     face_regions = []
#     face_cascade = cv2.CascadeClassifier(
#         cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
#     )
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     for scale in [1.05, 1.1, 1.2]:
#         faces = face_cascade.detectMultiScale(
#             gray,
#             scaleFactor=scale,
#             minNeighbors=3,
#             minSize=(20, 20)
#         )
#         if len(faces) > 0:
#             face_regions = faces
#             break

#     print(f"Detected {len(face_regions)} faces in group photo")

#     face_encodings = []
#     temp_dir = "temp_faces"
#     os.makedirs(temp_dir, exist_ok=True)

#     try:
#         full_result = DeepFace.represent(
#             img_path=image_path,
#             model_name="Facenet",
#             enforce_detection=False
#         )
#         if full_result:
#             for r in full_result:
#                 face_encodings.append(r["embedding"])
#             print(f"DeepFace found {len(full_result)} faces directly")

#         for i, (x, y, w, h) in enumerate(face_regions):
#             padding = 20
#             x1 = max(0, x - padding)
#             y1 = max(0, y - padding)
#             x2 = min(img.shape[1], x + w + padding)
#             y2 = min(img.shape[0], y + h + padding)

#             face_img = img[y1:y2, x1:x2]
#             temp_path = f"{temp_dir}/face_{i}.jpg"
#             cv2.imwrite(temp_path, face_img)

#             try:
#                 result = DeepFace.represent(
#                     img_path=temp_path,
#                     model_name="Facenet",
#                     enforce_detection=False
#                 )
#                 if result:
#                     face_encodings.append(result[0]["embedding"])
#             except Exception as e:
#                 print(f"Could not encode face {i}: {e}")

#     finally:
#         if os.path.exists(temp_dir):
#             shutil.rmtree(temp_dir)

#     print(f"Total face encodings extracted: {len(face_encodings)}")
#     return face_encodings


# def process_group_photo(session):
#     try:
#         group_image_path = session.group_photo.path
#         face_encodings = extract_faces_from_image(group_image_path)

#         if not face_encodings:
#             print("No faces found in group photo!")
#             session.processed = True
#             session.save()
#             return 0

#         students = Student.objects.filter(
#             department=session.department
#         ).exclude(
#             face_encoding__isnull=True
#         ).exclude(face_encoding='')

#         present_count = 0
#         SIMILARITY_THRESHOLD = 0.5

#         for student in students:
#             try:
#                 student_encoding = json.loads(student.face_encoding)
#                 best_similarity = 0

#                 for face_enc in face_encodings:
#                     sim = cosine_similarity(student_encoding, face_enc)
#                     if sim > best_similarity:
#                         best_similarity = sim

#                 if best_similarity >= SIMILARITY_THRESHOLD:
#                     Attendance.objects.filter(
#                         student=student,
#                         session=session
#                     ).update(status='present')
#                     present_count += 1
#                     print(f"✅ {student.name} - Present"
#                           f" (score: {best_similarity:.2f})")

#                     # Send WhatsApp notification
#                     try:
#                         notify_attendance_marked(student, session)
#                         print(f"📱 WhatsApp sent to {student.name}")
#                     except Exception as e:
#                         print(f"Notification failed: {e}")
#                 else:
#                     print(f"❌ {student.name} - Absent"
#                           f" (score: {best_similarity:.2f})")

#             except Exception as e:
#                 print(f"Error matching {student.name}: {e}")
#                 continue

#         session.processed = True
#         session.save()
#         return present_count

#     except Exception as e:
#         print(f"Error processing group photo: {e}")
#         return 0
def process_group_photo(session):
    if not DEEPFACE_AVAILABLE:
        return 0
    # ... rest of existing code

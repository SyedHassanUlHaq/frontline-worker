from django.db import models

# Create your models here.
class Chat(models.Model):
    message = models.TextField()
    sender = models.CharField(max_length=255)   # renamed "from" → "sender" (since "from" is reserved in Python/SQL)
    topic = models.CharField(max_length=255, blank=True, null=True)
    session_id = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.session_id}] {self.sender}: {self.message[:30]}"


class Summary(models.Model):
    summary_text = models.TextField()
    session_id = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary for {self.session_id}"


class Appointment(models.Model):
    session_id = models.CharField(max_length=255, db_index=True)
    department = models.CharField(max_length=255)
    time = models.DateTimeField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"Appointment {self.first_name} {self.last_name} ({self.department})"


class WantAppointment(models.Model):
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    wants_appointment = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.session_id} → {self.wants_appointment}"
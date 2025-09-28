from django.db import models

# Create your models here.

class HealthFacility(models.Model):
    id = models.AutoField(primary_key=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    osm_id = models.BigIntegerField(null=True, blank=True)
    osm_type = models.CharField(max_length=50, null=True, blank=True)
    completeness = models.IntegerField(null=True, blank=True)
    is_in_health_zone = models.CharField(max_length=50, null=True, blank=True)
    amenity = models.CharField(max_length=100, null=True, blank=True)
    speciality = models.CharField(max_length=255, null=True, blank=True)
    addr_full = models.TextField(null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    water_source = models.CharField(max_length=255, null=True, blank=True)
    changeset_id = models.BigIntegerField(null=True, blank=True)
    insurance = models.CharField(max_length=255, null=True, blank=True)
    staff_doctors = models.CharField(max_length=50, null=True, blank=True)
    contact_number = models.CharField(max_length=100, null=True, blank=True)
    uuid = models.CharField(max_length=100, null=True, blank=True)
    electricity = models.CharField(max_length=50, null=True, blank=True)
    opening_hours = models.CharField(max_length=255, null=True, blank=True)
    operational_status = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    is_in_health_area = models.CharField(max_length=50, null=True, blank=True)
    health_amenity_type = models.CharField(max_length=255, null=True, blank=True)
    changeset_version = models.IntegerField(null=True, blank=True)
    emergency = models.CharField(max_length=50, null=True, blank=True)
    changeset_timestamp = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    staff_nurses = models.CharField(max_length=50, null=True, blank=True)
    changeset_user = models.CharField(max_length=255, null=True, blank=True)
    wheelchair = models.CharField(max_length=50, null=True, blank=True)
    beds = models.CharField(max_length=50, null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    dispensing = models.CharField(max_length=50, null=True, blank=True)
    healthcare = models.CharField(max_length=100, null=True, blank=True)
    operator_type = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "health_facilities"  # Match your manual table

    def __str__(self):
        return self.name or f"Facility {self.id}"
    
class Chat(models.Model):
    message = models.TextField()
    sender = models.CharField(max_length=255, null=True)   # renamed "from" → "sender" (since "from" is reserved in Python/SQL)
    topic = models.CharField(max_length=255, blank=True, null=True)
    session_id = models.CharField(max_length=255, db_index=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.session_id}] {self.sender}: {self.message[:30]}"


class Summary(models.Model):
    summary_text = models.TextField()
    session_id = models.CharField(max_length=255, db_index=True)
    wants_appointment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary for {self.session_id}"


class Appointment(models.Model):
    session_id = models.CharField(max_length=255, db_index=True)
    department = models.CharField(max_length=255, null=True)
    time = models.DateTimeField()
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f"Appointment {self.first_name} {self.last_name} ({self.department})"


class WantAppointment(models.Model):
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    wants_appointment = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.session_id} → {self.wants_appointment}"
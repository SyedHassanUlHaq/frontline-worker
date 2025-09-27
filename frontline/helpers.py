####

from .models import WantAppointment
from django.core.exceptions import ObjectDoesNotExist

def wants_appointment(session_id: str) -> bool | None:
    try:
        record = WantAppointment.objects.get(session_id=session_id)
        return record.wants_appointment
    except ObjectDoesNotExist:
        return None
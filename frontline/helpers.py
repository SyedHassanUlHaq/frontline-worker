####
from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import Power
from .models import WantAppointment, HealthFacility
from django.core.exceptions import ObjectDoesNotExist

def wants_appointment(session_id: str) -> bool | None:
    try:
        record = WantAppointment.objects.get(session_id=session_id)
        return record.wants_appointment
    except ObjectDoesNotExist:
        return None

def get_closest_matching_department(coordinates: tuple[float, float], department: str):
    x, y = coordinates

    # distance = (x - facility.x)^2 + (y - facility.y)^2
    distance_expr = ExpressionWrapper(
        Power(F("x") - x, 2) + Power(F("y") - y, 2),
        output_field=FloatField()
    )

    facilities = (
        HealthFacility.objects
        .filter(health_amenity_type__icontains=department)   # match department loosely
        .annotate(distance=distance_expr)
        .order_by("distance")[:3]
    )

    results = []
    for f in facilities:
        results.append({
            "id": f.id,
            "department_name": f.health_amenity_type,
            "location_name": f.name,
            "working_hours": f.opening_hours,
        })

    return results

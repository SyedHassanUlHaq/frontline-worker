from django.db.models import F, FloatField, ExpressionWrapper, Q
from django.db.models.functions import Power
from .models import WantAppointment, HealthFacility
from django.core.exceptions import ObjectDoesNotExist


def wants_appointment(session_id: str) -> bool | None:
    print(f"[wants_appointment] Checking if session_id={session_id} wants an appointment...")

    try:
        record = WantAppointment.objects.get(session_id=session_id)
        print(f"[wants_appointment] Found record: {record.session_id}, wants_appointment={record.wants_appointment}")
        return record.wants_appointment
    except ObjectDoesNotExist:
        print(f"[wants_appointment] No record found for session_id={session_id}")
        return None


def get_closest_matching_department(coordinates: tuple[float, float], department: str):
    x, y = coordinates
    print(f"[get_closest_matching_department] Looking for department='{department}' near coordinates=({x}, {y})")

    # distance = (x - facility.x)^2 + (y - facility.y)^2
    distance_expr = ExpressionWrapper(
        Power(F("x") - x, 2) + Power(F("y") - y, 2),
        output_field=FloatField()
    )

    facilities = (
        HealthFacility.objects
        .filter(
            Q(amenity__icontains=department)
        )
        .annotate(distance=distance_expr)
        .order_by("distance")[:3]
    )

    print(f"[get_closest_matching_department] Returning {len(facilities)} facilities (limited to 3)")

    results = []
    for f in facilities:
        print(f"[get_closest_matching_department] Found facility: id={f.id}, "
              f"name={f.name}, dept={f.health_amenity_type}, distance={f.distance}, "
              f"working_hours={f.opening_hours}")

        results.append({
            "id": f.id,
            "department_name": f.health_amenity_type,
            "location_name": f.name,
            "working_hours": f.opening_hours,
        })

    print(f"[get_closest_matching_department] Final results: {results}")
    return results


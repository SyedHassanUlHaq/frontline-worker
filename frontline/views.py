from django.shortcuts import render
from frontline.helpers import wants_appointment, get_closest_matching_department
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from frontline.helpers import wants_appointment, get_closest_matching_department
# Create your views here.

@require_GET
def temp(request):
    session_id = request.GET.get("session_id", "23423")  # default for testing
    appointment = wants_appointment(session_id)
    facilities = get_closest_matching_department((67.069987889853, 24.9210952612059), "hospital")

    return JsonResponse({
        "wants_appointment": appointment,
        "closest_facilities": facilities
    })
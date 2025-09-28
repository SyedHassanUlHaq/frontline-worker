from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Summary
from django.db import transaction
from .helpers import wants_appointment, get_closest_matching_department, classify_emergency_agent, user_facing_agent, appointment_agent, create_appointment, save_chat_messages, summarizing_agent, get_last_five_messages

# Create your views here.
@api_view(["POST"])
def chat_flow(request):
    user_message = request.data.get("message")
    session_id = request.data.get("session_id")  # boolean flag
    latitude = request.data.get("latitude")  # assuming per-user tracking
    longitude = request.data.get("longitude")  # assuming per-user tracking
    latency = request.data.get("latency")  # network latency in ms
    coordinates = (latitude, longitude) if latitude and longitude else None
    
    if not user_message:
        return Response({"error": "message is required"}, status=400)
    
    # wants_appointment is a boolean flag
    appointment = wants_appointment(session_id)

    messages = get_last_five_messages(session_id)
    summary = Summary.objects.filter(session_id=session_id).order_by('-created_at').first()

    if appointment == False:
        #Classify department
        emergency_result = classify_emergency_agent(latency, user_message)
        # Get closest department
        closest_departments = get_closest_matching_department(coordinates, emergency_result.get("department"))
        
        response = user_facing_agent(latency, user_message, summary, messages, closest_departments, emergency_result.get("emergency_level"))
        
    else:
        # Step 5: Handle appointment booking flow
        # appointment agent
        info = appointment_agent(latency, user_message, summary, messages, closest_departments)
        response = info.get("answer")
        #
        # check if all details present (placeholder)
        if info.get("all_fields_collected"):
            with transaction.atomic():
                appointment = create_appointment(
                    session_id=session_id,
                    department_id=info.get("chosen_department_id"),
                    date=info.get("appointment_date"),
                    time=info.get("appointment_time"),
                    first_name=info.get("first_name"),
                    last_name=info.get("last_name"),
                    email=info.get("email"),
                )
    
    #  store the agent's response and user's message in chat table
    save_chat_messages(session_id, user_message, response)
    
    # Store the summary of the conversation so far in summary table in background
    summarizing_agent(latency, user_message, summary, session_id)

    # Step 6: Return agent response
    return Response({
        "agent_response": response
    })
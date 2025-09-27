from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction

# Create your views here.
@api_view(["POST"])
def chat_flow(request):
    user_message = request.data.get("message")
    session_id = request.data.get("session_id")  # boolean flag
    latitude = request.data.get("latitude")  # assuming per-user tracking
    longitude = request.data.get("longitude")  # assuming per-user tracking
    coordinates = (latitude, longitude) if latitude and longitude else None
    
    if not user_message:
        return Response({"error": "message is required"}, status=400)
    
    # wants_appointment is a boolean flag

    if 'wants_appointment' == False:
        #Classify department
        
        pass
        #Get closest department
        

        #main agent
        
    else:
        # Step 5: Handle appointment booking flo
        #appointment agent
        pass
        # 
        # check if all details present (placeholder)    
        
    # store the agent's response and user's message in chat table
    
    # Store the summary of the conversation so far in summary table in background

    # Step 6: Return agent response
    return Response({
        "agent_response": 'agent_response'
    })
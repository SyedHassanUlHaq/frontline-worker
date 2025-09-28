from django.db.models import F, FloatField, ExpressionWrapper, Q
from django.db.models.functions import Power
from .models import WantAppointment, HealthFacility, Summary
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

import os
import json
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Get the API key from environment variables
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
print("openrouter api key", OPENROUTER_API_KEY)

# Check if the API key is present; if not, raise an error
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set. Please ensure it is defined in your .env file.")

# # Load university data
# DATA_PATH = os.path.join("knowledge", "iqra_university_data.json")
# try:
#     with open(DATA_PATH, 'r') as file:
#         university_data = json.load(file)
# except FileNotFoundError:
#     raise FileNotFoundError(f"Data file not found at: {DATA_PATH}")

# Create a context string from the university data
# context = """
# """


external_client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

model = OpenAIChatCompletionsModel(
    model="google/gemini-2.0-flash-001",
    openai_client=external_client
)

run_config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Format the context with the data
# formatted_context = context.format(data=json.dumps(university_data, indent=2))
# agent: Agent = Agent(name="Iqra University Assistant", model=model)


def classify_emergency_agent(latency, message):
    """
    LLM agent which returns in json: department, emergency_level
    
    Args:
        latency: Response time requirement
        message: Emergency message to classify
    
    Returns:
        dict: JSON with department and emergency_level keys
    """
    emergency_agent = Agent(name="Emergency Classifier", model=model)
    
    prompt = f"""
    Analyze this emergency message and classify it based on the department and emergency level.
    
    Message: {message}
    Response time requirement: {latency} seconds
    
    Please respond with a JSON object containing:
    - department: Choose ONLY from these departments: "Police post", "Police Station", "Hospital", "Clinic", "Pharmacy", "Doctors", "Dentist"
    - emergency_level: The urgency level (1-5, where 1 is critical/life-threatening, 5 is low priority)
    
    IMPORTANT: The department field MUST be exactly one of the listed departments above. Do not use any other department names.
    
    Only return the JSON object, no additional text.
    """
    
    result = Runner.run_sync(emergency_agent, prompt)
    
    # Clean the response - remove markdown code blocks if present
    raw_response = result.final_output.strip()
    if raw_response.startswith('```json'):
        raw_response = raw_response[7:]  # Remove ```json
    if raw_response.startswith('```'):
        raw_response = raw_response[3:]   # Remove ```
    if raw_response.endswith('```'):
        raw_response = raw_response[:-3]  # Remove trailing ```
    
    raw_response = raw_response.strip()
    
    try:
        # Parse the JSON response
        response_json = json.loads(raw_response)
        return response_json
    except json.JSONDecodeError:
        # If JSON parsing fails, return a default response
        return {
            "department": "General",
            "emergency_level": 3
        }
#####################################################
# def secondary_agent(latency, message):
#     """
#     LLM agent which returns in json: department, emergency_level
    
#     Args:
#         latency: Response time requirement
#         message: Emergency message to classify
    
#     Returns:
#         dict: JSON with department and emergency_level keys
#     """
#     secondary_agent = Agent(name="Secondary Agent", model=model)
    
#     prompt = f"""
#     Analyze this emergency message and classify it based on the department and emergency level.
    
#     Message: {message}
#     Response time requirement: {latency} seconds
    
#     Please respond with a JSON object containing:
#     - department: Choose ONLY from these departments: "Police post", "Police Station", "Hospital", "Clinic", "Pharmacy", "Doctors", "Dentist"
#     - emergency_level: The urgency level (1-5, where 1 is critical/life-threatening, 5 is low priority)
    
#     IMPORTANT: The department field MUST be exactly one of the listed departments above. Do not use any other department names.
    
#     Only return the JSON object, no additional text.
#     """
    
#     result = Runner.run_sync(secondary_agent, prompt)
    
#     # Clean the response - remove markdown code blocks if present
#     raw_response = result.final_output.strip()
#     if raw_response.startswith('```json'):
#         raw_response = raw_response[7:]  # Remove ```json
#     if raw_response.startswith('```'):
#         raw_response = raw_response[3:]   # Remove ```
#     if raw_response.endswith('```'):
#         raw_response = raw_response[:-3]  # Remove trailing ```
    
#     raw_response = raw_response.strip()
    
#     try:
#         # Parse the JSON response
#         response_json = json.loads(raw_response)
#         return response_json
#     except json.JSONDecodeError:
#         # If JSON parsing fails, return a default response
#         return {
#             "response": "I'm sorry, I can't help with that."
#         }


# Test the classify_emergency_agent function
# emergency_result = classify_emergency_agent(30, "I need a water connection permit for my new house.")
# print("Emergency Classification Result:")
# print(json.dumps(emergency_result, indent=2))


def user_facing_agent(latency, message, summary, messages, departments, emergency_level):
    """
    LLM agent that provides a conversational response to the user based on their message and context.

    Args:
        latency: Response time requirement
        message: Emergency message to classify
        summary: Conversation summary so far
        messages: Last 3 messages in this chat
        departments: Relevant departments for this user
        emergency_level: Current emergency level

    Returns:
        str: A conversational response to the user
    """
    emergency_agent = Agent(name="Emergency Classifier", model=model)

    prompt = f"""
        You are a helpful assistant that provides users with clear and supportive responses.
        Conversation summary so far:
        {summary}
        Last 3 messages in this chat:
        {messages}
        The relevant departments for this user are:
        {departments}
        Emergency level is {emergency_level}.
        The departments are given in the format:
        id, department_name, location_name, working_hours
        The user’s latest message:
        "{message}"
        Your tasks:
        1. Understand the user’s request in the context of the summary and recent messages, relevant department, and emergency level.
        2. If the user is in distress or asking for help, provide a calm and supportive message first.
        3. Present the relevant departments in a **clear, user-friendly message**, including:
           - Department name
           - Location name
           - Working hours
        4. If the emergency_level is 1 or 2, prioritize suggesting immediate help options (e.g., emergency services) in your response.
        5. If the emergency_level is 3, 4, or 5, ask the user if they would like an appointment.
        6. Keep the response conversational, short, and easy to understand.
    """

    result = Runner.run_sync(emergency_agent, prompt)

    # Clean the response - remove markdown code blocks if present
    raw_response = result.final_output.strip()
    if raw_response.startswith('```json'):
        raw_response = raw_response[7:]  # Remove ```json
    if raw_response.startswith('```'):
        raw_response = raw_response[3:]   # Remove ```
    if raw_response.endswith('```'):
        raw_response = raw_response[:-3]  # Remove trailing ```

    raw_response = raw_response.strip()

    return raw_response

    

import json

def summarizing_agent(latency, message, summary, session_id):
    """
    LLM agent which returns a structured summary of the conversation so far and updates/creates the Summary model.

    Args:
        latency: Response time requirement
        message: Latest user message
        summary: Previous summary
        session_id: Unique session identifier

    Returns:
        dict: JSON with conversation summary and extracted key info
    """
    summarizer_agent = Agent(name="Conversation Summarizer", model=model)
    prompt = f"""
        You are a summarizing assistant.
        Current conversation summary:
        {summary}
        Latest user message:
        "{message}"
        Your tasks:
        1. Create a concise, updated summary of the conversation so far.
        2. Capture the user’s intent and context (what they need or are asking for).
        3. Note any relevant department(s) that may be useful given the conversation.
        4. Always return a JSON object containing:
           - updated_summary: Concise but complete summary of the conversation so far
           - appointment_active: Boolean indicating if appointment booking is in progress
    """
    result = Runner.run_sync(summarizer_agent, prompt)
    # Clean response
    raw_response = result.final_output.strip()
    if raw_response.startswith('```json'):
        raw_response = raw_response[7:]
    if raw_response.startswith('```'):
        raw_response = raw_response[3:]
    if raw_response.endswith('```'):
        raw_response = raw_response[:-3]
    raw_response = raw_response.strip()

    try:
        response_json = json.loads(raw_response)
    except json.JSONDecodeError:
        response_json = {
            "updated_summary": f"User said: {message}. Previous summary: {summary}",
            "appointment_active": False
        }

    # Update or create the Summary record
    Summary.objects.update_or_create(
        session_id=session_id,
        defaults={
            'summary_text': response_json['updated_summary'],
            'wants_appointment': response_json['appointment_active'],
        }
    )

    return response_json




def appointment_agent(latency, message, summary, messages, departments):
    """
    LLM agent which collects appointment details step by step:
    - first_name
    - last_name
    - email
    - chosen_department_id
    
    Returns:
        dict: JSON with collected fields and the agent’s next question
    """

    agent = Agent(name="Appointment Agent", model=model)

    prompt = f"""
        You are an assistant that schedules appointments.

        Conversation summary so far:
        {summary}

        Last 3 messages in this chat:
        {messages}

        The available departments are:
        {departments}

        The user’s latest message:
        "{message}"

        Your tasks:
        1. Collect the following fields one by one, in order:
            - first_name
            - last_name
            - email (must be validated with a proper format, e.g., user@example.com)
            - chosen_department_id (must exist in the provided departments list)
            - date chosen for appointment (format: YYYY-MM-DD)
            - time chosen for appointment (format: HH:MM, 24-hour)
        2. Only ask for one field at a time. Do not skip ahead.
        3. If a required field is already provided by the user, confirm and move to the next.
        4. If email is invalid, ask again until a valid one is provided.
        5. When all fields are collected, confirm the details.

        Always return a JSON object with:
        - answer: The question or confirmation message you want to show the user
        - first_name: collected or null
        - last_name: collected or null
        - email: collected or null
        - chosen_department_id: collected or null
        - all_fields_collected: boolean (true only when all fields are filled)
    """

    result = Runner.run_sync(agent, prompt)

    # Clean response
    raw_response = result.final_output.strip()
    if raw_response.startswith('```json'):
        raw_response = raw_response[7:]
    if raw_response.startswith('```'):
        raw_response = raw_response[3:]
    if raw_response.endswith('```'):
        raw_response = raw_response[:-3]
    raw_response = raw_response.strip()

    try:
        response_json = json.loads(raw_response)
        return response_json
    except json.JSONDecodeError:
        return {
            "answer": "Sorry, I couldn’t process your details. Could you repeat?",
            "first_name": None,
            "last_name": None,
            "email": None,
            "chosen_department_id": None,
            "appointment_date": None,
            "appointment_time": None,
            "all_fields_collected": False
        }


from datetime import datetime
from django.utils.timezone import make_aware
from .models import Appointment

def create_appointment(session_id, first_name, last_name, email, chosen_department_id, date_str, time_str, phone=None):
    """
    Creates an Appointment record from collected details.

    Args:
        session_id (str): The session identifier
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): Validated email
        chosen_department_id (str|int): Department ID or name
        date_str (str): Appointment date in 'YYYY-MM-DD'
        time_str (str): Appointment time in 'HH:MM' (24-hour format)
        phone (str, optional): User's phone number

    Returns:
        Appointment: The created Appointment instance
    """

    # Combine date and time into a datetime object
    try:
        datetime_str = f"{date_str} {time_str}"
        appointment_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        appointment_datetime = make_aware(appointment_datetime)  # Make timezone-aware
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {e}")

    # Create appointment record
    appointment = Appointment.objects.create(
        session_id=session_id,
        department=str(chosen_department_id),  # store id or name depending on design
        time=appointment_datetime,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone
    )

    return appointment



from django.utils import timezone
from models import Chat

def save_chat_messages(session_id, user_message, agent_response, topic=None, sender_user="user", sender_agent="agent"):
    """
    Save both user and agent messages to the Chat model.

    Args:
        session_id (str): Unique session identifier
        user_message (str): Message from the user
        agent_response (str): Response from the agent
        topic (str, optional): Topic of the conversation
        sender_user (str, optional): Sender label for the user message
        sender_agent (str, optional): Sender label for the agent message
    """
    # Save user message
    Chat.objects.create(
        message=user_message,
        sender=sender_user,
        topic=topic,
        session_id=session_id,
    )

    # Save agent response
    Chat.objects.create(
        message=agent_response,
        sender=sender_agent,
        topic=topic,
        session_id=session_id,
    )


def get_last_five_messages(session_id):
    """
    Retrieve the last 5 messages for a given session_id, ordered by creation time.

    Args:
        session_id (str): Unique session identifier

    Returns:
        QuerySet: Last 5 Chat objects for the session, ordered by created_at (newest first)
    """
    return Chat.objects.filter(session_id=session_id).order_by('-created_at')[:5]

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
emergency_result = classify_emergency_agent(30, "I need a water connection permit for my new house.")
print("Emergency Classification Result:")
print(json.dumps(emergency_result, indent=2))
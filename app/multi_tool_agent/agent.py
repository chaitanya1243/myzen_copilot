import datetime
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools import ToolContext, FunctionTool

import requests

API_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkNGRTFFNDFEMEQwMEQ5RDIxRUE1M0EwQzgxM0EyRkZFRkY3QkUyN0FSUzI1NiIsInR5cCI6ImF0K2p3dCIsIng1dCI6InotSGtIUTBBMmRJZXBUb01nVG92X3Y5NzRubyJ9.eyJuYmYiOjE3NDU2NDIyNjksImV4cCI6MTc0NTY3ODI2OSwiaXNzIjoiaHR0cHM6Ly9pZHMuemVub3RpLmNvbSIsImF1ZCI6ImFwaSIsImNsaWVudF9pZCI6IjZjM2NmZTI2LTk4OTQtNGE3ZS05MjlhLWM5ODg5YzliYmVkMSIsInN1YiI6ImIxMmIyYmE2LTM0ZmYtNDk0Ny05OGU3LWE3NjE4OTMzM2I3NSIsImF1dGhfdGltZSI6MTc0NTEyNzg1OSwiaWRwIjoibG9jYWwiLCJ1c2VyX2lkIjoiYjEyYjJiYTYtMzRmZi00OTQ3LTk4ZTctYTc2MTg5MzMzYjc1Iiwib3JnX2lkIjoiNmIwMjliZTUtNjQ1Yy00ZjgxLTg4MmMtZTRlYjU5ZTE0MmQ0IiwiYWNjX25hbWUiOiJhbXJzMDEiLCJjZW50ZXJfaWQiOiJiYzc3Yjk4Mi0yYjA1LTQ5ZWItYTQxZi02ZGY4Mzc0MzFlYmIiLCJ0aW1lX3pvbmVfaWQiOiI2OCIsImN1bHR1cmVfaWQiOiI0MyIsImN1cnJlbmN5X2lkIjoiMTQ4Iiwiem9uZV9pZCI6IiIsImxhc3RfZGF0ZSI6IiIsImltbyI6IkZhbHNlIiwibG9naW5fdXNlcl90eXBlIjoiRW1wbG95ZWUiLCJzb3VyY2VfYXBwIjoiNTAiLCJjbGllbnRfdHlwZSI6IkludGVybmFsTXVsdGlBY2NvdW50IiwibmFtZSI6ImxvY2RAemVub3RpLmNvbSIsImFjY291bnRfbmFtZSI6ImFtcnMwMSIsImJyb3dzZXJfaWQiOiI2YzFmN2ZiNS1kN2IwLTQxNDUtYWU4My1kYTVlY2UwMDJjNTciLCJqdGkiOiI0MjU0RTUwQzhCQ0IwQ0I1QTJFMDRBOUI3QzM4RUM5RSIsInNpZCI6IjEzNTNCOEZEQTU5NzI2QzhDNkNGMkUzRUNDN0RCNzMyIiwiaWF0IjoxNzQ1MTI3ODYwLCJzY29wZSI6WyJvcGVuaWQiLCJhcGkiLCJvZmZsaW5lX2FjY2VzcyJdLCJhbXIiOlsicHdkIl19.PytAmy4Sm_pBUjGKbZHIb4snqhflfwot7F7Qa9qgRC5pJCNjX53NgMcZFcLz64ixXudvFZQP1hNf2fZQVvAx5T7F8UlhL5SKg03-R81gfGRUuSaJaSNlKbU18EM337VSQOhN4xSh4BJwwlqYhZ2jV3cYr-cg8EEs0nBHeGQZvgRnFOcMSfYJJ8cbclaJ3dDbSdhdGtPHjhg6lGNV9LcsiowfRjeVgrbnInofwWkB6-R_JOlt5z9XXXWVGSI9GwTUFE7-AILKfca3lVMVeTItHmssre_uyYhaFpjrVZdd7dmQdiRWvbvYicG7atdVIMnuNHDtNYPtNbDLyLO6I0miRA"
HOST = "https://apiamrs01.zenoti.com"

app_context = {
    "center_id": "bc77b982-2b05-49eb-a41f-6df837431ebb",
    "therapist_id": "b12b2ba6-34ff-4947-98e7-a76189333b75",
}


async def search_services(
    search_value: str,
    tool_context: ToolContext
) -> dict:
    """Search for services based on given parameters.
    
    Args:
        search_value (str): Search term
    
    Returns:
        dict: List of services matching the search criteria
    """

    center_id = app_context['center_id']
    therapist_id = app_context['therapist_id']

    query_params = {
        'CenterId': center_id,
        'SearchValue': search_value
    }
    
    # Add optional parameters if they exist
    # if user_id:
    #     query_params['UserId'] = user_id
    if therapist_id:
        query_params['TherapistId'] = therapist_id

    query_params['AppointmentDate'] =  datetime.datetime.now().isoformat()
    
    # Prepare headers with bearer token
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Remove None values from headers
    headers = {k: v for k, v in headers.items() if v is not None}
    
    # Make the HTTP request
    url = f'{HOST}/api/Services/Search'
    
    response = requests.get(url, params=query_params, headers=headers)
    
    # Parse the response
    data = response.json()
    services = data.get('Services', [])
    print(services)
    tool_context.state['services_raw'] = services
    return { 'status': 'success', 'services': services}


async def select_service(
    service_id: str,
    tool_context: ToolContext
) -> dict:
    """Select a specific service by its ID from previously fetched services.
    
    This tool retrieves the service details from previously searched services
    and stores the selected service in the state for further processing.
    
    Args:
        service_id (str): The ID of the service to select
    
    Returns:
        dict: Information about the selected service with status
              indicating if the service was found
    """
    # Get previously stored services
    services = tool_context.state.get('services_raw', [])
    
    if not services:
        return {
            'status': 'error',
            'error_message': 'No services available. Please search for services first.'
        }
    
    # Find the service with the matching ID
    selected_service = None
    for service in services:
        if service.get('Id') == service_id:
            selected_service = service
            break
    
    # Store the selected service and return appropriate response
    if selected_service:
        tool_context.state['selected_service'] = selected_service
        print(f"Selected service: {selected_service}")
        return {
            'status': 'success',
            'service': selected_service
        }
    else:
        return {
            'status': 'error',
            'error_message': f'Service with ID {service_id} not found.'
        }


async def search_guests(
    search_value: str,
    tool_context: ToolContext
) -> dict:
    """Search for guests in the system.
    
    This tool searches for guests using the provided search term and returns
    matching guest records from the Zenoti system.
    
    Args:
        search_value (str): Search term to find guests (name, phone, email etc.)
    
    Returns:
        dict: List of guests matching the search criteria with status indicating
              success or failure of the search operation
    """
    
    
    query_params = {
        'SearchValue': search_value
    }
    
    # Prepare headers with bearer token
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Make the HTTP request
    url = f'{HOST}/api/guests/search'
    
    try:
        response = requests.get(url, params=query_params, headers=headers)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        # Parse the response
        data = response.json()
        guests = data.get('Guests', [])
        
        # Store the raw guests data in state for later use
        tool_context.state['guests_raw'] = guests
        
        return {
            'status': 'success',
            'guests': guests,
            'total_count': len(guests)
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'error_message': f'Failed to search guests: {str(e)}'
        }


async def select_guest(
    guest_id: str,
    tool_context: ToolContext
) -> dict:
    """Select a specific guest by their ID from previously fetched guests.
    
    This tool retrieves the guest details from previously searched guests
    and stores the selected guest in the state for further processing.
    
    Args:
        guest_id (str): The ID of the guest to select
    
    Returns:
        dict: Information about the selected guest with status
              indicating if the guest was found
    """
    # Get previously stored guests
    guests = tool_context.state.get('guests_raw', [])
    
    if not guests:
        return {
            'status': 'error',
            'error_message': 'No guests available. Please search for guests first.'
        }
    
    # Find the guest with the matching ID
    selected_guest = None
    for guest in guests:
        if guest.get('Id') == guest_id:
            selected_guest = guest
            break
    
    # Store the selected guest and return appropriate response
    if selected_guest:
        tool_context.state['selected_guest'] = selected_guest
        print(f"Selected guest: {selected_guest}")
        return {
            'status': 'success',
            'guest': selected_guest
        }
    else:
        return {
            'status': 'error',
            'error_message': f'Guest with ID {guest_id} not found.'
        }


root_agent = Agent(
    name="service_search_agent",
    model="gemini-2.0-flash-exp",
    description=(
        "Agent to search for services and guests and select them"
    ),
    instruction=(
        "You are a helpful agent who can search for services and guests. "
        "You get the service name or guest details from the user. "
        "You can select a service from the list of services. "
        "You can select a guest from the list of guests. "
        "You are done when you have selected both a service and a guest"
    ),
    tools=[search_services, select_service, search_guests, select_guest],
)






APP_NAME = "stock_app"
USER_ID = "1234"
SESSION_ID = "session1234"



# Session and Runner
# session_service = InMemorySessionService()
# session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
# runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


# # Agent Interaction
# def call_agent(query):
#     content = types.Content(role='user', parts=[types.Part(text=query)])
#     events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

#     for event in events:
#         if event.is_final_response():
#             final_response = event.content.parts[0].text
#             print("Agent Response: ", final_response)

# call_agent("search for haircut services")
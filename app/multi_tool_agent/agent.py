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

async def create_guest(
    tool_context: ToolContext,
    first_name: str,
    last_name: str,
    username: str,
    email: str,
    phone_number: str = "",
    gender: int = 0,
    date_of_birth: str = ""
) -> dict:
    """Create a new guest with the provided details.
    
    This tool creates a new guest in the Zenoti system with the provided details.
    
    Args:
        first_name (str): Guest's first name
        last_name (str): Guest's last name
        username (str): Guest's username
        email (str): Guest's email address
        phone_number (str, optional): Guest's phone number
        gender (int, optional): Guest's gender (0: Not specified, 1: Male, 2: Female). Default is 0.
        date_of_birth (str, optional): Guest's date of birth in YYYY-MM-DD format
    
    Returns:
        dict: Information about the created guest with status indicating success or failure
    """
    
    # Create the API endpoint URL
    url = f'{HOST}/api/Guests/Add'
    
    # Create mobile phone model if phone number is provided
    mobile_phone_model = None
    if phone_number:
        mobile_phone_model = {
            "Number": phone_number,
            "DisplayNumber": phone_number
        }
    
    # Prepare the payload
    payload = {
        "CenterId": app_context['center_id'],
        "Guest": {
            "Id": None,
            "FirstName": first_name,
            "LastName": last_name,
            "Code": None,
            "Username": username,
            "PostalCode": None,
            "Address1": None,
            "City": None,
            "State": None,
            "Country": None,
            "DOB_IncompleteYear": None,
            "DateOfBirth": date_of_birth,
            "IsMinors": date_of_birth and (
                datetime.datetime.strptime(date_of_birth, "%Y-%m-%d").date() > 
                (datetime.datetime.now() - datetime.timedelta(days=365*18)).date()
            ),
            "AnniversaryDate": None,
            "Email": email,
            "Room": None,
            "Gender": gender,
            "MobileNumber": phone_number,
            "MobilePhoneModel": mobile_phone_model,
            "WorkPhone": None,
            "WorkPhoneModel": None,
            "HomePhone": None,
            "HomePhoneModel": None,
            "RelationshipManager": None,
            "Nationality": None,
            "ReferralSource": None,
            "ReferredGuestId": None,
            "ReceiveMarketingSMS": False,
            "ReceiveTransactionalSMS": True,
            "ReceiveTransactionalEmail": True,
            "ReceiveMarketingEmail": False,
            "ReceiveLPStmt": True,
            "OptInForLoyaltyProgram": True,
            "PreferredPronounId": None,
            "PreferredPronoun": None,
            "GuestMarketingLoyaltyOptIn": False
        },
        "Validate": True
    }
    
    # Prepare headers with bearer token
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Make the API request
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        # Parse the response
        data = response.json()
        
        # Check for errors in the response
        if data.get('Error'):
            return {
                'status': 'error',
                'error_message': f'API error: {data.get("Error")}'
            }
        
        # Create a summary of the created guest
        created_guest = {
            'guestId': data.get('GuestId'),
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'phoneNumber': phone_number,
            'username': username,
            'gender': 'Male' if gender == 1 else 'Female' if gender == 2 else 'Not specified',
            'dateOfBirth': date_of_birth
        }
        
        # Store the created guest in state
        tool_context.state['created_guest'] = created_guest
        tool_context.state['selected_guest'] = created_guest
        
        return {
            'status': 'success',
            'message': f'Guest {first_name} {last_name} created successfully',
            'guest': created_guest
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'error_message': f'Failed to create guest: {str(e)}'
        }


async def get_guest_mandatory_fields(
    tool_context: ToolContext
) -> dict:
    """Get the mandatory fields required for guest creation from the organization settings.
    
    This tool fetches organization settings and extracts which fields are mandatory
    when creating a new guest, helping to guide the user through the guest creation process.
    
    Returns:
        dict: A dictionary containing mandatory fields and other relevant guest settings
    """
    
    # Create the API endpoint URL
    url = f'{HOST}/v1/organizations/settings/all'
    
    # Prepare headers with bearer token
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Make the API request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        # Parse the response
        data = response.json()
        
        # Extract guest mandatory fields
        mandatory_fields = []
        is_mobile_required = False
        other_settings = {}
        
        if data and 'guest' in data:
            # Get mandatory fields array
            if 'guest_manadatory_fields' in data['guest'] and isinstance(data['guest']['guest_manadatory_fields'], list):
                mandatory_fields = data['guest']['guest_manadatory_fields']
            
            # Check if mobile number is mandatory
            if 'is_mobile_number_mandatory' in data['guest']:
                is_mobile_required = data['guest']['is_mobile_number_mandatory']
            
            # Get other relevant guest settings
            other_settings = {
                'enforceMandatoryFields': data['guest'].get('enforce_guest_fields', False),
                'checkMinorAge': data['guest'].get('Check_Minor_Age', False),
                'minorAge': data['guest'].get('Minor_Age', 18),
                'allowSameEmail': data['guest'].get('Allow_Guest_With_Same_Email_Address', False),
                'allowSameMobile': data['guest'].get('Allow_Guest_With_Same_Mobile', False),
                'enableOtherGender': data['guest'].get('Enable_Other_Gender', False)
            }
        
        # Format the fields in a more human-readable way
        formatted_fields = []
        for field in mandatory_fields:
            if field == "dob":
                formatted_fields.append("Date of Birth")
            elif field == "email":
                formatted_fields.append("Email")
            elif field == "gender":
                formatted_fields.append("Gender")
            elif field == "mobile":
                formatted_fields.append("Mobile Number")
            elif field == "username":
                formatted_fields.append("Username")
            else:
                # Capitalize the field name
                formatted_fields.append(field.capitalize())
        
        if is_mobile_required and "Mobile Number" not in formatted_fields:
            formatted_fields.append("Mobile Number")
        
        # Store the fields in state for future reference
        tool_context.state['mandatory_fields'] = formatted_fields
        tool_context.state['raw_mandatory_fields'] = mandatory_fields
        tool_context.state['is_mobile_required'] = is_mobile_required
        tool_context.state['guest_settings'] = other_settings
        
        return {
            'status': 'success',
            'mandatoryFields': formatted_fields,
            'rawMandatoryFields': mandatory_fields,
            'isMobileRequired': is_mobile_required,
            'otherSettings': other_settings
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'error_message': f'Failed to fetch mandatory fields: {str(e)}'
        }


async def reserve_service_slot(
    slot_time: str,
    tool_context: ToolContext
) -> dict:
    """Reserve a slot for a service appointment.
    
    This tool reserves a time slot for the previously selected service and guest.
    It requires that both a service and guest have been selected using the 
    select_service and select_guest tools first.
    
    Args:
        slot_time (str): The time slot to reserve in format 'YYYY-MM-DD HH:MM:SS'
    
    Returns:
        dict: Information about the reservation with status indicating success or failure
    """
    # Get previously selected guest and service from state
    selected_guest = tool_context.state.get('selected_guest')
    selected_service = tool_context.state.get('selected_service')
    
    # Validate that both guest and service are selected
    if not selected_guest:
        return {
            'status': 'error',
            'error_message': 'No guest selected. Please select a guest first.'
        }
    
    if not selected_service:
        return {
            'status': 'error',
            'error_message': 'No service selected. Please select a service first.'
        }
    
    # Get guest ID from selected guest
    guest_id = selected_guest.get('Id') or selected_guest.get('guestId')
    if not guest_id:
        return {
            'status': 'error',
            'error_message': 'Invalid guest information. Missing guest ID.'
        }
    
    # Create the API endpoint URL
    url = f'{HOST}/api/v2.0/Appointments/ReserveSlots'
    
    # Center ID from app context
    center_id = app_context['center_id']
    therapist_id = app_context['therapist_id']
    
    # Create the service object from the selected service
    service_object = selected_service
    
    # Extract date for center time (use slot_time if provided)
    center_time = slot_time
    
    # Create full payload
    payload = {
        "CouplesService": False,
        "CenterId": center_id,
        "ReservationId": None,
        "SlotBookings": [
            {
                "GuestId": guest_id,
                "VirtualGuest": {
                    "FirstName": None,
                    "LastName": None,
                    "Mobile": None,
                    "Gender": None,
                },
                "AppointmentGroupId": None,
                "waitlist_group_id": None,
                "quote_pk": None,
                "RemoveBuddyServiceFinishSegment": True,
                "SkipAutoOrderingOfServices": False,
                "email_link": None,
                "sms_link": None,
                "appointment_category_id": None,
                "waitlist_id": None,
                "SlotBookingIdentifier": "appointment_1",
                "TherapistId": therapist_id,
                "BookingNotes": "",
                "PreferredTime": None,
                "Price": None,
                "ConsiderSingleTherapistSlot": True,
                "Services": [
                    {
                        "OrderNo": 2,
                        "CoupleGroupNo": 1,
                        "CoupleGroupId": None,
                        "AppointmentId": None,
                        "InvoiceItemId": None,
                        "UIItemIdentifier": "appointment_1#item_2",
                        "CartItemId": None,
                        "Lock": False,
                        "PackageId": None,
                        "PkgGroupNo": None,
                        "Service": service_object,
                        "ResetIfTherapistCanNotDoService": False,
                        "StartTime": slot_time,
                        "StartTimeInCenter": None,
                        "EndTime": None,
                        "EndTimeInCenter": None,
                        "RequestedDuration": None,
                        "RequestedTherapistGender": 3,
                        "RequestedTherapist": {
                            "Id": therapist_id
                        },
                        "RequestedParallelGroupFk": None,
                        "Room": None,
                        "Equipment": None,
                        "AssignDefaultSlot": True,
                        "FillOpenSlots": False,
                        "AppointmentSource": 0,
                        "Do_Not_Reprocess_Therapist": True,
                        "IsGuestSpecificDuration": False,
                        "isGuestSpecificPriceUpdated": False,
                        "QuoteItemPk": None,
                        "is_flexi_day_package": False,
                        "is_service_bundle_day_package": False,
                        "service_bundle_day_package_id": None,
                        "service_bundle_day_package_group_no": None,
                        "service_bundle_package_no": 1,
                    },
                ],
            },
        ],
        "CenterTime": center_time,
        "BookingSource": 2,
        "IsNoncontiguousSlots": False,
        "ConsiderOnlyCheckedInEmployees": False,
        "WaitlistGroupId": None,
    }
    
    # Prepare headers with bearer token
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Make the API request
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        # Parse the response
        data = response.json()
        
        # Store the reservation data in state
        tool_context.state['reservation_data'] = data
        
        # Check if the reservation was successful
        if data.get('Error'):
            return {
                'status': 'error',
                'error_message': f'API error: {data.get("Error")}'
            }
        
        return {
            'status': 'success',
            'message': f'Appointment slot reserved successfully',
            'reservation_details': data
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'error_message': f'Failed to reserve slot: {str(e)}'
        }


root_agent = Agent(
    name="service_search_agent",
    model="gemini-2.0-flash-exp",
    description=(
        "Agent to search for services and guests and select them and also create a new guest if the guest is not in the system"
    ),
    instruction=(
        "You are a helpful agent who can search for services and guests. "
        "You get the service name or guest details from the user. "
        "You can select a service from the list of services. "
        "You can select a guest from the list of guests. "
        "You can reserve a slot for a service appointment once both a service and guest are selected. "
        "You are done when you have successfully reserved a slot."
        "You can also create a new guest if the guest is not in the system. You have to ask the user for the guest details and then create the guest using the create_guest tool."
        "You can also get the mandatory fields required for guest creation from the organization settings using the get_guest_mandatory_fields tool."
    ),
    tools=[search_services, select_service, search_guests, select_guest, create_guest, get_guest_mandatory_fields, reserve_service_slot],
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
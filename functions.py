import json
import os
from openai import OpenAI
import requests
from dotenv import load_dotenv
from prompts import assistant_instructions

from slack_app import app

load_dotenv()

client = OpenAI()

AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
HR_CHANNEL_ID = os.environ["HR_CHANNEL_ID"]
TABLE_URL = "YOUR_TABLE_URL"


# Save new ticket to Airtable
def create_new_ticket(arguments, created_by):
    url = TABLE_URL
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "records": [
            {
                "fields": {
                    "Title": arguments["ticket_title"],
                    "Details": arguments["ticket_details"],
                    "Priority": arguments["priority"],
                    "Created By": created_by,
                },
            },
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Ticket has been submitted generated.")
        send_new_ticket_message_to_hr_channel(data["records"][0]["fields"])
        return response.json()
    else:
        print(f"Failed to create new Ticket: {response.text}")
        return f"Failed to create new Ticket: {response.text}"


# Fetch All Pending Tickets from the Airtable
def get_all_tickets(channel_id):
    if channel_id != HR_CHANNEL_ID:
        return "You are not Authorized for this only HR personal can see the Tickets"

    url = TABLE_URL
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    }

    # Define the filter formula to get only 'Pending' status records
    query_params = {"filterByFormula": "({Status} = 'Pending')"}

    response = requests.get(url, headers=headers, params=query_params)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to fetch Tickets: {response.text}"


# Update the Status of ticket from Pending to Done
def update_ticket_status(title, channel_id, thread_ts):
    if channel_id != HR_CHANNEL_ID:
        return "You are not Authorized for this only HR personal can update the status of Tickets"
    # Step 1: Fetch the Record ID
    url = TABLE_URL
    query_params = {
        "filterByFormula": f"AND({{Title}} = '{title}', {{Status}} = 'Pending')"
    }
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }

    get_response = requests.get(url, headers=headers, params=query_params)
    if get_response.status_code != 200:
        return f"Failed to retrieve record: {get_response.text}"

    records = get_response.json().get("records", [])
    if not records:
        return "No Ticket found with the given title."

    record_id = records[0]["id"]

    app.client.chat_postMessage(
        channel=channel_id,
        text="Updating the Ticket...",
        thread_ts=thread_ts,
    )

    # Step 2: Update the Record
    data = {
        "records": [
            {
                "id": record_id,
                "fields": {
                    "Status": "Done",
                },
            }
        ]
    }

    response = requests.patch(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return f"Ticket Status of {title} has been Successfully updated to Done"
    else:
        return f"Failed to update ticket: {response.text}"


def send_new_ticket_message_to_hr_channel(data):
    try:
        title = data.get("Title", "N/A")
        created_by = data.get("Created By", "N/A")
        details = data.get("Details", "N/A")
        priority = data.get("Priority", "N/A")

        message = f'There is a new ticket \'"{title}"\' created by "{created_by}" with details: "{details}" and its priority is "{priority}".'

        app.client.chat_postMessage(channel=HR_CHANNEL_ID, text=message)

    except Exception as e:
        print(f"Error sending message to HR channel: {e}")
        return None


def create_assistant():
    assistant_file_path = "assistant.json"

    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, "r") as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data["assistant_id"]
            print("Loaded existing assistant ID.")
    else:
        assistant = client.beta.assistants.create(
            instructions=assistant_instructions,
            name="Slackbot HR-Assistant",
            model="gpt-4-1106-preview",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "create_new_ticket",
                        "description": "Initiate a new Ticket by providing the title, details, and urgency level of the request.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "ticket_title": {
                                    "type": "string",
                                    "description": "A concise title summarizing the nature of the Ticket.",
                                },
                                "ticket_details": {
                                    "type": "string",
                                    "description": "Elaborate details outlining the specifics of the Ticket.",
                                },
                                "priority": {
                                    "type": "string",
                                    "enum": ["Low", "Medium", "High"],
                                    "description": "The urgency level of the Ticket, which helps in prioritizing its execution. Available options are 'Low', 'Medium', and 'High'.",
                                },
                            },
                            "required": [
                                "ticket_title",
                                "ticket_details",
                                "priority",
                            ],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_all_tickets",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": [],
                        },
                        "description": """Retrieves a list of all Pending Tickets from the database. 
                This function is designed for HR personnel only to view and address outstanding related 
                inquiries and tasks. Display only Title, Details, Status and Priority and Created By.""",
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "update_ticket_status",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "The title of the Ticket to be updated.",
                                }
                            },
                            "required": ["title"],
                        },
                        "description": """This function updates the status of a Ticket to 'Done'. 
                It identifies the specific Ticket by its title from the list of pending requests 
                and updates its status in the database.""",
                    },
                },
            ],
        )

        with open(assistant_file_path, "w") as file:
            json.dump({"assistant_id": assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id

import requests
import json
import os

# API Key (get it securely, e.g., from environment variables)
api_key = os.environ.get('fs_api_key')
if not api_key:
    raise ValueError("fs_api_key environment variable not set.")

# Static variables
base_url = 'https://pacs.freshservice.com'
api_password = 'x'
group_id = 21000562401
responder_id = 21002944650
email = 'phone_call@email.com'
line_break = "\n"
issue_type = "Other"
category = "Other"

def create_ticket(full_name, incoming_phone_number, issue_type, category, group_id, responder_id, email):
    url = f"{base_url}/api/v2/tickets"
    headers = {'Content-Type': 'application/json'}

    ticket_data = {
        'category': category,
        'email': email,
        'status': 2,
        'priority': 1,
        'source': 3,
        'subject': f'{full_name} | Phone Call, {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")}',
        'description': f"{full_name} | Phone Call, {datetime.datetime.now().strftime('%m/%d/%Y, %H:%M')}",
        'workspace_id': 11,
        'group_id': group_id,
        'responder_id': responder_id,
        'custom_fields': {
            'issuetype': issue_type,
            'user_phone_number': incoming_phone_number
        }
    }
    data = json.dumps(ticket_data)

    try:
        response = requests.post(url, auth=(api_key, api_password), headers=headers, data=data)
        response.raise_for_status()

        ticket_number = response.json()['ticket']['id']
        return ticket_number

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error creating ticket: {str(e)}\n{response.text}")


def start_timer(ticket_number):
    url = f"{base_url}/api/v2/tickets/{ticket_number}/time_entries"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        'time_entry': {
            'timer_running': 'true',
            'agent_id': responder_id,
            'billable': True,
        }
    })

    try:
        response = requests.post(url, auth=(api_key, api_password), headers=headers, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error starting timer: {str(e)}\n {response.text}")


def stop_timer(ticket_number):
    url = f"{base_url}/api/v2/tickets/{ticket_number}/time_entries"
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.get(url, auth=(api_key, api_password), headers=headers)
        response.raise_for_status()

        time_entry_data = response.json()

        if time_entry_data and 'time_entries' in time_entry_data:
            time_entries = time_entry_data['time_entries']
            for entry in time_entries:
                if entry['timer_running']:
                    time_entry_id = entry['id']
                    stop_url = f"{base_url}/api/v2/tickets/{ticket_number}/time_entries/{time_entry_id}"
                    data = {'timer_running': False}
                    response = requests.put(stop_url, auth=(api_key, api_password), headers=headers, json=data)
                    response.raise_for_status()

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error stopping timer: {str(e)}{response.text}")


def get_departments():
    all_departments = []
    all_dept_ids = []
    page = 1
    per_page = 100

    while True:
        departments_url = f"{base_url}/api/v2/departments?page={page}&per_page={per_page}"
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.get(departments_url, auth=(api_key, api_password), headers=headers)
            response.raise_for_status()

            departments_data = response.json()
            departments = departments_data.get('departments', [])

            if not departments:
                break

            all_departments.extend([dept['name'] for dept in departments])
            all_dept_ids.extend([dept['id'] for dept in departments])

            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching departments: {e}\n{response.text}")
            break

    return all_departments, all_dept_ids
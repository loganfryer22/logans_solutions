import requests
import sys
import json
import datetime
import tkinter as tk
from tkinter import messagebox

# API Key
secret_file = 'C:\\Users\\logan.fryer\\OneDrive - PACS\\Documents\\Misc\\my_api_key.txt'
with open(secret_file, "r") as f:
    secret_key = f.read().strip()
    f.close()

# static variables
domain = 'https://pacs.freshservice.com'
api_key = secret_key
password = 'x'
group_id = 21000562406
responder_id = 21002944650
email = 'phone_call@email.com'

# RC args
# incoming_phone_number = sys.argv[1]
incoming_phone_number = '987654321'
# incoming_first_name = sys.argv[2]
incoming_first_name = 'First'
# incoming_last_name = sys.argv[3]
incoming_last_name = 'Last'


# create the ticket
ticket_url = f"{domain}/api/v2/tickets"
ticket_headers = {'Content-Type': 'application/json'}
ticket_data = json.dumps({
    'category': "Other",
    'email': email,
    'status': 2,
    'priority': 1,
    'source': 3,
    'subject': (f'{incoming_first_name} {incoming_last_name} | Phone Call, {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")}'),
    'description': (f"{incoming_first_name} {incoming_last_name} | Phone Call, {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")}"),
    'workspace_id': 11,
    'group_id': group_id,
    'responder_id': responder_id,
    'custom_fields': {
        'issuetype': 'Other'
    }
})

# Send request to create ticket
try:
    ticket_response = requests.post(ticket_url, auth=(api_key, password), headers=ticket_headers, data=ticket_data)
    ticket_response.raise_for_status()  # Raise exception for error responses

    # Extract ticket number
    ticket_number = ticket_response.json()['ticket']['id']

except requests.exceptions.RequestException as e:
    messagebox.showerror("Error", f"Error creating ticket: {str(e)}")

def start_timer(ticket_number):
    url = f"{domain}/api/v2/tickets/{ticket_number}/time_entries"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        'time_entry': {
            'timer_running': 'true',
            'agent_id': responder_id,
            'billable': True,
      }
  })

    # Send request to start timer
    try:
        response = requests.post(url, auth=(api_key, password), headers=headers, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error starting timer: {str(e)}")

# submit notes
def submit_note(body):
    ticket_url = f"{domain}/api/v2/tickets/{ticket_number}/notes"
    ticket_headers = {'Content-Type': 'application/json'}
    ticket_data = json.dumps({
        "private": True,
        "body": f"{body}"

    })

    # Send request to create ticket
    try:
        ticket_response = requests.post(ticket_url, auth=(api_key, password), headers=ticket_headers, data=ticket_data)
        ticket_response.raise_for_status()  # Raise exception for error responses
        root.destroy() # exits out of the gui
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error creating ticket: {str(e)}")

# start the timer
start_timer(ticket_number)

# Create the main window
root = tk.Tk()
root.geometry('400x400')
root.overrideredirect(True)

# Create the title bar
title_bar = tk.Frame(root, bg="purple")

# Add elements to the title bar
title_label = tk.Label(title_bar, text="RC/FS Call Tool", font=("Arial", 12))
title_label.pack(side=tk.RIGHT)

# Position the title bar
title_bar.pack(fill=tk.X)

# Create the main content area
content_frame = tk.Frame(root)
content_frame.pack(fill=tk.BOTH, expand=True)

# Bind mouse motion events to the title bar
def move_window(event):
    root.geometry(f"+{event.x_root}+{event.y_root}")

title_bar.bind("<Button1-Motion>", move_window)

# label for ticket number enrty
ticket_number_label = tk.Label(root, text=f"Ticket number")
ticket_number_label.pack()
ticket_number_entry = tk.Label(root, text=f"{ticket_number}")
ticket_number_entry.pack()

# label for phone number arg:
arg_label = tk.Label(root, text="Phone Number:" )
arg_label.pack()
arg_text = tk.Label(root, text=f"{incoming_phone_number}")
arg_text.pack()

# label for full name arg
arg_label = tk.Label(root, text="Full Name:")
arg_label.pack()
arg_text = tk.Label(root, text=f"{incoming_first_name} {incoming_last_name}")
arg_text.pack()

# text box for notes
text_label = tk.Label(root, text="Notes:")
text_label.pack()
text_text = tk.Text(root, width=30, height=10)
text_text.pack()

# Button to submit notes ticket
start_button = tk.Button(root, text="Submit", command=lambda: submit_note(text_text.get('1.0', tk.END)))
start_button.pack()

# Keep the window open
root.mainloop()
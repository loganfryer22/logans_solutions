import requests
import sys
import json
import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

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
line_break = "\n"


### RC args ###
# incoming_phone_number = sys.argv[1]
incoming_phone_number = '987654321'
# incoming_first_name = sys.argv[2]
incoming_first_name = 'First'
# incoming_last_name = sys.argv[3]
incoming_last_name = 'Last'
ticket_number = '486448'

# create the ticket
def create_ticket():
    ticket_url = f"{domain}/api/v2/tickets"
    ticket_headers = {'Content-Type': 'application/json'}
    ticket_data = json.dumps({
        'category': "Other",
        'email': email,
        'status': 2,
        'priority': 1,
        'source': 3,
        'subject': (f'{incoming_first_name} {incoming_last_name} | Phone Call,'
                    f' {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")}'),
        'description': (f"{incoming_first_name} {incoming_last_name} | Phone Call,"
                        f" {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")}"),
        'workspace_id': 11,
        'group_id': group_id,
        'responder_id': responder_id,
        'custom_fields': {
            'issuetype': 'Other',
            'user_phone_number': incoming_phone_number

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
        messagebox.showerror("Error", f"Error starting timer: {str(e)}\n {response.text}")

# function to override the passed phone number arg
def phone_number_override():
    override_number = number_override_text.get("1.0", tk.END).strip()
    if override_number == '':
        return
    else:
        ticket_url = f"{domain}/api/v2/changes/{ticket_number}"
        ticket_headers = {'Content-Type': 'application/json'}
        ticket_data = json.dumps({
            'custom_fields': {
                'phone_number': override_number
            }
        })

        # Send put request to changes endpoint to adjust the phone number
        try:
            response = requests.put(ticket_url, auth=(api_key, password), headers=ticket_headers,
                                                data=ticket_data)
            response.raise_for_status()  # Raise exception for error responses
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Error creating ticket: {str(e)}\n{response.text}")

# submit notes
def submit_note(body):
    ticket_url = f"{domain}/api/v2/tickets/{ticket_number}/notes"
    ticket_headers = {'Content-Type': 'application/json'}
    formatted_body = body.replace('\n', '<br>')
    enter = line_break.replace('\n', '<br>')
    ticket_data = json.dumps({
        "private": True,
        "body": f"Agent Notes:{enter}{formatted_body}",
    })

    # Send request to submit private note
    try:
        response = requests.post(ticket_url, auth=(api_key, password), headers=ticket_headers, data=ticket_data)
        response.raise_for_status()  # Raise exception for error responses
        root.destroy() # exits out of the gui
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error creating ticket: {str(e)}\n {response.text}")

    # Run the override phone number function
    phone_number_override() #### I Do Not Have Permissions for this endpoint

# Function to run all start functions
def run_all():
    create_ticket()
    start_timer(ticket_number)

# Create the main window
root = tk.Tk()
root.title("RC/FS Call Tool")
root.geometry('600x600')
root.overrideredirect(True)

# Style for themed widgets
style = ttk.Style()
style.theme_use('clam')

# Create the title bar
title_bar = ttk.Frame(root, style='Titlebar.TFrame')
title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

# Configure the title bar style
style.configure('Titlebar.TFrame', background='Purple')

# Load and display the icon
# icon_image = Image.open('icon.png')
# icon_photo = ImageTk.PhotoImage(icon_image.resize((24, 24)))
# icon_label = tk.Label(title_bar, image=icon_photo, bg="#2980b9")
# icon_label.image = icon_photo
# icon_label.grid(row=0, column=0, padx=5, pady=5)

# Title label
title_label = ttk.Label(title_bar, text="RC/FS Enhanced Call App   PACS",
                        font=("Helvetica", 14, "bold"), background='Purple', foreground='white')
title_label.grid(row=0, column=1, padx=10, pady=5)

# Bind mouse events to the title bar for dragging
def start_move(event):
    root.x = event.x
    root.y = event.y

def move_window(event):
    x = root.winfo_x() - root.x + event.x
    y = root.winfo_y() - root.y + event.y
    root.geometry(f"+{x}+{y}")

# Bind to the title bar
title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<B1-Motion>", move_window)

# Bind to the title label
title_label.bind("<ButtonPress-1>", start_move)
title_label.bind("<B1-Motion>", move_window)

# Main content area
content_frame = ttk.Frame(root, padding=10)
content_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Ticket number label and display
ticket_number_label = ttk.Label(content_frame, text="Ticket Number:")
ticket_number_label.grid(row=0, column=0, sticky="w")
ticket_number_entry = ttk.Label(content_frame, text=ticket_number)
ticket_number_entry.grid(row=0, column=1, sticky="e")

# Phone number label and display
incoming_phone_number_label = ttk.Label(content_frame, text="Phone Number:")
incoming_phone_number_label.grid(row=1, column=0, sticky="w")
incoming_phone_number_text = ttk.Label(content_frame, text=incoming_phone_number)
incoming_phone_number_text.grid(row=1, column=1, sticky="e")

# Full name label and display
full_name_label = ttk.Label(content_frame, text="Full Name:")
full_name_label.grid(row=2, column=0, sticky="w")
full_name_text = ttk.Label(content_frame, text=f"{incoming_first_name} {incoming_last_name}")
full_name_text.grid(row=2, column=1, sticky="e")

# Notes label and text box
text_label = ttk.Label(content_frame, text="Notes:")
text_label.grid(row=3, column=0, sticky="w")
text_text = tk.Text(content_frame, width=35, height=10, wrap="word")
text_text.grid(row=4, column=0, columnspan=2, pady=5)

# Phone number override text box
number_override_text = tk.Text(content_frame, width=15, height=1, wrap="word")
number_override_text.grid(row=1, column=2, sticky="e")

# Submit button
start_button = ttk.Button(content_frame, text="Submit",
                          command=lambda: submit_note(text_text.get('1.0', tk.END)))
start_button.grid(row=5, column=0, columnspan=2, pady=10)

# Configure grid weights for resizing
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# run functions and keep gui open
# run_all()
root.mainloop()
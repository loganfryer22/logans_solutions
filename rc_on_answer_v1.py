import sys
import os
import requests
import json
import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

# API Key
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

# Global Variables
all_department_ids = []
all_department_names = []
selected_facility_name = ""
override_number = ""

### RC args ###
incoming_phone_number = sys.argv[1]
incoming_first_name = sys.argv[2]
incoming_last_name = sys.argv[3]
full_name = f"{incoming_first_name} {incoming_last_name}"
ticket_number = ''
# incoming_phone_number = '987654321'
# incoming_first_name = 'First'
# incoming_last_name = 'Last'
# ticket_number = '518178'
# full_name = f"{incoming_first_name} {incoming_last_name}"



# functions to Bind mouse events for dragging
def start_move(event):
    root.x = event.x
    root.y = event.y
def move_window(event):
    x = root.winfo_x() - root.x + event.x
    y = root.winfo_y() - root.y + event.y
    root.geometry(f"+{x}+{y}")

# Create the ticket
def create_ticket():
    global ticket_number
    url = f"{base_url}/api/v2/tickets"
    headers = {'Content-Type': 'application/json'}

    ticket_data = {
        'category': category,
        'email': email,
        'status': 2,
        'priority': 1,
        'source': 3,
        'subject': f'{full_name} | Phone Call, {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")}',
        'description': f"{incoming_first_name} {incoming_last_name} | Phone Call, {datetime.datetime.now().strftime('%m/%d/%Y, %H:%M')}",
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

# function to start the timer
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

    # Send request to start timer
    try:
        response = requests.post(url, auth=(api_key, api_password), headers=headers, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error starting timer: {str(e)}\n {response.text}")

# function to stop the timer
def stop_timer(ticket_number):
    url = f"{base_url}/api/v2/tickets/{ticket_number}/time_entries"
    headers = {'Content-Type': 'application/json'}

    try:
        # Fetch time entries for the ticket
        response = requests.get(url, auth=(api_key, api_password), headers=headers)
        response.raise_for_status()

        # Extract time entry data
        time_entry_data = response.json()

        # Check if any timers are running
        if time_entry_data and 'time_entries' in time_entry_data:
            time_entries = time_entry_data['time_entries']

            # Loop through each time entry and stop running timers
            for entry in time_entries:
                if entry['timer_running']:  # Check if timer is running
                    time_entry_id = entry['id']
                    stop_url = f"{base_url}/api/v2/tickets/{ticket_number}/time_entries/{time_entry_id}"
                    data = {'timer_running': False}

                    # Send PUT request to stop the timer
                    response = requests.put(stop_url, auth=(api_key, api_password), headers=headers, json=data)
                    response.raise_for_status()

    # error catch message box
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error stopping timer: {str(e)}{response.text}")

# function to override the passed phone number arg
def phone_number_override():
    global override_number
    override_number = number_override_text.get("1.0", tk.END).strip()
    if override_number == '':
        return
    else:
        ticket_url = f"{base_url}/api/v2/tickets/{ticket_number}"
        ticket_headers = {'Content-Type': 'application/json'}
        ticket_data = json.dumps({
            'custom_fields': {
                'user_phone_number': override_number
            }
        })


        # Send put request to changes endpoint to adjust the phone number
        try:
            response = requests.put(ticket_url, auth=(api_key, api_password), headers=ticket_headers,
                                                data=ticket_data)
            response.raise_for_status()  # Raise exception for error responses
            return override_number
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Error creating ticket: {str(e)}\n{response.text}")

# Submit/Continue function, Submits all notes and adjustments to the ticket and closes the ticket out
def submit_and_continue(body):
    # run phone number override function
    phone_number_override()

    # get facility name, forced
    selected_facility_id = selected_facility()
    if selected_facility_id is None:
        messagebox.showerror("Error", "Please select a valid facility before submitting.")
        return

    ticket_url = f"{base_url}/api/v2/tickets/{ticket_number}/notes"
    ticket_headers = {'Content-Type': 'application/json'}
    formatted_body = body.replace('\n', '<br>')
    enter = line_break.replace('\n', '<br>')
    ticket_data = json.dumps({
        "private": True,
        "body": f"Agent Notes:{enter}{formatted_body}",
    })

    # Update ticket properties
    update_url = f"{base_url}/api/v2/tickets/{ticket_number}"
    update_headers = {'Content-Type': 'application/json'}
    update_data = json.dumps({
        'group_id': group_id,
        'department_id': selected_facility_id,
        'user_phone_number': phone_number_override,

    })

    try:
        # api request for updated url data
        update_response = requests.put(update_url, auth=(api_key, api_password), headers=update_headers,
                                       data=update_data)
        update_response.raise_for_status()

        # note response data
        response = requests.post(ticket_url, auth=(api_key, api_password), headers=ticket_headers, data=ticket_data)
        response.raise_for_status()  # Raise exception for error responses
        root.destroy() # exits out of the gui

    except requests.exceptions.RequestException as e:
        # catch errors from either the status update or the note submission
        if e.response is not None:
            error_message = f"Error updating ticket or submitting note: {str(e)}\n{e.response.text}"
        else:
            error_message = f"Error updating ticket or submitting note: {str(e)}"
        messagebox.showerror("Error", error_message)

# Submit/close function, Submits all notes and adjustments to the ticket and closes the ticket out (unfinished)
def submit_and_close():
    # TODO: Implement logic to close the ticket
    root.destroy() # destroys the gui/ quits application

# Function to submit all notes and adjustments but places the ticket on hold/stop timer (unfinished)
def submit_and_hold(body):

    # Create a new window for the text box
    text_box_window = tk.Toplevel(root)
    text_box_window.title("Submit/Hold Reason")
    text_box_window.geometry('300x150')

    # Label for instructions or context
    reason_label = tk.Label(text_box_window, text="Please state a reason this ticket is on hold:")
    reason_label.pack()

    # Combobox for issue types
    reason_text = tk.Text(text_box_window, height=3, width=30)
    reason_text.pack()

    def _submit_and_hold():
        phone_number_override()

        selected_facility_id = selected_facility()
        if selected_facility_id is None:
            messagebox.showerror("Error", "Please select a valid facility before submitting.")
            return

        # get reason text box text and set to variable
        reason = reason_text.get('1.0', tk.END).strip()

        # note data
        note_url = f"{base_url}/api/v2/tickets/{ticket_number}/notes"
        note_headers = {'Content-Type': 'application/json'}
        formatted_body = body.replace('\n', '<br>')
        enter = line_break.replace('\n', '<br>')
        note_data = json.dumps({
            "private": True,
            "body": f"Agent Notes:{enter}{formatted_body}{enter}Reason for hold: {reason}"
        })

        # Update ticket properties
        update_url = f"{base_url}/api/v2/tickets/{ticket_number}"
        update_headers = {'Content-Type': 'application/json'}
        update_data = json.dumps({
            'group_id': group_id,
            'status': 16,
            'department_id': selected_facility_id
        })

        # Send request to submit private note and status change
        try:
            # api request for update data
            update_response = requests.put(update_url, auth=(api_key, api_password), headers=update_headers,
                                           data=update_data)
            update_response.raise_for_status()

            # api request for note data
            response = requests.post(note_url, auth=(api_key, api_password), headers=note_headers, data=note_data)
            response.raise_for_status()  # Raise exception for error responses

            # exits out of the gui
            root.destroy()

        except requests.exceptions.RequestException as e:
            # catch errors from either the update or the note submission
            if e.response is not None:
                error_message = f"Error updating ticket or submitting note: {str(e)}\n{e.response.text}"
            else:
                error_message = f"Error updating ticket or submitting note: {str(e)}"
            messagebox.showerror("Error", error_message)

        # Stop the timer
        stop_timer(ticket_number)

    # Submit Hold reason button
    submit_button = ttk.Button(text_box_window, text="Submit Reason", command=_submit_and_hold)
    submit_button.pack(padx=10, pady=10)

# function to get a list of all facility names
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

    global all_department_names
    global all_department_ids
    all_department_names = all_departments
    all_department_ids = all_dept_ids

# sets a variable for the selected facility
def selected_facility():
    global selected_facility_name
    global all_department_ids
    global all_department_names

    selected_facility_name = dept_list_dropdown_combobox.get()

    # Create a dictionary for faster lookup
    dept_name_to_id = {name: id for name, id in zip(all_department_names, all_department_ids)}

    selected_facility_id = dept_name_to_id.get(selected_facility_name)  # Get ID or None if not found
    return selected_facility_id

# function to search as you type in facility list (Needs bugs worked out)
def update_facility_dropdown_list(event=None):
    global all_department_names

    # Get the typed text
    typed_text = dept_list_dropdown_combobox.get()

    # Filter the names
    filtered_names = [name for name in all_department_names if typed_text.lower() in name.lower()]

    # Update the combobox values
    dept_list_dropdown_combobox['values'] = filtered_names

    # Only generate the <Down> event if it was a genuine key press
    if event and event.type == 'key':  # Check if it's a key press event
        dept_list_dropdown_combobox.event_generate('<Down>')

# function to close the ticket using the combobox of issue types
def assign_issue_type():
    # TODO: Implement logic to update the issue type
    global issue_type

# Function to run all start functions
def run_all():
    create_ticket()
    start_timer(ticket_number)

## lines of codes to be static ##
# Fetch departments and extract names
all_departments = get_departments()

## lines of codes to be static ##

# Create the main window
root = tk.Tk()
root.title("RC/FS Call Tool")
root.geometry('605x405')
root.overrideredirect(True) # removes default title bar
root.configure(background='purple', cursor='hand2')

# Make the GUI stay on to
root.attributes('-topmost', True)

# Style for themed widgets
style = ttk.Style()
style.theme_use('classic')

# Create the title bar
title_bar = ttk.Frame(root, style='Titlebar.TFrame')
title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

# Configure the title bar style
style.configure('Titlebar.TFrame', background='Purple')

# Load and display the icon
icon_image = Image.open("C:\\Users\\logan.fryer\\OneDrive - PACS\\Pictures\\Icons\\Screenshot 2024-09-10 004921.png")
icon_photo = ImageTk.PhotoImage(icon_image.resize((115, 34)))
icon_label = tk.Label(title_bar, image=icon_photo)
icon_label.image = icon_photo
icon_label.grid(row=0, column=0, padx=5, pady=5)

# Title label
title_label = ttk.Label(title_bar, text="RC/FS Enhanced Call App",
                        font=("Helvetica", 14, "bold"), background='Purple', foreground='white')
title_label.grid(row=0, column=1, padx=10, pady=5)

# Bind to the title bar
title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<B1-Motion>", move_window)

# Bind to the title label
title_label.bind("<ButtonPress-1>", start_move)
title_label.bind("<B1-Motion>", move_window)

# Bind to the logo
icon_label.bind("<ButtonPress-1>", start_move)
icon_label.bind("<B1-Motion>", move_window)

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
notes_label = ttk.Label(content_frame, text="Notes:")
notes_label.grid(row=3, column=0, sticky="w")
notes_text = tk.Text(content_frame, width=45, height=10, wrap="word")
notes_text.grid(row=4, column=0, columnspan=3, pady=5)

# Phone number override text box
number_override_text = tk.Text(content_frame, width=15, height=1, wrap="word")
number_override_text.grid(row=1, column=2, sticky="w")

# department list label
dept_list_label = ttk.Label(content_frame, text="Facility List:")
dept_list_label.grid(row=0, column=3, columnspan=2, sticky="s")

# department list drop down
dept_list_dropdown_combobox = ttk.Combobox(content_frame, values=all_department_names,
                                           postcommand=update_facility_dropdown_list)
dept_list_dropdown_combobox.grid(row=1, column=3, columnspan=2, pady=5, sticky="n")
dept_list_dropdown_combobox.bind("<Key>", update_facility_dropdown_list)

# Issue type label
issue_type_label = ttk.Label(content_frame, text="Issue Type:")
issue_type_label.grid(row=2, column=3, columnspan=2, sticky="s")

# Issue type drop down list
issue_type_label = ttk.Label(content_frame, text="Issue type place holder")
issue_type_label.grid(row=3, column=3, columnspan=2, sticky="n")


# Submit/Continue button
submit_and_Continue_button = ttk.Button(content_frame, text="Submit/Continue",
                                        command=lambda: submit_and_continue(notes_text.get('1.0', tk.END)))
submit_and_Continue_button.grid(row=5, column=1, columnspan=1, pady=10, sticky="s")

# Submit/Hold
submit_and_hold_button = ttk.Button(content_frame, text="Submit/Hold",
                                    command=lambda: submit_and_hold(notes_text.get('1.0', tk.END)))
submit_and_hold_button.grid(row=5, column=0, columnspan=1, pady=10, sticky="e")


# Submit/Close Button
submit_and_close_button = ttk.Button(content_frame, text="Submit/Close",
                                     command=lambda: submit_and_close())
submit_and_close_button.grid(row=5, column=2, columnspan=1, pady=10, sticky="w")

# Configure grid weights for resizing
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# run functions and keep gui open
run_all()
root.mainloop()
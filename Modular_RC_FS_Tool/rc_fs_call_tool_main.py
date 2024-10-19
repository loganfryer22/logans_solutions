import sys
import os
import datetime
import json
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import api_functions
import gui_elements
import helpers

# Global Variables
all_department_ids = []
all_department_names = []
selected_facility_name = ""
override_number = ""

### RC args ###
# incoming_phone_number = sys.argv[1]
# incoming_first_name = sys.argv[2]
# incoming_last_name = sys.argv[3]
# full_name = f"{incoming_first_name} {incoming_last_name}"
# ticket_number = ''
incoming_phone_number = '987654321'
incoming_first_name = 'First'
incoming_last_name = 'Last'
ticket_number = '518178'  # You might want to remove this if you're creating a new ticket
full_name = f"{incoming_first_name} {incoming_last_name}"


# function to override the passed phone number arg
def phone_number_override(number_override_text):
    global override_number
    override_number = number_override_text.get("1.0", tk.END).strip()
    if override_number == '':
        return
    else:
        ticket_url = f"{api_functions.base_url}/api/v2/tickets/{ticket_number}"
        ticket_headers = {'Content-Type': 'application/json'}
        ticket_data = json.dumps({
            'custom_fields': {
                'user_phone_number': override_number
            }
        })

        try:
            response = requests.put(ticket_url, auth=(api_functions.api_key, api_functions.api_password), headers=ticket_headers,
                                                data=ticket_data)
            response.raise_for_status()  # Raise exception for error responses
            return override_number
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Error creating ticket: {str(e)}\n{response.text}")


# Submit/Continue function, Submits all notes and adjustments to the ticket and closes the ticket out
def submit_and_continue(body, dept_list_dropdown_combobox, all_department_ids, all_department_names):
    # run phone number override function
    phone_number_override(number_override_text)  # Assuming number_override_text is accessible

    # get facility name, forced
    selected_facility_id = helpers.selected_facility(dept_list_dropdown_combobox, all_department_ids, all_department_names)
    if selected_facility_id is None:
        messagebox.showerror("Error", "Please select a valid facility before submitting.")
        return

    ticket_url = f"{api_functions.base_url}/api/v2/tickets/{ticket_number}/notes"
    ticket_headers = {'Content-Type': 'application/json'}
    formatted_body = body.replace('\n', '<br>')
    enter = api_functions.line_break.replace('\n', '<br>')
    ticket_data = json.dumps({
        "private": True,
        "body": f"Agent Notes:{enter}{formatted_body}",
    })

    # Update ticket properties
    update_url = f"{api_functions.base_url}/api/v2/tickets/{ticket_number}"
    update_headers = {'Content-Type': 'application/json'}
    update_data = json.dumps({
        'group_id': api_functions.group_id,
        'department_id': selected_facility_id,

    })

    try:
        # api request for updated url data
        update_response = requests.put(update_url, auth=(api_functions.api_key, api_functions.api_password),
                                       headers=update_headers,
                                       data=update_data)
        update_response.raise_for_status()

        # note response data
        response = requests.post(ticket_url, auth=(api_functions.api_key, api_functions.api_password),
                                 headers=ticket_headers, data=ticket_data)
        response.raise_for_status()  # Raise exception for error responses
        root.destroy()  # exits out of the gui

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
    root.destroy()  # destroys the gui/ quits application


# Function to submit all notes and adjustments but places the ticket on hold/stop timer (unfinished)
def submit_and_hold(body, dept_list_dropdown_combobox, all_department_ids, all_department_names):
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
        phone_number_override(number_override_text)  # Assuming number_override_text is accessible

        selected_facility_id = helpers.selected_facility(dept_list_dropdown_combobox, all_department_ids, all_department_names)
        if selected_facility_id is None:
            messagebox.showerror("Error", "Please select a valid facility before submitting.")
            return

        # get reason text box text and set to variable
        reason = reason_text.get('1.0', tk.END).strip()

        # note data
        note_url = f"{api_functions.base_url}/api/v2/tickets/{ticket_number}/notes"
        note_headers = {'Content-Type': 'application/json'}
        formatted_body = body.replace('\n', '<br>')
        enter = api_functions.line_break.replace('\n', '<br>')
        note_data = json.dumps({
            "private": True,
            "body": f"Agent Notes:{enter}{formatted_body}{enter}Reason for hold: {reason}"
        })

        # Update ticket properties
        update_url = f"{api_functions.base_url}/api/v2/tickets/{ticket_number}"
        update_headers = {'Content-Type': 'application/json'}
        update_data = json.dumps({
            'group_id': api_functions.group_id,
            'status': 16,
            'department_id': selected_facility_id
        })

        # Send request to submit private note and status change
        try:
            # api request for update data
            update_response = requests.put(update_url, auth=(api_functions.api_key, api_functions.api_password),
                                           headers=update_headers,
                                           data=update_data)
            update_response.raise_for_status()

            # api request for note data
            response = requests.post(note_url, auth=(api_functions.api_key, api_functions.api_password),
                                     headers=update_headers,data=note_data)
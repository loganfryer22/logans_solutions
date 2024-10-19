


# import requests
# import sys
# import json
# import datetime
# import tkinter as tk
# from tkinter import messagebox
# import tkinter
# from PIL import Image, ImageTk
# import pandas as pd
#
# # API Key
# secret_file = 'C:\\Users\\logan.fryer\\OneDrive - PACS\\Documents\\Misc\\my_api_key.txt'
# with open(secret_file, "r") as f:
#     secret_key = f.read().strip()
#     f.close()
#
# # static variables
# base_url = 'https://pacs.freshservice.com'
# api_key = secret_key
# api_password = 'x'
# group_id = 21000562406
# responder_id = 21002944650
# override_number = None
# email = 'testing@email.com'
# ticket = 518178
# line_break = "\n"
# enter = line_break.replace('\n', '<br>')
#
# url = f"{base_url}/api/v2/problem/types"
# headers = {'Content-Type': 'application/json'}
#
# response = requests.get(url, auth=(api_key, api_password), headers=headers)
# response.raise_for_status()
#
# print(f"status code: {response.status_code}")
# print(f"response json: {response}")
# print(f"response text: {response.text}")























#
# # # # Global Variables
# # # selected_facility_id = None
# # # all_department_ids = None
# # # selected_facility_name = None
# # # all_department_names = None
# #
# # # get info on all departments
# # def get_departments():
# #     all_departments = []
# #     all_dept_ids = []
# #     page = 1
# #     per_page = 100
# #
# #     while True:
# #         departments_url = f"{domain}/api/v2/departments?page={page}&per_page={per_page}"
# #         headers = {'Content-Type': 'application/json'}
# #
# #         try:
# #             response = requests.get(departments_url, auth=(api_key, password), headers=headers)
# #             response.raise_for_status()
# #
# #             departments_data = response.json()
# #             departments = departments_data.get('departments', [])  # Directly access the list
# #
# #             if not departments:
# #                 break
# #
# #             for dept in departments:
# #                 all_departments.append(dept['name'])
# #                 all_dept_ids.append(dept['id'])
# #
# #             page += 1
# #
# #         except requests.exceptions.RequestException as e:
# #             print(f"Error fetching departments: {e}\n{response.text}")
# #             break
# #
# #     global all_department_names
# #     global all_department_ids
# #     all_department_names = all_departments
# #     all_department_ids = all_dept_ids
# #
# # # get info for the selected facility
# # def selected_facility():
# #     global selected_facility_name
# #     global all_department_ids
# #     global selected_facility_id
# #
# #     selected_facility_name = "Anchor Post Acute"  ################# test #####################
# #
# #     try:
# #         index = all_department_names.index(selected_facility_name)
# #         selected_facility_id = all_department_ids[index]
# #         return selected_facility_id
# #     except ValueError:
# #         print(f"Error: Department '{selected_facility_name}' not found.")
# #         return None
# #
# # get_departments()
# # selected_facility()
# # print(selected_facility_name)
# # print(selected_facility_id) # 21000149089
# # print(all_department_names)
# # print(all_department_ids)
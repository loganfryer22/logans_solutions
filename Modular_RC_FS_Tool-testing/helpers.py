def selected_facility(dept_list_dropdown_combobox, all_department_ids, all_department_names):
    selected_facility_name = dept_list_dropdown_combobox.get()

    # Create a dictionary for faster lookup
    dept_name_to_id = {name: id for name, id in zip(all_department_names, all_department_ids)}

    selected_facility_id = dept_name_to_id.get(selected_facility_name)  # Get ID or None if not found
    return selected_facility_id
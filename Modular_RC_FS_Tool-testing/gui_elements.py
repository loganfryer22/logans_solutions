import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def start_move(event):
    root.x = event.x
    root.y = event.y

def move_window(event):
    x = root.winfo_x() - root.x + event.x
    y = root.winfo_y() - root.y + event.y
    root.geometry(f"+{x}+{y}")

def create_title_bar(root, icon_path):
    style = ttk.Style()
    style.theme_use('classic')
    title_bar = ttk.Frame(root, style='Titlebar.TFrame')
    title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
    style.configure('Titlebar.TFrame', background='Purple')

    icon_image = Image.open(icon_path)
    icon_photo = ImageTk.PhotoImage(icon_image.resize((115, 34)))
    icon_label = tk.Label(title_bar, image=icon_photo)
    icon_label.image = icon_photo
    icon_label.grid(row=0, column=0, padx=5, pady=5)

    title_label = ttk.Label(title_bar, text="RC/FS Enhanced Call App",
                            font=("Helvetica", 14, "bold"), background='Purple', foreground='white')
    title_label.grid(row=0, column=1, padx=10, pady=5)

    title_bar.bind("<ButtonPress-1>", start_move)
    title_bar.bind("<B1-Motion>", move_window)
    title_label.bind("<ButtonPress-1>", start_move)
    title_label.bind("<B1-Motion>", move_window)
    icon_label.bind("<ButtonPress-1>", start_move)
    icon_label.bind("<B1-Motion>", move_window)

    return title_bar

def create_content_frame(root, all_department_names, ticket_number, incoming_phone_number, full_name):
    content_frame = ttk.Frame(root, padding=10)
    content_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    ticket_number_label = ttk.Label(content_frame, text="Ticket Number:")
    ticket_number_label.grid(row=0, column=0, sticky="w")
    ticket_number_entry = ttk.Label(content_frame, text=ticket_number)
    ticket_number_entry.grid(row=0, column=1, sticky="e")

    incoming_phone_number_label = ttk.Label(content_frame, text="Phone Number:")
    incoming_phone_number_label.grid(row=1, column=0, sticky="w")
    incoming_phone_number_text = ttk.Label(content_frame, text=incoming_phone_number)
    incoming_phone_number_text.grid(row=1, column=1, sticky="e")

    full_name_label = ttk.Label()
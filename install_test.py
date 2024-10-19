import tkinter as tk
from tkinter import ttk, messagebox

# Create gui
root = tk.Tk()
root.title("Testing Installer")
root.geometry("300x300")
root.attributes("-topmost", True)

# test label
label = ttk.Label(text='TESTING INSTALLER')
label.grid(column=0, row=0, columnspan=2)

# keep gui open
root.mainloop()
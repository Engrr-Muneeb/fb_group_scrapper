import tkinter as tk
import sys
from tkinter import filedialog
from tkinter import messagebox
from datetime import date
from pathlib import Path


DEFAULT_COOKIES_FILE_PATH = Path(__file__).resolve().parent.parent / '.conf' / '.cookies'

def CreateInitGUI():
    user_inputs = {}

    def submit():
        nonlocal user_inputs
        error_label.config(text="")  # Clear the error message
        cookies_file = cookies_file_entry.get()
        group_id = group_id_entry.get()
        number_of_pages = number_of_pages_entry.get()
        selected_date = date_picker.get()

        # Validate the mandatory fields
        if not cookies_file or not group_id:
            error_label.config(text="Please fill in all mandatory fields.", fg="red")
            return

        # Store the inputs in user_inputs dictionary
        user_inputs = {
            "cookies_file": Path(cookies_file),
            "group_id": group_id,
            "number_of_pages": int(number_of_pages),
            "selected_date": selected_date
        }
        window.destroy()


    def select_cookies_file():
        cookies_file = filedialog.askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        cookies_file_entry.delete(0, tk.END)
        cookies_file_entry.insert(0, cookies_file)


    def add_today():
        date_picker.delete(0, tk.END)
        date_picker.insert(0, date.today().strftime("%d-%m-%Y"))  # Default value

    def on_closing():
        messagebox.showerror("Error", "Closing the scrapper")
        sys.exit(1)

    # Create the main window
    window = tk.Tk()
    window.title("Input Form")

    # Register the callback function for window close event
    window.protocol("WM_DELETE_WINDOW", on_closing)

    # Cookies File
    cookies_file_label = tk.Label(window, text="   Cookies File:")
    cookies_file_label.grid(row=0, column=0, sticky="w")

    cookies_file_asterisk = tk.Label(window, text="*", fg="red")
    cookies_file_asterisk.grid(row=0, sticky="w")

    cookies_file_entry = tk.Entry(window)
    cookies_file_entry.grid(row=0, column=1, pady=5)

    if DEFAULT_COOKIES_FILE_PATH.is_file():
        cookies_file_entry.insert(0, str(DEFAULT_COOKIES_FILE_PATH))  # Default value

    cookies_file_button = tk.Button(window, text="Select", command=select_cookies_file)
    cookies_file_button.grid(row=0, column=2)

    # Group ID
    group_id_label = tk.Label(window, text="   Group ID:")
    group_id_label.grid(row=1, column=0, sticky="w")

    group_id_asterisk = tk.Label(window, text="*", fg="red")
    group_id_asterisk.grid(row=1, sticky="w")

    group_id_entry = tk.Entry(window)
    group_id_entry.insert(0, '1608483306030594')
    group_id_entry.grid(row=1, column=1, pady=5)

    # Number of Pages
    number_of_pages_label = tk.Label(window, text="Pages to scrape:")
    number_of_pages_label.grid(row=2, column=0, sticky="w")

    number_of_pages_entry = tk.Entry(window)
    number_of_pages_entry.insert(0, "4")  # Default value
    number_of_pages_entry.grid(row=2, column=1, pady=5)

    # Date

    # date_label = tk.Label(window, text="Date:")
    # date_label.grid(row=3, column=0, sticky="w")

    # date_picker = tk.Entry(window)
    # date_picker.grid(row=3, column=1, pady=5)

    # date_picker_button = tk.Button(window, text="Select Date", command=show_date_picker)
    # date_picker_button.grid(row=3, column=2)


    date_label = tk.Label(window, text="Date: (DD-MM-YYYY)")
    date_label.grid(row=3, column=0, sticky="w")

    date_picker = tk.Entry(window)
    date_picker.grid(row=3, column=1, pady=5)
    today_button = tk.Button(window, text="Today", command=add_today)
    today_button.grid(row=3, column=2)

    # Error Label
    error_label = tk.Label(window, text="")
    error_label.grid(row=4, column=0, columnspan=2, pady=5)

    # Submit Button
    submit_button = tk.Button(window, text="Submit", command=submit)
    submit_button.grid(row=5, column=0, columnspan=2, pady=10)

    # Start the GUI
    window.mainloop()
    return user_inputs


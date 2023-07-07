import tkinter as tk
import sys
from tkinter import messagebox
import logging


class LogWriter:
    def __init__(self, text_widget, log_file):
        self.text_widget = text_widget
        self.log_file = log_file

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.text_widget.update()  # Update the log window immediately

    def flush(self):
        pass

log_text = None

def redirect_stdout(log_file, logger):
    window = tk.Tk()
    window.withdraw()
    global log_text
    log_window = tk.Toplevel()
    log_window.title("Log")
    log_window.geometry('750x600')
    window.geometry('800x600')
    log_text = tk.Text(log_window, height=20, width=50)
    # Create the Scrollbar widget
    scrollbar = tk.Scrollbar(log_window)

    # Configure the Text widget and Scrollbar
    log_text.configure(yscrollcommand=scrollbar.set)
    scrollbar.configure(command=log_text.yview)

    # Pack the Text widget and Scrollbar in the log window
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Allow the log window to resize the Text widget
    log_window.pack_propagate(False)

    log_writer = LogWriter(log_text, log_file)
    log_window_handle = logging.StreamHandler(stream=log_writer)

    logger.addHandler(log_window_handle)
    return log_window_handle, window

def end_scraping(logger, log_window_handle, window):
    logger.removeHandler(log_window_handle)  # Remove the log window handler

    messagebox.showinfo("Complete", "Data Scraping Completed!!")
    window.destroy()

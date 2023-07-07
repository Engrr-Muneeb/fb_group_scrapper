import tkinter as tk

def AskToGetLatestData():
    # Create the main window
    root = tk.Tk()
    root.title("Post Scraper")
    root.geometry("300x150")

    # Create a StringVar to store the selected option
    selected_option = tk.StringVar()

    message = """Warning: Already scraped data available. Please select:\n\nContinue: To use already created data
    Scrape Latest posts: To scraoe only latest posts\nScrape Again: Again scrape with new params"""

    # Display the warning message
    warning_label = tk.Label(root, text=message)
    warning_label.pack(pady=10)

    # Create a frame to hold the buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Create the buttons
    scrape_latest_button = tk.Button(button_frame, text="Scrape Latest Posts", command=lambda: process_selection("Scrape Latest Posts"))
    scrape_latest_button.pack(side=tk.LEFT, padx=5)

    continue_button = tk.Button(button_frame, text="Continue", command=lambda: process_selection("Continue"))
    continue_button.pack(side=tk.LEFT, padx=5)

    scrape_again_button = tk.Button(button_frame, text="Scrape Again", command=lambda: process_selection("Scrape Again"))
    scrape_again_button.pack(side=tk.LEFT, padx=5)

    # Function to process the selection
    def process_selection(selection):
        selected_option.set(selection)
        root.destroy()  # Close the GUI

    # Run the GUI
    root.mainloop()

    # Return the selected option
    return selected_option.get()


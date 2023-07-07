import tkinter as tk
from tkinter import ttk
import sys
sys.path.append("..")

from ReadWriteData import ReadDataFromFile
from filter_class import Filters


def AddText(post, parent_widget, word_to_bold):

    post_text = tk.Text(parent_widget, wrap=tk.WORD, height=2, width=50, bd=0, highlightthickness=0)
    post_text.grid(row=0, column=1)
    post_text.insert(tk.END, post.text)

    # Bold specific words in the post text
    if word_to_bold:
        start_index = "1.0"
        while True:
            start_index = post_text.search(word_to_bold, start_index, stopindex=tk.END)
            if not start_index:
                break
            end_index = f"{start_index}+{len(word_to_bold)}c"
            post_text.tag_add("bold", start_index, end_index)
            post_text.tag_configure("bold", font=("Arial", 12, "bold"))
            start_index = end_index

    # Configure the height of the Text widget based on the content
    lines = int(post_text.index("end-1c").split(".")[0])
    post_text.configure(height=lines + 4)

    # Disable editing in the Text widget
    post_text.configure(state=tk.DISABLED)

def create_post_widget(post, parent_frame, word_to_bold):
    post_widget = tk.Frame(parent_frame, padx=10, pady=10, relief=tk.RAISED, borderwidth=1)
    post_widget.pack(fill=tk.X, padx=10, pady=10)

    AddText(post, post_widget, word_to_bold)

    # User Name and Time
    user_info = tk.Label(post_widget, text=f"{post.user}\n{post.time}", wraplength=100)
    user_info.grid(row=0, column=0)

    # Post Link
    post_link = tk.Label(post_widget, text="View Post", fg="blue", cursor="hand2")
    post_link.grid(row=0, column=2)
    post_link.bind("<Button-1>", lambda event, url=post.url: open_link(url))

    def toggle_comments():
        if comment_frame.winfo_ismapped():
            comment_frame.pack_forget()
            plus_button.config(text="Show Comments")
        else:
            comment_frame.pack(padx=10, pady=5)
            plus_button.config(text="Hide Comments")

    # Comment Frame
    comment_widget = tk.Frame(parent_frame, padx=10, pady=5, relief=tk.RAISED, borderwidth=1)
    comment_widget.pack(fill=tk.X, padx=10, pady=10)

    comment_frame = tk.Frame(comment_widget, padx=10, pady=5, relief=tk.RAISED, borderwidth=1)

    # "+" Button
    plus_button = tk.Button(comment_widget, text="Show Comments", width=15, command=toggle_comments)
    plus_button.pack()

    # Comments
    for comment in post.comments:
        create_comment_widget(comment, comment_frame, word_to_bold)
        for reply in comment.replies:
            create_comment_widget(reply, comment_frame, word_to_bold)

def create_comment_widget(comment, parent_frame, word_to_bold):
    comment_widget = tk.Frame(parent_frame, padx=5, pady=5)

    # Comment Text
    AddText(comment, comment_widget, word_to_bold)

    # User Name and Time
    user_info = tk.Label(comment_widget, text=f"{comment.user}\n{comment.time}")
    user_info.grid(row=0,column=0)

    # Post Link
    post_link = tk.Label(comment_widget, text="View Post", fg="blue", cursor="hand2")
    post_link.grid(row=0,column=2)
    post_link.bind("<Button-1>", lambda event, url=comment.url: open_link(url))

    # comment_text.pack(anchor=tk.CENTER)
    comment_widget.pack(fill=tk.X, padx=10, pady=10)

def open_link(url):
    # Implement your code to open the URL here
    print("Opening URL:", url)

def ShowData():
    # Create the main window
    root = tk.Tk()
    root.title("Posts GUI")
    root.geometry('750x600')

    # Create a filters frame
    filters_frame = tk.Frame(root, padx=10, pady=10, relief=tk.RAISED, borderwidth=1)
    filters_frame.pack(fill=tk.X, padx=10, pady=10)

    # String Search Field
    string_search_label = tk.Label(filters_frame, text="String Search:")
    string_search_label.grid(row=0, column=0, sticky=tk.E)
    string_search_entry = tk.Entry(filters_frame)
    string_search_entry.grid(row=0, column=1, padx=5, pady=5)

    # Include Users Field
    include_users_label = tk.Label(filters_frame, text="Include Users:")
    include_users_label.grid(row=1, column=0, sticky=tk.E)
    include_users_entry = tk.Entry(filters_frame)
    include_users_entry.grid(row=1, column=1, padx=5, pady=5)

    # Exclude Users Field
    exclude_users_label = tk.Label(filters_frame, text="Exclude Users:")
    exclude_users_label.grid(row=2, column=0, sticky=tk.E)
    exclude_users_entry = tk.Entry(filters_frame)
    exclude_users_entry.grid(row=2, column=1, padx=5, pady=5)

    # Search Button
    def search_button_clicked():
        include_users, exclude_users = [], []
        search_text = string_search_entry.get()
        if include_users_entry.get():
            include_users = include_users_entry.get().split(',')
        if exclude_users_entry.get():
            exclude_users = exclude_users_entry.get().split(',')

        print("String Search:", search_text)
        print("Include Users:", include_users)
        print("Exclude Users:", exclude_users)

        filters = Filters(string_to_search=search_text, include_users=include_users, exclude_users=exclude_users)

        posts = ReadDataFromFile(filters=filters)
        print(len(posts))
        # Perform search or any other action with the search inputs

        # Show the post data
        show_post_data(posts, search_text)

    search_button = tk.Button(filters_frame, text="Search", command=search_button_clicked)
    search_button.grid(row=3, columnspan=2, padx=5, pady=10)

    # Create a canvas widget
    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar to the canvas
    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure the canvas to use the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Create a frame inside the canvas to hold the content
    content_frame = tk.Frame(canvas)
    content_frame.pack(fill=tk.BOTH, padx=10, pady=10)

    def show_post_data(posts, search_text):
        # Clear the content frame
        for widget in content_frame.winfo_children():
            widget.destroy()

        # Create widgets for each post
        for post in posts:
            create_post_widget(post, content_frame, search_text)

        # Function to configure the canvas scrolling region
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        content_frame.bind("<Configure>", configure_canvas)

    # Set the canvas scrolling region
    def set_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    content_frame.bind("<Configure>", set_scroll_region)

    # Create a window in the canvas for the content frame
    canvas.create_window(0, 0, anchor="nw", window=content_frame)

    # Configure the scrollbar to scroll with the canvas
    def scroll_canvas(*args):
        canvas.yview(*args)

    scrollbar.config(command=scroll_canvas)

    # Start the main event loop
    root.mainloop()




    if __name__ == "__main__":
        ShowData()
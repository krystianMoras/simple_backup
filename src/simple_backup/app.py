import tkinter as tk
from tkinter import filedialog, ttk
from simple_backup.handler import copy_files
import threading
import queue

def select_source():
    source_path.set(filedialog.askdirectory())

def select_target():
    target_path.set(filedialog.askdirectory())

def update_progress(progress):
    global progress_bar
    progress_bar['value'] = progress

def start_progress():
    source = source_path.get()
    target = target_path.get()
    # disable the start button
    start_button['state'] = 'disabled'
    errors_label['text'] = ""
    exception_queue = queue.Queue()
    thread = threading.Thread(target=copy_files, args=(source, target, update_progress, exception_queue))
    thread.start()
    root.after(100, check_thread, thread, exception_queue)


def check_thread(thread, exception_queue):
    if thread.is_alive():
        # Check again in 100ms
        root.after(100, check_thread, thread, exception_queue)
    else:
        # If the thread has finished, enable the start button
        start_button['state'] = 'normal'
        if not exception_queue.empty():
            e = exception_queue.get()
            errors_label['text'] = str(e)
            errors_label['fg'] = 'red'
        else:
            errors_label['text'] = "Done!"
            errors_label['fg'] = 'green'

root = tk.Tk()

source_path = tk.StringVar()
target_path = tk.StringVar()

source_button = tk.Button(root, text="Select Source", command=select_source)
source_button.pack()

source_label = tk.Label(root, textvariable=source_path)
source_label.pack()

target_button = tk.Button(root, text="Select Target", command=select_target)
target_button.pack()

target_label = tk.Label(root, textvariable=target_path)
target_label.pack()

progress_bar = ttk.Progressbar(root, length=200, mode='determinate')
progress_bar.pack()

errors_label = tk.Label(root, text="")
errors_label.pack()

start_button = tk.Button(root, text="Start", command=start_progress)
start_button.pack()

root.mainloop()
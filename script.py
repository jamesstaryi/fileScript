### Created by James Yi
### TODO - Link application to artifactory, need to use their APIs
###      - Make application work with fortify scans as well. Shouldn't be difficult, use pypdf pymupdf
### Note - Drag n drop breaks sometimes with file directories that contain spaces, still need to figure out a way to fix

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import shutil
from datetime import datetime, timedelta

MAX_DATE_RANGE = 1000; # Maximum date from today allowed. For example, if you want files within 30 days only, then set it to 30
previous_state = None

# Loads the state data and abbreviations
def load_state_data(abbreviation_file, name_file):
    state_data = []
    try:
        with open(abbreviation_file, 'r', encoding="utf8", errors='ignore') as abbrev_file, open(name_file, 'r', encoding="utf8", errors='ignore') as name_file:
            for abbrev_line, name_line in zip(abbrev_file, name_file):
                abbreviation = abbrev_line.strip()
                state_name = name_line.strip()
                state_data.append((abbreviation, state_name))
        return state_data
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return []

# Go through the file to check for certain requirements
def find_states(filename, state_abbreviations, state_names):
    output = []
    try:
        with open(filename, 'r', encoding="utf8", errors='ignore') as file:
            line_number = 1
            for line in file:
                # Ignore if it is a CIVID ticket
                if "CIVID" in line:
                    line_number += 1
                    continue
                
                # Ignore if line starts with "-": means it is a note and may contain flagged info
                if line.strip().startswith("-"):
                    line_number += 1
                    continue
                
                found = False
                # Check for abbreviations with boundary conditions, case-insensitive
                for abbreviation in state_abbreviations:
                    if re.search(rf'(^|[\s_]){re.escape(abbreviation)}($|[\s_])', line):
                        output.append(f'Line {line_number}: {line.strip()} (Found Abbreviation: {abbreviation})')
                        found = True
                        break
                
                # Check for full state names with boundary conditions, case-insensitive
                if not found:
                    for state_name in state_names:
                        if re.search(rf'(^|[\s_]){re.escape(state_name)}($|[\s_])', line, re.IGNORECASE):
                            output.append(f'Line {line_number}: {line.strip()} (Found State Name: {state_name})')
                            break

                line_number += 1
    except FileNotFoundError:
        print(f"The file '{filename}' was not found.")
    
    return output

# Get version number from filename - assuming version number is formatted with 4 numbers and 3 periods
def extract_version_from_filename(filename):
    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', filename)
    return match.group(1) if match else None

# Get version number from the file and date from the most recent part of the release note
def extract_version_and_date_from_file(file_path):
    version_pattern = re.compile(r'version:\s*([^\s]+)', re.IGNORECASE)
    date_pattern = re.compile(r'\b\d{1,2}/\d{1,2}/(\d{2}|\d{4})\b') 
    
    try:
        with open(file_path, 'r', encoding="utf8", errors='ignore') as file:
            for line in file:
                version_match = version_pattern.search(line)
                if version_match:
                    version_info = version_match.group(1).strip()
                    date_match = date_pattern.search(line)
                    date_info = date_match.group(0) if date_match else None
                    return version_info, date_info
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    
    return None, None

# Parse the date to work with multiple date formats
def parse_date(date_str):
    date_formats = ['%m/%d/%Y', '%m/%d/%y']
    for date_format in date_formats:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            continue
    return None

# When clicking on a file in the application
def show_file_output(event):
    clicked_widget = event.widget
    clicked_widget.update_idletasks()
    
    # Retrieve file path associated with the clicked label
    file_path = clicked_widget.path
    
    # Extract file name and color
    file_name = os.path.basename(file_path)
    file_color = clicked_widget.cget("fg")
    
    if file_color == 'green':
        messagebox.showinfo("Info", "This file does not contain any errors.")
        return

    state_abbreviations = {abbrev for abbrev, name in state_data if name != selected_state}
    state_names = {name for abbrev, name in state_data if name != selected_state}
    output = find_states(file_path, state_abbreviations, state_names)
    
    # Check version and date match
    title_version = extract_version_from_filename(file_name)
    file_version, file_date = extract_version_and_date_from_file(file_path)
    
    version_mismatch_message = ""
    if title_version and file_version and title_version != file_version:
        version_mismatch_message = f"Version mismatch: Filename version ({title_version}) does not match file version ({file_version}).\n"
    
    missing_version_message = ""
    if not title_version or not file_version:
        missing_version_message = "Version number is missing in the filename or the file content.\n"
    
    if file_date:
        try:
            file_date_obj = parse_date(file_date)
            current_date = datetime.now()
            if abs((current_date - file_date_obj).days) > MAX_DATE_RANGE:
                date_message = f"Date on file is not within {MAX_DATE_RANGE} days of current date: {file_date}\n"
            else:
                date_message = ""
        except ValueError:
            date_message = f"Invalid date format found in file: {file_date}\n"
    else:
        date_message = "No date found in the file.\n"
    
    if output:
        output_text = f"{version_mismatch_message}{missing_version_message}{date_message}\n" + '\n'.join(output)
    else:
        output_text = f"{version_mismatch_message}{missing_version_message}{date_message}"
    
    # Create a popup window
    popup = tk.Toplevel(root)
    popup.title(f"Output for {file_name}")
    popup.geometry("600x400")

    # Position the popup relative to the root window
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    popup.geometry(f"+{root_x+50}+{root_y+50}")
    
    # Add a Text widget to display the output
    text_widget = tk.Text(popup, wrap=tk.WORD)
    text_widget.pack(expand=True, fill=tk.BOTH)
    text_widget.insert(tk.END, output_text)
    text_widget.config(state=tk.DISABLED)

# Swapping between states
def on_select(event):
    global selected_state, previous_state
    
    # Get the newly selected state
    new_state = state_combo.get()
    
    # Check if a state change is needed
    if selected_state and new_state != selected_state:
        # Confirm the state switch
        result = messagebox.askyesno("Confirm State Change", f"Are you sure you want to switch from '{selected_state}' to '{new_state}'? \n\n This will remove all the files.")
        if not result:
            # User cancelled the change, revert to previous state
            state_combo.set(selected_state)
            return
        else:
            # User agreed, remove all files
            for widget in file_list_frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.destroy()
            # Update the state of the upload button
            update_upload_button_state()
    
    # Update the selected state
    selected_state = new_state
    previous_state = new_state

# Using Select File button for file upload
def select_files():
    if not selected_state:
        messagebox.showinfo("Info", "Please select a state.")
        return

    global current_directory
    file_paths = filedialog.askopenfilenames(
        title="Select Files",
        filetypes=[("Text Files", "*.txt")],
        defaultextension=".txt"
    )
    
    if selected_state:
        state_abbreviations = {abbrev for abbrev, name in state_data if name != selected_state}
        state_names = {name for abbrev, name in state_data if name != selected_state}

        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            current_directory = os.path.dirname(file_path)
            
            # Check if the file already exists in the list
            existing_frame = None
            for child in file_list_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    label = child.winfo_children()[0]  # Assuming label is the first child
                    if file_name in label.cget("text"):
                        existing_frame = child
                        break

            has_state = find_states(file_path, state_abbreviations, state_names)
            
            # Extract version and date information
            title_version = extract_version_from_filename(file_name)
            file_version, file_date = extract_version_and_date_from_file(file_path)
            
            # Determine file color
            if title_version and file_version and title_version == file_version:
                if file_date:
                    try:
                        file_date_obj = parse_date(file_date)
                        current_date = datetime.now()
                        color = 'green' if abs((current_date - file_date_obj).days) <= MAX_DATE_RANGE and not has_state else 'red'
                    except ValueError:
                        color = 'red'  # Invalid date format
                else:
                    color = 'red'  # Missing date
            else:
                color = 'red'
            
            # Update existing entry or add a new one
            if existing_frame:
                # Update existing entry
                existing_frame.winfo_children()[0].config(fg=color)

                # Remove ignore button if file turns green
                if color == 'green':
                    for widget in existing_frame.winfo_children():
                        if isinstance(widget, tk.Button) and widget.cget('text') == 'Ignore':
                            widget.destroy()
                            break
            else:
                # Add new entry
                file_frame = tk.Frame(file_list_frame)
                file_frame.pack(fill=tk.X, padx=5, pady=2)

                # Create label for file name
                file_label = tk.Label(file_frame, text=file_name, fg=color, padx=10, anchor='w')
                file_label.path = file_path
                file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                file_label.bind("<Button-1>", show_file_output)
                
                # Create remove button
                remove_button = tk.Button(file_frame, text="Remove", command=lambda f=file_frame: remove_file_entry(f))
                remove_button.pack(side=tk.RIGHT)
                
                # Create ignore button if the file is red
                if color == 'red':
                    ignore_button = tk.Button(file_frame, text="Ignore", command=lambda f=file_frame: ignore_file_entry(f))
                    ignore_button.pack(side=tk.RIGHT)

        # Update the state of the upload button
        update_upload_button_state()

    else:
        messagebox.showinfo("Info", "Please select a State.")

# Using drag n drop for file upload
def on_drop(event):
    if not selected_state:
        messagebox.showinfo("Info", "Please select a state.")
        return

    global current_directory
    file_paths = event.data.split('}')
    
    # Clean up paths and remove empty strings
    file_paths = [fp.strip().strip('{').strip() for fp in file_paths if fp.strip()]
    
    # Handle the case where paths are not enclosed in braces
    if len(file_paths) == 1 and ' ' in file_paths[0]:
        # If the paths are not enclosed in braces and are space-separated
        file_paths = file_paths[0].split()
    
    # Handle paths that still have '{' at the start
    complete_file_paths = [fp if not fp.startswith('{') else fp[1:] for fp in file_paths]
    
    if selected_state:
        state_abbreviations = {abbrev for abbrev, name in state_data if name != selected_state}
        state_names = {name for abbrev, name in state_data if name != selected_state}

        for file_path in complete_file_paths:
            file_name = os.path.basename(file_path)
            current_directory = os.path.dirname(file_path)
            
            # Check if the file already exists in the list
            existing_frame = None
            for child in file_list_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    label = child.winfo_children()[0]  # Assuming label is the first child
                    if file_name in label.cget("text"):
                        existing_frame = child
                        break

            has_state = find_states(file_path, state_abbreviations, state_names)
            
            # Extract version and date information
            title_version = extract_version_from_filename(file_name)
            file_version, file_date = extract_version_and_date_from_file(file_path)
            
            # Determine file color
            if title_version and file_version and title_version == file_version:
                if file_date:
                    try:
                        file_date_obj = parse_date(file_date)
                        current_date = datetime.now()
                        color = 'green' if abs((current_date - file_date_obj).days) <= MAX_DATE_RANGE and not has_state else 'red'
                    except ValueError:
                        color = 'red'  # Invalid date format
                else:
                    color = 'red'  # Missing date
            else:
                color = 'red'
            
            # Update existing entry or add a new one
            if existing_frame:
                # Update existing entry
                existing_frame.winfo_children()[0].config(fg=color)

                # Remove ignore button if file turns green
                if color == 'green':
                    for widget in existing_frame.winfo_children():
                        if isinstance(widget, tk.Button) and widget.cget('text') == 'Ignore':
                            widget.destroy()
                            break
            else:
                # Add new entry
                file_frame = tk.Frame(file_list_frame)
                file_frame.pack(fill=tk.X, padx=5, pady=2)

                # Create label for file name
                file_label = tk.Label(file_frame, text=file_name, fg=color, padx=10, anchor='w')
                file_label.path = file_path
                file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                file_label.bind("<Button-1>", show_file_output)
                
                # Create remove button
                remove_button = tk.Button(file_frame, text="Remove", command=lambda f=file_frame: remove_file_entry(f))
                remove_button.pack(side=tk.RIGHT)
                
                # Create ignore button if the file is red
                if color == 'red':
                    ignore_button = tk.Button(file_frame, text="Ignore", command=lambda f=file_frame: ignore_file_entry(f))
                    ignore_button.pack(side=tk.RIGHT)

        # Update the state of the upload button
        update_upload_button_state()
    else:
        messagebox.showinfo("Info", "Please select a State.")

# Ignore file button
def ignore_file_entry(frame):
    # Find the text from the relevant widget in the frame
    file_text = ""
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Label):
            file_text = widget.cget("text")
            break

    # Confirm ignoring the file with the frame's text
    result = messagebox.askyesno("Confirm Ignore", f"Are you sure you want to ignore the file '{file_text}'?")
    if result:
        # Mark the file entry as ignored by changing its color or text
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(fg='orange')
            if isinstance(widget, tk.Button) and widget.cget('text') == 'Ignore':
                widget.destroy()
                break
        # Update the state of the upload button
        update_upload_button_state()

# Remove file button
def remove_file_entry(frame):
    # Find the text from the relevant widget in the frame
    file_text = ""
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Label):
            file_text = widget.cget("text")
            break

    # Confirm deleting the file with the frame's text
    result = messagebox.askyesno("Confirm Remove", f"Are you sure you want to remove the file '{file_text}'?")
    if result:
        frame.destroy()
        # Update the state of the upload button
        update_upload_button_state()

# Remove ALL file button
def remove_all_files():
    # Confirm removing all the files
    result = messagebox.askyesno("Confirm Celar All", f"Are you sure you want to remove all the files?")
    if result:
        for widget in file_list_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()
        # Update the state of the upload button
        update_upload_button_state()

# TODO - Upload to artifactory button
def upload_files():
    mgmt_textbox_content = mgmt_textbox.get()  # Get the content from the mgmt_textbox

    if re.search(r'\d', mgmt_textbox_content):
        # Ask for confirmation if numbers are found
        result = messagebox.askyesno("Confirm Upload", f"Do you want to upload to MGMT-{mgmt_textbox_content}? \n (This hasn't actually been implemented)")
        if result:
            # Show a confirmation message after successful upload
            messagebox.showinfo("Upload Successful", f"The files were successfully uploaded to MGMT-{mgmt_textbox_content}. \n (This hasn't actually been implemented)")
            return

    else:
        # Show an error message if no numbers are found
        messagebox.showerror("Input Error", "Please input a valid MGMT number.")

# Use if you want upload button to download to local directories
def upload_files_to_directory():
    global current_directory
    if not file_list_frame.winfo_children():
        messagebox.showwarning("No Files", "No files to upload.")
        return

    # Ask for destination folder
    dest_folder = filedialog.askdirectory(title="Select Destination Folder")
    if not dest_folder:
        messagebox.showwarning("No Destination", "No destination folder selected.")
        return
    
    # Copy files to the destination folder
    for child in file_list_frame.winfo_children():
        for widget in child.winfo_children():
            if isinstance(widget, tk.Label):
                file_name = os.path.basename(widget.cget("text"))
                file_color = widget.cget("fg")
                
                src_path = widget.path
                dest_path = os.path.join(dest_folder, file_name)
                
                if os.path.exists(src_path):
                    try:
                        shutil.copy(src_path, dest_path)
                    except Exception as e:
                        print(f"Error copying file '{file_name}': {e}")
    
    messagebox.showinfo("Upload Complete", f"Files have been uploaded to {dest_folder}.")

# Checks to see if upload button should be available or not
def update_upload_button_state():
    # Check if there are any child frames in file_list_frame
    has_files = any(isinstance(child, tk.Frame) for child in file_list_frame.winfo_children())
    
    # Check if there are any red files
    has_red_files = any(
        child.winfo_children()[0].cget("fg") == 'red'
        for child in file_list_frame.winfo_children()
        if isinstance(child, tk.Frame)
    )
    
    # Update the state of the upload button
    if has_files and not has_red_files:
        upload_button.config(state=tk.NORMAL)
    else:
        upload_button.config(state=tk.DISABLED)

# Exit the app
def close_app():
    if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
        root.destroy()

if __name__ == "__main__":
    # Load state data
    state_data = load_state_data("us-states-abbreviation.txt", "us-states.txt")
    selected_state = None
    current_directory = ""

    # Setup GUI
    root = TkinterDnD.Tk()
    root.title("File Processor")
    root.geometry("500x700")
    
    # MGMT input
    mgmt_label = tk.Label(root, text="Enter MGMT:")
    mgmt_label.pack(padx=5)
    mgmt_textbox = tk.Entry(root, width=10)
    mgmt_textbox.pack(padx=10, pady=10)
    mgmt_textbox.config(justify='right')

    # Dropdown menu
    state_label = tk.Label(root, text="Select a state for the Release Request:")
    state_label.pack(pady=10)
    state_combo = ttk.Combobox(root, values=[name for _, name in state_data])
    state_combo.bind("<<ComboboxSelected>>", on_select)
    state_combo.pack(pady=10)
    
    # File selection button
    select_button = tk.Button(root, text="Select Files", command=select_files)
    select_button.pack(pady=20)
    
    # Drop area
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', on_drop)

    # Listbox to display file names
    file_list_frame = tk.Frame(root)
    file_list_frame.pack(pady=10)
    
    # Frame to hold the buttons at the bottom
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
    button_frame = tk.Frame(bottom_frame)
    button_frame.pack()

    # Create the remove button
    remove_button = tk.Button(button_frame, text="Remove All", command=remove_all_files)
    remove_button.pack(side=tk.LEFT, padx=10)

    # Create the upload button
    upload_button = tk.Button(button_frame, text="Upload to Artifactory", command=upload_files)
    upload_button.pack(side=tk.LEFT, padx=10)
    
    # Initialize upload button state
    update_upload_button_state()

    # Set up application close confirmation
    root.protocol("WM_DELETE_WINDOW", close_app)

    # Run the GUI loop
    root.mainloop()

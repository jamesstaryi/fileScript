import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import shutil

def load_state_data(abbreviation_file, name_file):
    state_data = []
    try:
        with open(abbreviation_file, 'r') as abbrev_file, open(name_file, 'r') as name_file:
            for abbrev_line, name_line in zip(abbrev_file, name_file):
                abbreviation = abbrev_line.strip()
                state_name = name_line.strip()
                state_data.append((abbreviation, state_name))
        return state_data
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return []

def find_states(filename, state_abbreviations, state_names):
    output = []
    try:
        with open(filename, 'r') as file:
            line_number = 1
            for line in file:
                if "CIVID" in line:
                    line_number += 1
                    continue
                
                if line.strip().startswith("-"):
                    line_number += 1
                    continue
                
                found = False
                # Check for abbreviations with boundary conditions
                for abbreviation in state_abbreviations:
                    if re.search(rf'(^|[\s_]){re.escape(abbreviation)}($|[\s_])', line):
                        output.append(f'Line {line_number}: {line.strip()} (Found Abbreviation: {abbreviation})')
                        found = True
                        break
                
                # Check for full state names with boundary conditions
                if not found:
                    for state_name in state_names:
                        if re.search(rf'(^|[\s_]){re.escape(state_name)}($|[\s_])', line):
                            output.append(f'Line {line_number}: {line.strip()} (Found State Name: {state_name})')
                            break

                line_number += 1
    except FileNotFoundError:
        print(f"The file '{filename}' was not found.")
    
    return output

def show_file_output(event):
    clicked_widget = event.widget
    clicked_widget.update_idletasks()
    
    # Retrieve file path associated with the clicked label
    file_path = clicked_widget.path
    
    # Extract file name and color
    file_name = os.path.basename(file_path)
    file_color = clicked_widget.cget("fg")
    
    if file_color == 'green':
        messagebox.showinfo("Info", "This file does not contain any excluded states.")
        return

    state_abbreviations = {abbrev for abbrev, name in state_data if name != selected_state}
    state_names = {name for abbrev, name in state_data if name != selected_state}
    output = find_states(file_path, state_abbreviations, state_names)
    
    if output:
        output_text = '\n'.join(output)
    else:
        output_text = "No states found."
    
    # Create a popup window
    popup = tk.Toplevel(root)
    popup.title(f"Output for {file_name}")
    popup.geometry("600x400")
    
    # Add a Text widget to display the output
    text_widget = tk.Text(popup, wrap=tk.WORD)
    text_widget.pack(expand=True, fill=tk.BOTH)
    text_widget.insert(tk.END, output_text)
    text_widget.config(state=tk.DISABLED)

def on_select(event):
    global selected_state
    selected_state = state_combo.get()

def select_files():
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
            color = 'green' if not has_state else 'red'
            # Update existing entry or add a new one
            if existing_frame:
                # Update existing entry
                existing_frame.winfo_children()[0].config(fg=color)  # Example: Update color
            else:
                # Add new entry
                file_frame = tk.Frame(file_list_frame)
                file_frame.pack(fill=tk.X, padx=5, pady=2)

                # Create label for file name
                file_label = tk.Label(file_frame, text=file_name, fg=color, padx=10, anchor='w')
                file_label.path = file_path
                file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                file_label.bind("<Button-1>", show_file_output)
                
                # Create delete button
                delete_button = tk.Button(file_frame, text="Delete", command=lambda f=file_frame: delete_file_entry(f))
                delete_button.pack(side=tk.RIGHT)
                
                # Create ignore button if the file is red
                if color == 'red':
                    ignore_button = tk.Button(file_frame, text="Ignore", command=lambda f=file_frame: ignore_file_entry(f))
                    ignore_button.pack(side=tk.RIGHT)

        # Update the state of the upload button
        update_upload_button_state()

    else:
        print("Please select a state to exclude.")

def on_drop(event):
    global current_directory
    file_paths = event.data
    file_paths = file_paths.strip().split()
    
    if selected_state:
        state_abbreviations = {abbrev for abbrev, name in state_data if name != selected_state}
        state_names = {name for abbrev, name in state_data if name != selected_state}

        for file_path in file_paths:
            if file_path.startswith("{") and file_path.endswith("}"):
                file_path = file_path[1:-1]  # Remove curly braces from the file path
            
            file_path = file_path.strip()
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
            color = 'green' if not has_state else 'red'
            # Update existing entry or add a new one
            if existing_frame:
                # Update existing entry
                existing_frame.winfo_children()[0].config(fg=color)  # Example: Update color
            else:
                # Add new entry
                file_frame = tk.Frame(file_list_frame)
                file_frame.pack(fill=tk.X, padx=5, pady=2)

                # Create label for file name
                file_label = tk.Label(file_frame, text=file_name, fg=color, padx=10, anchor='w')
                file_label.path = file_path
                file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                file_label.bind("<Button-1>", show_file_output)
                
                # Create delete button
                delete_button = tk.Button(file_frame, text="Delete", command=lambda f=file_frame: delete_file_entry(f))
                delete_button.pack(side=tk.RIGHT)
                
                # Create ignore button if the file is red
                if color == 'red':
                    ignore_button = tk.Button(file_frame, text="Ignore", command=lambda f=file_frame: ignore_file_entry(f))
                    ignore_button.pack(side=tk.RIGHT)

        # Update the state of the upload button
        update_upload_button_state()
    else:
        print("Please select a state to exclude.")

def ignore_file_entry(frame):
    # Mark the file entry as ignored by changing its color or text
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Label):
            widget.config(fg='orange')
    # Update the state of the upload button
    update_upload_button_state()

def delete_file_entry(frame):
    frame.destroy()
    # Update the state of the upload button
    update_upload_button_state()

def upload_files():
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

def update_upload_button_state():
    # Check if there are any red files
    has_red_files = any(
        child.winfo_children()[0].cget("fg") == 'red'
        for child in file_list_frame.winfo_children()
        if isinstance(child, tk.Frame)
    )
    
    # Enable or disable the upload button
    upload_button.config(state=tk.DISABLED if has_red_files else tk.NORMAL)

if __name__ == "__main__":
    # Load state data
    state_data = load_state_data("us-states-abbreviation.txt", "us-states.txt")
    selected_state = None
    current_directory = ""

    # Setup GUI
    root = TkinterDnD.Tk()
    root.title("State Exclusion Tool")
    root.geometry("500x500")
    
    # Dropdown menu
    state_label = tk.Label(root, text="Select a state to exclude:")
    state_label.pack(pady=10)
    state_combo = ttk.Combobox(root, values=[name for _, name in state_data])
    state_combo.bind("<<ComboboxSelected>>", on_select)
    state_combo.pack(pady=10)
    
    # File selection button
    file_button = tk.Button(root, text="Select Files", command=select_files)
    file_button.pack(pady=20)
    
    # Drop area
    drop_label = tk.Label(root, text="Drag and drop files here")
    drop_label.pack(pady=20)
    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind('<<Drop>>', on_drop)
    
    # Listbox to display file names
    file_list_frame = tk.Frame(root)
    file_list_frame.pack(pady=10)
    
    # Upload file to Artifactory
    upload_button = tk.Button(root, text="Upload to Artifactory", command=upload_files)
    upload_button.pack(side=tk.BOTTOM, pady=10)
    
    # Initialize upload button state
    update_upload_button_state()

    # Run the GUI loop
    root.mainloop()
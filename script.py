import tkinter as tk
from tkinter import ttk, filedialog
import re
from tkinterdnd2 import DND_FILES, TkinterDnD
import os

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
    has_state = False
    try:
        with open(filename, 'r') as file:
            line_number = 1
            for line in file:
                if "CIVID" in line:
                    line_number += 1
                    continue
                
                found = False
                # Check for abbreviations with boundary conditions
                for abbreviation in state_abbreviations:
                    if re.search(rf'(^|[\s_]){re.escape(abbreviation)}($|[\s_])', line):
                        has_state = True
                        break
                
                # Check for full state names with boundary conditions
                if not found:
                    for state_name in state_names:
                        if re.search(rf'(^|[\s_]){re.escape(state_name)}($|[\s_])', line):
                            has_state = True
                            break

                line_number += 1
    except FileNotFoundError:
        print(f"The file '{filename}' was not found.")
    
    return has_state

def on_select(event):
    global selected_state
    selected_state = state_combo.get()

def select_files():
    file_paths = filedialog.askopenfilenames(
        title="Select Files",
        filetypes=[("Text Files", "*.txt")],
        defaultextension=".txt"
    )
    
    if selected_state:
        state_abbreviations = {abbrev for abbrev, name in state_data if name != selected_state}
        state_names = {name for abbrev, name in state_data if name != selected_state}
        
        # Clear the listbox
        file_listbox.delete(0, tk.END)
        
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            has_state = find_states(file_path, state_abbreviations, state_names)
            color = 'green' if not has_state else 'red'
            file_listbox.insert(tk.END, file_name, color)
    else:
        print("Please select a state to exclude.")

def on_drop(event):
    file_paths = event.data
    file_paths = file_paths.strip().split()
    
    if selected_state:
        state_abbreviations = {abbrev for abbrev, name in state_data if name != selected_state}
        state_names = {name for abbrev, name in state_data if name != selected_state}
        
        # Clear the listbox
        file_listbox.delete(0, tk.END)
        
        for file_path in file_paths:
            if file_path.startswith("{") and file_path.endswith("}"):
                file_path = file_path[1:-1]  # Remove curly braces from the file path
            
            file_path = file_path.strip()
            file_name = os.path.basename(file_path)
            has_state = find_states(file_path, state_abbreviations, state_names)
            color = 'green' if not has_state else 'red'
            file_listbox.insert(tk.END, file_name)
            file_listbox.itemconfig(tk.END, {'fg': color})
    else:
        print("Please select a state to exclude.")

if __name__ == "__main__":
    # Load state data
    state_data = load_state_data("us-states-abbreviation.txt", "us-states.txt")
    selected_state = None

    # Setup GUI
    root = TkinterDnD.Tk()
    root.title("State Exclusion Tool")
    root.geometry("500x400")
    
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
    file_listbox = tk.Listbox(root, width=60, height=10)
    file_listbox.pack(pady=10)
    
    # Configure listbox tags for colors
    
    
    # Run the GUI loop
    root.mainloop()

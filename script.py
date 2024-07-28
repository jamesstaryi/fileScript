import tkinter as tk
from tkinter import ttk
import re
from tkinterdnd2 import DND_FILES, TkinterDnD

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
                        print(f'File: {filename}, Line {line_number}: {line.strip()} (Found Abbreviation: {abbreviation})')
                        found = True
                        break
                
                # Check for full state names with boundary conditions
                if not found:
                    for state_name in state_names:
                        if re.search(rf'(^|[\s_]){re.escape(state_name)}($|[\s_])', line):
                            print(f'File: {filename}, Line {line_number}: {line.strip()} (Found State Name: {state_name})')
                            break

                line_number += 1
    except FileNotFoundError:
        print(f"The file '{filename}' was not found.")

def on_select(event):
    global selected_state
    selected_state = state_combo.get()

def on_drop(event):
<<<<<<< HEAD
    file_paths = event.data
    file_paths = file_paths.strip().split()
=======
    file_path = event.data
    if file_path.startswith("{") and file_path.endswith("}"):
        file_path = file_path[1:-1]  # Remove curly braces from the file path
    file_path = file_path.strip()
>>>>>>> 880c81c7e15b910d5cac55e6e34d9b5b7848c520
    
    if selected_state:
        state_abbreviations = {abbrev for abbrev, name in state_data if name != selected_state}
        state_names = {name for abbrev, name in state_data if name != selected_state}
<<<<<<< HEAD
        
        for file_path in file_paths:
            if file_path.startswith("{") and file_path.endswith("}"):
                file_path = file_path[1:-1]  # Remove curly braces from the file path
            
            file_path = file_path.strip()
            find_states(file_path, state_abbreviations, state_names)
=======
        find_states(file_path, state_abbreviations, state_names)
>>>>>>> 880c81c7e15b910d5cac55e6e34d9b5b7848c520
    else:
        print("Please select a state to exclude.")

if __name__ == "__main__":
    # Load state data
    state_data = load_state_data("us-states-abbreviation.txt", "us-states.txt")
    selected_state = None

    # Setup GUI
    root = TkinterDnD.Tk()
    root.title("State Exclusion Tool")
    root.geometry("400x200")
    
    # Dropdown menu
    state_label = tk.Label(root, text="Select a state to exclude:")
    state_label.pack(pady=10)
    state_combo = ttk.Combobox(root, values=[name for _, name in state_data])
    state_combo.bind("<<ComboboxSelected>>", on_select)
    state_combo.pack(pady=10)
    
    # Drop area
<<<<<<< HEAD
    drop_label = tk.Label(root, text="Drag and drop files here")
=======
    drop_label = tk.Label(root, text="Drag and drop a file here")
>>>>>>> 880c81c7e15b910d5cac55e6e34d9b5b7848c520
    drop_label.pack(pady=20)
    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind('<<Drop>>', on_drop)

    # Run the GUI loop
    root.mainloop()

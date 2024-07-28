import re

def load_state_data(abbreviation_file, name_file, exclude_state):
    state_abbreviations = set()
    state_names = set()
    
    try:
        with open(abbreviation_file, 'r') as abbrev_file, open(name_file, 'r') as name_file:
            for abbrev_line, name_line in zip(abbrev_file, name_file):
                abbreviation = abbrev_line.strip()
                state_name = name_line.strip()
                
                if exclude_state.lower() not in {abbreviation.lower(), state_name.lower()}:
                    state_abbreviations.add(abbreviation)
                    state_names.add(state_name)
        
        return state_abbreviations, state_names
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return set(), set()

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
                        print(f'Line {line_number}: {line.strip()} (Found Abbreviation: {abbreviation})')
                        found = True
                        break
                
                # Check for full state names with boundary conditions
                if not found:
                    for state_name in state_names:
                        if re.search(rf'(^|[\s_]){re.escape(state_name)}($|[\s_])', line):
                            print(f'Line {line_number}: {line.strip()} (Found State Name: {state_name})')
                            break

                line_number += 1
    except FileNotFoundError:
        print(f"The file '{filename}' was not found.")

if __name__ == "__main__":
    exclude_state = input("Enter the state abbreviation or name to exclude (e.g., 'IL' or 'Illinois'): ").strip()
    state_abbreviations, state_names = load_state_data("us-states-abbreviation.txt", "us-states.txt", exclude_state)
    find_states("IL.txt", state_abbreviations, state_names)

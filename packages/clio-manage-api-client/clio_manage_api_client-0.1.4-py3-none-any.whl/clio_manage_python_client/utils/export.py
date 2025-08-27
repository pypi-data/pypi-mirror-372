import pandas as pd
import os
import random

def save_to_xlsx(json_response: dict, save_path: str = "spreadsheet.xlsx"):

    if "data" not in json_response or not isinstance(json_response["data"], list):
        raise ValueError("'data' key is missing or not a list in the JSON response")

    data = pd.json_normalize(json_response["data"])

    # Ensure the save path is unique
    base, ext = os.path.splitext(save_path)
    count = 1
    while os.path.exists(save_path):
        save_path = f"{base}_{count}{ext}"
        count += 1

    # Ensure the directory exists (if applicable)
    directory = os.path.dirname(save_path)
    if directory:  # Only create directories if a directory path is provided
        os.makedirs(directory, exist_ok=True)

    # Write the DataFrame to an Excel file
    data.to_excel(save_path, index=False)
    print(f"Excel file saved to: {save_path}")
    
    
def get_first_id_from_response(json_response: dict):
    """
    Retrieves the 'id' value from the first dictionary in the 'data' list of a JSON response if it exists.
    """
    # Check if 'data' exists and is a list
    if "data" in json_response and isinstance(json_response["data"], list):
        data_list = json_response["data"]
        if data_list:  # Ensure the list is not empty
            first_entry = data_list[0]
            if isinstance(first_entry, dict) and "id" in first_entry:
                return first_entry["id"]
    
    return None

def get_random_id(json_response: dict, max_retries: int = 10):
    """
    Retrieves a random 'id' value from the 'data' list in the JSON response.
    """
    if "data" not in json_response or not isinstance(json_response["data"], list):
        raise ValueError("'data' key is missing or not a list in the JSON response")

    data_list = json_response["data"]

    for _ in range(max_retries):
        if not data_list:  # If the list is empty, break early
            break
        
        random_entry = random.choice(data_list)
        
        # Check if the entry has an 'id' key
        if isinstance(random_entry, dict) and "id" in random_entry:
            return random_entry["id"]

    return None
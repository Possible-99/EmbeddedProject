import os

def get_names_in_folder(folder_path):
    """Returns a list of file names in the given folder."""
    try:
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    except Exception as e:
        print(f"Error accessing folder: {e}")
        return []
    
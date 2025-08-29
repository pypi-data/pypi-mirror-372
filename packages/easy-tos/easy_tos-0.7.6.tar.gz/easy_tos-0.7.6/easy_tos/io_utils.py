from typing import Dict, List
import os
import shutil

def save_dict_to_json(data: Dict, file_path: str):
    import json
    with open(file_path, 'w') as json_file:
        # Write the dictionary to the file as JSON
        json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"Dict has been successfully saved to {file_path}")

def write_list_to_txt(uid_list: List, file_path: str, verbose: bool = False):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(uid_list))
    if verbose:
        print(f"List has been successfully saved to {file_path}")
        
def clean_local_cache(paths_list, verbose=False):
    """
    Deletes files or directories specified in paths_list.

    :param paths_list: List of file or directory paths to delete.
    """
    for path in paths_list:
        try:
            if os.path.exists(path):
                if os.path.isfile(path) or os.path.islink(path):
                    os.remove(path)  # Remove file or symlink
                    if verbose:
                        print(f"Deleted file: {path}")
                elif os.path.isdir(path):
                    shutil.rmtree(path)  # Remove directory and its contents
                    if verbose:
                        print(f"Deleted directory: {path}")
            else:
                if verbose:
                    print(f"Path does not exist: {path}")
        except Exception as e:
            if verbose:
                print(f"Error deleting {path}: {e}")
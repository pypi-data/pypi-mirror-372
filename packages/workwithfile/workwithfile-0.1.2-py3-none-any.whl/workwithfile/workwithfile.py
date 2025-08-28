import os
import subprocess
import shutil

def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    
def write_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as f:
        result = f.write(content)
    print(f"'{content}' was recorded in {file_path}")

def find_in_file(file_path, keyword):
    content = read_file(file_path)
    if keyword in content:
        print(f"Found '{keyword}' in {file_path}")
    else:
        print(f"Not Found '{keyword} in {file_path}'")

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' has been created")
    else:
        print(f"Folder '{folder_name}' already created")

def delete_path(path):
    if os.path.isfile(path):
        os.remove(path)
        print(f"File '{path}' has been deleted")
    elif os.path.isdir(path):
        shutil.rmtree(path)
        print(f"Folder '{path}' and all the contents has benn deleted")
    else:
        print(f"{path} not found or blocked")

def run_cmd(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("The result of the command execution:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
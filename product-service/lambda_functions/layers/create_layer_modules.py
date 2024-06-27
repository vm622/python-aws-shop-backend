import subprocess
import os
import sys
import shutil
import zipfile

curr_dir = os.path.dirname(__file__)

def pip_install_modules(install_dir, reqs_filename):
    command = ['pip', 'install', '--target', install_dir, '-r', reqs_filename]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"\u2612 Error occurred while installing modules:")
        print(stderr.decode('utf-8'))
    else:
        print(f"\u2611 Modules installed successfully in {install_dir}")

def create_modules_dir(modules_dir):
    modules_dir_path = os.path.join(curr_dir, "python")

    if not os.path.exists(modules_dir_path):
        try:
            os.makedirs(modules_dir_path)
            print(f"\u2611 Directory '{modules_dir_path}' created successfully.")
        except OSError as e:
            print(f"\u2612 Error: Failed to create directory '{modules_dir_path}'. Reason: {e}")
        else:
            print(f"\u2611 Directory '{modules_dir_path}' already exists.")
    
    return modules_dir_path

def zip_modules(modules_path, zipfile_name):
    zip_path = os.path.join(curr_dir, f"{zipfile_name}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(modules_path):
            for file in files:
                zipf.write(os.path.join(root, file), 
                    os.path.relpath(os.path.join(root, file), os.path.join(modules_path, '..')))
    print(f"\u2611 Zip with modules created successfully.")

def delete_modules(modules_dir_path): 
    shutil.rmtree(modules_dir_path)
    print(f"\u2611 Modules removed successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\u2612 Please provide a layer name and packages requirements filename as arguments.")
    else:
        layer_name = sys.argv[1]
        reqs_path = sys.argv[2]
        modules_dir_path = create_modules_dir(layer_name)
        pip_install_modules(modules_dir_path, reqs_path)
        zip_modules(modules_dir_path, layer_name)
        delete_modules(modules_dir_path)

import os
def set_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Change the working directory to the current directory
    os.chdir(current_dir)
    print(current_dir)
import os
import json
import shutil
from subprocess import PIPE, run
import sys

GAME_DIR_PATTERN = "_game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMANDS = ["go", "build"]

#Walks down through all the directories/Folders to find the ones matching
#GAME_DIR_PATTERN and creates a full path to that dirrectory and outputs
#them as a list
def find_all_game_paths(source):
    game_paths = []
    
    for root, dirs, files in os.walk(source):
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)
        break
    return game_paths

#Gets the directory name from the path and strips off the to_strip text
def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)
        
    return new_names

#Creates a directory if it does not exist
def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

#Deletes the directory if it exists in the destination
#Recursively copies the files and directories to the destination
def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source, dest)

#Creates and saves the json metadata file
def make_json_metadata_file(path, game_dirs):
    data = {
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }
    
    with open(path, "w") as f:
        json.dump(data, f)

def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break#Finds the first one and stops
        
        break
    
    if code_file_name is None:
        return
    
    command = GAME_COMPILE_COMMANDS + [code_file_name]
    run_command(command, path)

def run_command(command, path):
    cwd = os.getcwd()#gets the current working directory
    os.chdir(path)#Changes the directory
    
    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True, shell=True)
    print("Compile result:", result)
    
    os.chdir(cwd)#changes the directory back

def main(source, target):
    #Don't get smart...just use these to get the file location instead fo trying to build them manually
    cwd = os.getcwd()#Current Working Directory
    source_path = os.path.join(cwd, source)
    target_path = os.path.join(cwd, target)
    
    game_paths = find_all_game_paths(source_path)
    new_game_dirs = get_name_from_paths(game_paths, GAME_DIR_PATTERN)
    
    create_dir(target_path)
    #Zipz the lists together then assigns the values to src and dest to loop through them
    #a = [1, 2, 3]
    #b = [a, b, c]
    #zip(a,b) = [(1, a), (2, b), (3, c)]
    for src, dest in zip(game_paths, new_game_dirs):#Zip creates a touple from equal length arrays
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path)
    
    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)

#Prevents the script from running unless this it is run from command line with command line arguments
if __name__ == "__main__":
	args = sys.argv
	if len(args) != 3:
		raise Exception("You must pass a source and target directory - only.")
	
	source, target = args[1:]
	main(source, target)
	
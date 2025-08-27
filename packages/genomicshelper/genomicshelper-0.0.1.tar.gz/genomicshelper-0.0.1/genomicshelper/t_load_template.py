import os

def _load_template():
    home_directory = os.path.expanduser("~")
    tempplate_dir = os.path.join(home_directory, ".genomicshelper")
    
    files = os.listdir( tempplate_dir )
    
    dic = dict()

    for file in files:
        if file[-4:]==".tmp":
            key = file[:-4]
            value = _load_txt( os.path.join( tempplate_dir,file) )
            dic[key] = value

    return dic

def _load_txt(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content_string = file.read()
        return file_content_string
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
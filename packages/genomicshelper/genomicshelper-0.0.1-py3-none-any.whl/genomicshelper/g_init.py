import shutil
import os
from .g_Log import Log

def _init(src_dir=None, 
          dst_dir=None,
          overwrite=False,
          log=Log()):
    
    src_dirs=[]
    
    if src_dir is not None:
        src_dirs.append(src_dir)

    filedir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(filedir, 'template')
    src_dirs.append(src_dir)

    if dst_dir is None:
        home_dir = os.path.expanduser("~")              # /home/username or /Users/username
        dst_dir = os.path.join(home_dir, ".genomicshelper")
    
    log.write('Copying to directory : {}'.format(dst_dir))   
    # Loop through files in source
    for src_dir in src_dirs:
        log.write('Copying from directory : {}'.format(src_dir))
        for filename in os.listdir(src_dir):
            if filename[-4:]==".tmp" or filename[-7:]==".header":
                src_file = os.path.join(src_dir, filename)
                dst_file = os.path.join(dst_dir, filename)

                # Only copy files (skip directories)
                if not os.path.exists(dst_file) or overwrite==True:  # skip if exists
                    log.write(f'Copying {filename}')
                    shutil.copy2(src_file, dst_file)  # copy2 preserves metadata
                else:
                    log.warning(f'Skipping {filename} (already exists)')
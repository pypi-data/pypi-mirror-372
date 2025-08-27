import os
from .g_Log import Log
from .t_load_template import _load_txt
from .t_parse_template import _parse_template

def _add_template( fullpath_from,
                   keyword=None,
                   overwrite=False,
                   log=Log()):
    
    basename = os.path.basename(fullpath_from)
    dirname = os.path.dirname(fullpath_from)
    
    home_directory = os.path.expanduser("~")
    tempplate_dir = os.path.join(home_directory, ".genomicshelper")

    if keyword is None:
        new_basename = basename.replace(".sh",".tmp")
    else:
        new_basename = "{}.tmp".format(keyword)

    new_dirname = tempplate_dir

    fullpath_to = os.path.join(new_dirname, new_basename) 

    
    log.write("Adding script: {} as template with keyword: [{}]".format(fullpath_from , new_basename))
    log.write("Adding script to: {}".format(new_dirname))

    if os.path.exists(fullpath_to):
        log.warning("{} exists!".format(fullpath_to))
        if overwrite == False:
            log.warning("Please try another keyword or add -o to overwrite!")
            return 0 
        else:
            log.warning("{} overwritten!".format(fullpath_to))
    
    script = _load_txt( fullpath_from )
    
    arguments= _parse_template(script)
    
    script_with_header = _add_header(arguments, script)

    with open(fullpath_to,"w") as file:
        file.write(script_with_header)
    
    return 0



def _add_header(arguments, script, shebang="#!/bin/bash\n"):
    header = '''## 
#################################
## NOTE #########################
##
#################################
## ARGUMENTS ####################
'''
    for i in arguments:
        header += "## {}: \n".format(i) 
    
    header +='''#################################

'''
    script_with_header = shebang+ header + script 
    return script_with_header
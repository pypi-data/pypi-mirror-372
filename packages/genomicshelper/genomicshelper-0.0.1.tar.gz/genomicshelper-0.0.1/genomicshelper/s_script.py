
def _create_script(interp=None, 
                   tool=None, 
                   **kwargs):
    
    script = ""
    
    if interp is not None:
        script += '{} '.format(interp)

    if tool is not None:
        script += '{} '.format(tool)
    
    for key in kwargs.items():
        script += '{} '.format(tool)
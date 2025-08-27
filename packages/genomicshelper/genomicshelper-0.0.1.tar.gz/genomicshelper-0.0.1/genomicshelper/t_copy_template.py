import os
from .g_Log import Log
from .t_parse_template import _parse_template
from .t_parse_template import _parse_default
from .t_load_header import _load_header

def _check_template(key = None, 
                   dic = None, 
                   header=None,
                   verbose=True,
                   log=Log()):
    

    if type(key) is str:
        value = dic[key]
        value = _insert_args(value)
        if header is not None:
            if type(header) is list:
                for signle_header in header[::-1]:
                    log.write("Adding HEADER {}.header...".format(signle_header),verbose=verbose)
                    value = _insert_header(value, signle_header)
            else:        
                log.write("Adding HEADER {}.header...".format(header),verbose=verbose)
                value = _insert_header(value, header)
    elif type(key) is list:
        value = dic[key[0]]

        for single_key in key[1:]:
            value = _insert_script(dic, single_key, value)

        value = _insert_args(value)

        if header is not None:
            if type(header) is list:
                for signle_header in header[::-1]:
                    log.write("Adding HEADER {}.header ...".format(signle_header),verbose=verbose)
                    value = _insert_header(value, signle_header)
            else:        
                log.write("Adding HEADER {}.header...".format(header),verbose=verbose)
                value = _insert_header(value, header)

    return value

def _copy_template(key = None, 
                   dic = None, 
                   header=None,
                   path = "./", 
                   log=Log()):

    if type(key) is str:
        value = dic[key]
        fullpath = _get_fullpath(path, key, log)
        value = _insert_args(value)
        if header is not None:
            if type(header) is list:
                for signle_header in header[::-1]:
                    log.write("Adding HEADER {}.header to {}...".format(signle_header, fullpath))
                    value = _insert_header(value, signle_header)
            else:        
                log.write("Adding HEADER {}.header to {}...".format(header, fullpath))
                value = _insert_header(value, header)
    elif type(key) is list:
        value = dic[key[0]]
        fullpath = _get_fullpath(path, key[0], log)

        for single_key in key[1:]:
            value = _insert_script(dic, single_key, value)

        value = _insert_args(value)

        if header is not None:
            if type(header) is list:
                for signle_header in header[::-1]:
                    log.write("Adding HEADER {}.header to {}...".format(signle_header, fullpath))
                    value = _insert_header(value, signle_header)
            else:        
                log.write("Adding HEADER {}.header to {}...".format(header, fullpath))
                value = _insert_header(value, header)

    with open(fullpath,"w") as file:
        file.write(value)
    return 0

def _insert_script(dic, key, value):
    script_text = dic[key].split("\n")[1:]

    lines = value.split("\n")
    lines += script_text
    value = "\n".join(lines)
    return value

def _insert_header(value, header):
    header_text = _load_header(header)
    lines = value.split("\n")
    position_to_insert = 1
    lines.insert(position_to_insert, header_text)
    value = "\n".join(lines)
    return value

def _insert_args(value):
    matches = _parse_template(value)
    defaults= _parse_default(value)

    lines = value.split("\n")
    for index, line in enumerate(lines):
        if line[:1]!="#":
            position_to_insert = index
            break

    defining_script=''
    for key in matches:
        if key in defaults.keys():
            defining_script+= '{}={} \n'.format(key, defaults[key])
        else:
            defining_script+= '{}= \n'.format(key,)

    lines.insert(position_to_insert, defining_script)
    value = "\n".join(lines)
    return value

def _get_fullpath(path, key, log):
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)

    if basename=="":
        basename = "{}.sh".format(key)
    
    fullpath = os.path.join(dirname, basename) 
    log.write("Copying template [{}] to: {}".format(key ,fullpath))

    if os.path.exists(fullpath):
        log.warning("{} exists! Adding suffix to avoid duplicates.".format(fullpath)) 

        for i in range(0,10000):
            old = '.'
            new = '.{}.'.format(i)
            maxreplace = 1
            newbasedname = new.join(basename.rsplit(old, maxreplace))

            fullpath = os.path.join(dirname, newbasedname) 
            if not os.path.exists(fullpath):
                log.write("Copying to: {}".format(fullpath))
                return fullpath
            else:
                log.warning("{} exists! Changing suffix to avoid duplicates.".format(fullpath)) 
    else:
        return fullpath
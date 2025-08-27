import re

def _search_template(dic=None,
                     p=None):
    if dic!=None:
        matched_keys = []
        for i in dic.keys():
            matches = re.findall(p, i)
            if len(matches)>0:
                matched_keys.append(i)
        return matched_keys
    else:
        return None
    
def _search_template_descriptions(dic=None, 
                                  p=None):
    if dic is not None:
        matched_keys = []
        for i in dic.keys():
            first_line = _get_first_file(dic, i)
            matches = re.findall(p, first_line)
            if len(matches)>0:
                matched_keys.append(i)
        return matched_keys
    else:
        return None
    
def _get_first_file(dic, key):
    first_line=''
    for line in dic[key].split("\n"):
                if line[:2]=="##":
                    first_line = line
                    break 
    return first_line
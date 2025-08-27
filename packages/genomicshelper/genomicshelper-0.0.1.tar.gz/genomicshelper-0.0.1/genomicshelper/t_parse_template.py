import re

def _parse_template(template):
    # get unique matches
    
    matches = re.findall(r'\$\{(\w+)\}', template)
    
    # keep order
    unique_matches = list(dict.fromkeys(matches))

    return unique_matches

def _parse_default(template):
    matches = re.findall(r'##[ ]*([_/\"\'\w]+)[ ]*=[ ]*([_/\"\'\w]+)[ ]*:?', template)
    if len(matches)>0:
        default_dic = dict(matches)
    else:
        default_dic=dict()
    return default_dic
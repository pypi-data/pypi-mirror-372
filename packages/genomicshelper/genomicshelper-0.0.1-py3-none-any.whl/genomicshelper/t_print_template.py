
def _print_first_line(matches, p, log, verbose):
    for index, key in enumerate(matches):
        first_line = ""
        for line in p.templates[key].split("\n"):
            if line[:2]=="##":
                first_line = line
                break 
        log.write("{} [{}]: {}".format(index,key, first_line), show_time=False, verbose=verbose)
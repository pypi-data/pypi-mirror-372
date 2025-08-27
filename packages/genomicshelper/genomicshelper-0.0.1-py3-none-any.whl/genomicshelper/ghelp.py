#!/usr/bin/env python

import argparse
from .g_Protocol import Protocol
from .t_parse_template import _parse_template
from .t_copy_template import _copy_template
from .t_copy_template import _check_template
from .t_add_template import _add_template
from .t_print_template import _print_first_line
from .g_Log import Log
import os
from .g_init  import _init

def parse_unknown_as_dict(unknown_args):
    """
    把未知参数解析成字典：
    - 支持 --key value
    - 支持 --key=value
    - 值可包含空格
    """
    result = {}
    key = None
    value_parts = []

    def commit_key():
        """保存当前 key 和累积的 value_parts"""
        if key is not None:
            result[key] = " ".join(value_parts).strip() if value_parts else None
        else:
            result["_GHELP"] = value_parts
            #result["GHELP"] = " ".join(value_parts).strip() if value_parts else None

    for arg in unknown_args:
        if arg.startswith("--"):
            # 如果正在处理上一个 key，先保存它
            commit_key()
            value_parts.clear()

            if "=" in arg:
                # --key=value 形式
                k, v = arg[2:].split("=", 1)
                result[k] = v
                key = None
            else:
                # --key value... 形式
                key = arg.lstrip("-")
        else:
            # 累积值（支持多单词）
            #if key is not None:
            value_parts.append(arg)

    # 循环结束后提交最后一个 key
    commit_key()
    return result


def main():
    log = Log()
    
    p = Protocol(log=log)
    p.load_templates()
    p.load_headers()

    parser = argparse.ArgumentParser(description="Genomics helper.")

    parser.add_argument('-a', "--add", default=None, help="Add existing script as template.")
    parser.add_argument('-r', "--run", default=None, help="Run specific script template with arguments.")
    parser.add_argument('-nr', "--nologrun", default=None, help="Run specific script template with arguments without showing the ghelp log..")
    parser.add_argument('-c', "--check", default=None, help="Check arguments in template.")
    parser.add_argument('-g', "--get", default=None, help="Copy template to specified directory. Default: ./ ")
    parser.add_argument('-s', "--search", default=None, help="Search template by checking if the keywords contain the specified pattern.")
    parser.add_argument('-sd', "--searchd", default=None, help="Search template by checking if the template description contain the specified pattern.")
    parser.add_argument('-l', '--list', default=False, action='store_true', help="List all templates.")
    parser.add_argument('-lh', '--listheaders', default=False, action='store_true', help="List all headers.")
    parser.add_argument('-o', '--overwrite', default=False, action='store_true', help="Whether overwrite the existing file.")
    parser.add_argument('--init', default=False, action='store_true',help="Copy template and HEADER from the current directory to ~/.genomicshelper")
    parser.add_argument('-n', '--nolog', default=False, action='store_true',  help="No logging message will be displayed.")
    parser.add_argument('-t', '--threads', default=1, help="Run with the specified number of CPU Threads")
    parser.add_argument('-m', '--memory', default=1024, help="Run with the specified memory in MB")
    parser.add_argument('-v', '--version',default=False, action='store_true', help="Show ghelp version")
    args, unknown = parser.parse_known_args()
    

    ######################################################################################################################
    if args.nologrun is not None:
        # shortcut for run and nolog
        args.nolog = True
        args.run = args.nologrun

    verbose = not args.nolog
    header=None

    if args.get is not None:
        if ":" in args.get:
            header = args.get.split(":")[0].split("+")
            args.get = args.get.split(":")[1]
        if "+" in args.get:
            args.get = args.get.split("+")
    
    if args.check is not None:
        if ":" in args.check:
            header = args.check.split(":")[0].split("+")
            args.check = args.check.split(":")[1]
        
        if "+" in args.check:
            args.check = args.check.split("+")
    
    if args.version==True:
        log.write("Genomics helper v0.1 (C) 2025-2025, Yunye He, MIT license, gwaslab@gmail.com")
        verbose = False

    ######################################################################################################################
   
    log.write("Strating Genomics helper...", verbose=verbose)

    if args.init ==True:
        if len(unknown)==0: unknown.append("./")
        log.write("Initiating genomicshelper.", verbose=verbose)
        _init(src_dir = unknown[0], overwrite=args.overwrite)

    if args.list == True:
        key_list = list(p.templates.keys())
        key_list.sort()
        for index, key in enumerate(key_list):
            first_line = ""
            for line in p.templates[key].split("\n"):
                if line[:2]=="##":
                    first_line = line
                    break 
            log.write("{} [{}]: {}".format(index,key, first_line), show_time=False, verbose=verbose)


    if args.listheaders == True:
        key_list = list(p.headers.keys())
        key_list.sort()
        for index, key in enumerate(key_list):
            log.write("{} {:#<60}:\n{}".format(index,  key + " ", p.headers[key]), show_time=False, verbose=verbose)

    ######################################################################################################################
    if args.add is not None:
        if not os.path.exists(args.add):
            # if not found, search
            log.warning("{} not found! Please check file path.".format(args.add))
        else:
            if len(unknown)==0: unknown.append(None)
            _add_template( fullpath_from=args.add,
                           keyword = unknown[0],
                           overwrite = args.overwrite,
                           log=log)
            
    ######################################################################################################################
    if args.get is not None:
        if type(args.get) is str:
            if args.get not in p.templates.keys():
                # if not found, search
                log.warning("{} not found...".format(args.get))
                args.search = args.get 
                return 0
        elif type(args.get) is list:
            for single_key in args.get:
                if single_key not in p.templates.keys():
                    # if not found, search
                    log.warning("{} not found...".format(args.get))
                    args.search = args.get 
                    return 0
        
        if len(unknown)==0: unknown.append("./")
        _copy_template(key=args.get,
                    dic=p.templates,
                    path= unknown[0],
                    header = header,
                    log=log)

    ######################################################################################################################

    if args.check is not None:
        if type(args.check) is str:
            if args.check not in p.templates.keys():
                # if not found, search
                log.warning("{} not found...".format(args.check))
                args.search = args.check 
                return 0
        elif type(args.check) is list:
            for single_key in args.check:
                if single_key not in p.templates.keys():
                    # if not found, search
                    log.warning("{} not found...".format(args.check))
                    args.search = args.check 
                    return 0

        script = _check_template(key=args.check,
                    dic=p.templates,
                    header = header,
                    log=log,
                    verbose=verbose)
        matches = _parse_template(script)
        log.write(f"Arguments in {args.check}", verbose=verbose)
        log.write(f"Arguments: {set(matches)}", verbose=verbose)
        log.linebreak("Script", verbose=verbose)
        log.write(script, show_time=False)
        log.linebreak(verbose=verbose)
    ######################################################################################################################

    if args.search is not None:
        log.write("Keywords for searching: {}".format(args.search))
        matches = p.search_templates(p=args.search)
        #matches = ",".join(matches)
        log.write(f"Matched templates: {matches}", verbose=verbose)
        _print_first_line(matches, p, log, verbose)
    ######################################################################################################################
    if args.searchd is not None:
        log.write("Keywords for searching: {}".format(args.searchd))
        matches = p.search_template_descriptions(p=args.searchd)
        #matches = ",".join(matches)
        log.write(f"Matched templates: {matches}", verbose=verbose)
        _print_first_line(matches, p, log, verbose)
    ######################################################################################################################
    #run script
    if args.run is not None:
        unknown_args = parse_unknown_as_dict(unknown)
        output = p.run_protocol(args.run, 
                                n_cores=args.threads, 
                                memory= args.memory, 
                                verbose=verbose,
                                **unknown_args)
        log.write(output,show_time=False,end="")
        log.save(path="./{}.log".format(args.run),verbose=verbose)
    ######################################################################################################################
    log.write("Finished Genomics helper...", verbose=verbose) 
    return 0

if __name__ == "__main__":
    main()


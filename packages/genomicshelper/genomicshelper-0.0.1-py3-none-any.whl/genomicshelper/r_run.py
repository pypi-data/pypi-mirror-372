import subprocess
from .g_Log import Log
import resource
import sys
import os
import signal
from .t_parse_template import _parse_template
from .t_parse_template import _parse_default

def _run_script(*args,**kwargs):
    script = " ".join(args)

    try:
        output = subprocess.check_output(script, 
                                         stderr=subprocess.STDOUT, 
                                         shell=True,
                                         text=True)
        return output
    
    except subprocess.CalledProcessError as e:
        return e.output
    
def _run_protocol(template,
                  log=Log(),
                  n_cores=1,
                  memory=1024,
                  verbose=True,
                  **kwargs):
    
    ################################################################
    # if only one argument is provided and there is only one variable in script, match the variable with the argument
    defaults = _parse_default(template)
    #matches = _parse_template(template)
    #if len(matches)==1 and len(kwargs.keys())==1:
    #    if "GHELP" in kwargs.keys():
    #        kwargs[matches[0]] = kwargs["GHELP"]
    #kwargs.pop('GHELP', None)

    kwargs = _match_args_with_kwargs(template, kwargs)

    ################################################################
    
    defaults.update(kwargs)

    script =_insert_key_value( template, **defaults)

    #script =_insert_key_value( template, **kwargs)
    
    log.write("Script ###########################",verbose=verbose)
    log.write(script,show_time=False,verbose=verbose)
    log.write("##################################",verbose=verbose)
    log.write(f"Memory:{memory}MB",verbose=verbose)
    log.write(f"CPU:{n_cores}",verbose=verbose)

    def set_limits():
        try:
            #resource.setrlimit(resource.RLIMIT_CPU, (int(n_cores), int(n_cores)))
            if memory is not None:
                mem_limit = int(memory) * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_limit, mem_limit))
        except Exception as e:
            # Direct write to stderr (safe in forked child)
            os.write(2, f"[preexec_fn] set_limits failed: {e}\n".encode())
        try:
            if hasattr(os, "sched_setaffinity"):
                os.sched_setaffinity(0, set(range(int(n_cores))))
        except Exception:
            pass  # Ignore if unsupported
    
    try:
        log.write("Running by initiating a subprocess...",verbose=verbose)
        output = subprocess.check_output(script, 
                                         stderr=subprocess.STDOUT, 
                                         preexec_fn = set_limits,
                                         shell=True,
                                         text=True)
        log.write("Subprocess was finished successfully.",verbose=verbose)
        log.write("Return ###########################",verbose=verbose)
        return output
    
    except subprocess.CalledProcessError as e:
        log.warning("")
        log.write(e.output, show_time=False)
        log.warning("CalledProcessError Failed!")

        if e.returncode > 128:
            sig = e.returncode - 128
            if sig == signal.SIGKILL:
                log.warning("Killed by SIGKILL → probably out of memory")
            elif sig == signal.SIGSEGV:
                log.warning("Killed by SIGSEGV → memory violation / too high allocation")
        else:
            if "MemoryError" in e.output:
                log.warning("Python MemoryError inside subprocess")
        
    except subprocess.SubprocessError as e:
        log.warning(e)
        log.warning("SubprocessError Failed!")


def _insert_key_value(value, **kwargs):
    lines = value.split("\n")
    for index, line in enumerate(lines):
        if line[:1]!="#":
            position_to_insert = index
            break
    defining_script=''
    for key,value in kwargs.items():
        defining_script+= '{}={}\n'.format(key, value)
    lines.insert(position_to_insert, defining_script)
    value = "\n".join(lines)
    return value

def _match_args_with_kwargs(template, kwargs):

    matches = _parse_template(template)

    if len(kwargs.keys())==1:
        if "_GHELP" in kwargs.keys():
            if len(matches) == len(kwargs["_GHELP"]):
                for index, value in enumerate(matches):
                    kwargs[value] = kwargs["_GHELP"][index]

    kwargs.pop('_GHELP', None)
    return kwargs

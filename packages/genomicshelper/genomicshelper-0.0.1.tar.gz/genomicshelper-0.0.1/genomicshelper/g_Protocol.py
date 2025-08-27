from .r_run import _run_script
from .r_run import _run_protocol
from .t_load_template import _load_template
from .t_search_template import _search_template
from .t_search_template import _search_template_descriptions
from .t_load_header import _load_headers
from .g_Log import Log

class Protocol():

    def __init__(self, log=Log()):
        self.log = log
        self.templates = dict()

    def run_script(self, *args,**kwargs):
        output = _run_script(*args,**kwargs)
        return output
    
    def run_protocol(self, protocol, verbose=True,**kwargs):
        template = self.templates[protocol]
        output = _run_protocol(template = template, 
                               log = self.log, 
                               verbose=verbose,
                               **kwargs)
        return output
    
    def load_templates(self):
        self.templates = _load_template()
    
    def load_headers(self):
        self.headers = _load_headers()

    def search_templates(self, p):
        return _search_template(dic = self.templates, p=p)
    
    def search_template_descriptions(self, p):
        return _search_template_descriptions(dic = self.templates, p=p)
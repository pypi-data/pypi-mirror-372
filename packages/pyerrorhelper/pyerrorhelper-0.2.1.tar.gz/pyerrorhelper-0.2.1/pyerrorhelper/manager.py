import sys
from pyerrorhelper.ollamembedder import OllamaEmbedder
import traceback 

class ErrorManager:
    def __init__(self):
        self.slm = OllamaEmbedder()
        self.old_hook = sys.excepthook

    def handle_error(self, exc_type, exc_value, exc_traceback):
        tb_list = traceback.format_tb(exc_traceback)
        tb_output = "".join(tb_list)
        print(self.slm.summarize(tb_output))

    
    def install(self):
        sys.excepthook = self.handle_error
    
    def uninstall(self):
        sys.excepthook = self.old_hook
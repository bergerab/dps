from datetime import datetime

class Logger:
    '''
    A configurable printer.
    '''
    def __init__(self, verbose):
        self.verbose = verbose

    def _print(self, *args):
        print(datetime.now(), ': ', *args)
            
    def error(*args):
        self._print(*args)        

    def log(*args):
        if verbose:
            self._print(*args)

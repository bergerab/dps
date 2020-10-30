from datetime import datetime

class Logger:
    '''
    A configurable printer.
    '''
    def __init__(self, verbose):
        self.verbose = verbose

    def _print(self, *args):
        print('DPS BP', str(datetime.now()) + ':', *args)
            
    def error(self, *args):
        self._print(*args)        

    def log(self, *args):
        if self.verbose:
            self._print(*args)

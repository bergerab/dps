POP_JOB_POSTFIX = '/api/v1/pop_job'
RESULT_POSTFIX = '/api/v1/result'
PROGRESS_POSTFIX = '/api/v1/progress'

class Logger:
    def __init__(self, verbose):
        self.verbose = verbose

    def log(*args):
        if verbose:
            print(*args)


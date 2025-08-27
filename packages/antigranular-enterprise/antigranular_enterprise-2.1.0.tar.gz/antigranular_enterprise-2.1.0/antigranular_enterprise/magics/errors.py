from IPython import get_ipython
class AGRuntimeError(Exception):
    def __init__(self, etype="Error", evalue="AG Runtime Error", msg=None):
        self.error_data = f"{etype}:\n{evalue}"
        self.tb = evalue

    def __str__(self):
        error_msg = f"{self.error_data}"
        if self.tb:
            error_msg += f"\nServer Traceback:\n{self.tb}"
        return error_msg


class AGTimeOutError(Exception):
    def __init__(self, etype="Error", evalue="AG TimeOut Error", msg=None):
        self.error_data = f"{etype}:\n{evalue}"
        self.tb = "Client TimeOut while waiting for server output"

    def __str__(self):
        error_msg = f"{self.error_data}"
        if self.tb:
            error_msg += f"\nServer Traceback:\n{self.tb}"
        return error_msg


def custom_exc(shell, etype, evalue, tb, tb_offset=None):
    return

# Use our custom exception handler
get_ipython().set_custom_exc((AGRuntimeError,), custom_exc)

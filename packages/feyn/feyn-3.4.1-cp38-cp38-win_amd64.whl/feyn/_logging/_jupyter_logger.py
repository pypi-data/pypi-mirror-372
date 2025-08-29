from logging import Logger, INFO, DEBUG

def _display(msg):
    from IPython.display import Markdown, display
    display(Markdown(msg))

class JupyterLogger(Logger):
    """A Logger extension for Jupyter environments that allows us to directly display some messages instead of logging them.
    
    The display functionality can be overridden by setting `use_display` to False, which will make it revert to the standard logger.
    Example:
    >>> logger = getLogger("feyn")
    >>> logger.use_display = False

    Arguments:
        Logger logging.Logger -- An already instantiated logger using logging.getLogger.
    """
    use_display = True

    def info(self, msg, *args, **kwargs):
        if self.use_display and self.isEnabledFor(INFO):
            _display(msg)
        else:
            # revert to default behaviour
            super(JupyterLogger, self).info(msg, *args, **kwargs)
    
    def debug(self, msg, *args, **kwargs):
        if self.use_display and self.isEnabledFor(DEBUG):
            msg = f"[DEBUG] - {msg}"
            _display(msg)
        else:
            # revert to default behaviour
            super(JupyterLogger, self).debug(msg, *args, **kwargs)
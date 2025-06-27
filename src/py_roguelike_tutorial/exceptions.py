class Impossible(Exception):
    """Exception raised when an action is impossible to be performed.

    The reason is given as the exception message.
    """
    
class QuitWithoutSaving(Exception):
    """Raised to exit the game without autosave."""

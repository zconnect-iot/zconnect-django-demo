from zconnect.util.exceptions import WorkerError


class InvalidEventDefinitionRef(WorkerError):
    """ Raised when a worker passed a event definition with an invalid ref """



class TransformError(Exception):
    pass


class CannotFindOwner(WorkerError):
    """ Raised when a worker cannot find owner """
    def __init__(self, owner_type):
        self.error_description = "Cannot find {} owner".format(owner_type)



class WellNotFreeException(Exception):

    def __init__ (self, position = None):

        message = f'Position {position.label} already in use' if position else "Position already in use"        

        super().__init__(message)

        return
    
class DuplicateEntryException(Exception):
    pass

class MissingEntryException(Exception):
    pass

class PlateEntryMatchException(Exception):
    pass

class NotEnoughWellsException(Exception):
    pass

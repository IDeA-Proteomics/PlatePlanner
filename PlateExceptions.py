

class WellNotFreeException(Exception):

    def __init__ (self, position = None):

        self.message = f'Position {position} already in use' if position else "Position already in use"    
        self.position = position    

        super().__init__(self.message)

        return
    
class DuplicateEntryException(Exception):
    pass

class MissingEntryException(Exception):
    pass

class PlateEntryMatchException(Exception):
    pass

class NotEnoughWellsException(Exception):
    def __init__ (self, requested, available):
        ## send back the number of actually available wells with the error
        ## in case caller wants to split between plates. 
        self.avalable = available
        self.requested = requested
        self.message = f'{requested} wells were requested but only {available} are available!'

        super().__init__(self.message)

        return

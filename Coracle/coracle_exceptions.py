class ParseException(Exception):
    '''
    When a parser encountered an invalid paramater,
    throw this exception
    '''
    pass

class SessionException(Exception):
    '''
    When ITSdriver encounters an error, raise this 
    exception
    '''
    pass

class HistoryManagerException(Exception):
    '''
    When the history manager has a problem managing
    a list of shifts, raise this error
    '''
    pass

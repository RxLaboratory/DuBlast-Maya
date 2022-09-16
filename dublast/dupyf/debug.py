import time

class Logger( ):
    """Logs messages to the console (and on file)"""
    
    toolName = ""
    
    def log( self, log = "", time_start = 0 ):
        """Logs a message"""
        t = time.time() - time_start
        print( " ".join( [ self.toolName , " (%.2f s):" % t , log ] ) )
from multiprocessing import Process, Queue, Pipe
import collections
import time
import signal
from datetime import datetime as dt
import logging


class AbstractManager( object ):
    """Abstract implementation of a manager. 
    
    A manager is similar to a server or daemon process. It sits and listners for events
    and then carries them out accordingly. Through its pipes it can receive
    and send information. The manager is backed by a dispatcher, which is
    run as a separate subprocess, allowing it to be run concurrently with
    other managers and processes. 
    
    PUBLIC IVARS:
     * process:    Multiprocessing Process object that represents this
                   manager's subprocess.
    
    DISPATCHER:
    Method `dispatcher` implements the event loop for this subprocess. It
    waits for instructions to be sent through the connection and handles
    them accordingly. An instruction takes the form of a list `a`, where
        len(a) >= 1,
        a[0] is the manager method to be called,
    and a[1:] are arguments for the method (`self` should not be included).
    
    The internal process (`self.process`) reads instructions from the pipe
    (`_subproc_connection` and `_parent_connection`). Users of the manager
    need not worry about this, however, as the manager should implement wrapper
    functions carry out the sending and receiving messages through the connection
    endpoint. (E.g., see `stop_process` vs `_stop_process`.)

    BLOCKING VS NONBLOCKING INSTRUCTIONS:
    Two types of instruction may be implemented by subclasses.
    For instructions that do not solicit a response, the instruction can
    be placed on the dispatcher's queue and left. 
    Alternatively, and especially in the case of instructions that seek
    a response, the wrapper method can place the instruction on the queue
    and then block until the underlying method is dispatched and returns 
    a response through the pipe
    back to the wrapper method.
    
    PROCESS STATE 
    Note that as soon as `process.start()` is called, the manager object 
    running in the process becomes an indepndent copy of the original manager
    object. Thus, at the point at which `start()` is called, from this point on,
    all communication  and manipulation of the object should exclusively be 
    done using the manager wrapper methods (or by invoking methods through the 
    communication pipe).
    (Specifically, all state-changing actions should be executed through the
    dispatcher.)
    
    MANAGER INDEPENDENCE
    Instructions for a specific HP are handled in-order by that manager.
    There is no guaranteed overall ordering among instructions for different
    managers.
    For example, if instructions are received as follows:
      A1, A2, B1, A3, B2, A4
    The following ordering guarantees are made:
      A1 < A2 < A3 < A4
    and
      B1 < B2.
    On the other hand, the following would not be guaranteed:
      A1 < B1.
    """
    
    def __init__( self ):
        """~
        """
        parent_conn, child_conn = Pipe()
            # parent_conn: the connection to be held by the parent
            #   .send()  sends info to the child's connection
            #   .recv()  receives info from the child's connection
        
        # Internals
        self._stop_request_received = False 
        self._subproc_connection = child_conn
            # the endpoint used by the dispatcher and dispatched methods.
        self._parent_connection = parent_conn 
           # the endpoint used by the parent for two-way comm with this 
           # manager's dispatcher subprocess.
        
        # Public
        self.process = Process( target=self.dispatcher )
    
    def stop_process( self ):
        self._parent_connection.send( ['_stop_process',] )
    
    def _stop_process( self ):
        self._stop_request_received = True
    
    def dispatcher( self ):
        while not self._stop_request_received:
            obj = self._subproc_connection.recv()  # blocks until object available
            fname = obj[0]
            args = obj[1:]
            
            print "args:", args, "~"
            
            func = getattr( self, fname )
            func( *args )


class ExampleManager( AbstractManager ):
    # Decorators could be written for the wrapper methods. The methods
    # themselves would be empty. The decorator would figure out the
    # function name and putting on the dispatch queue. 
    # Both wrapper (`f`) and underlying method (`_f`) would be required in
    # the class definition. 
    
    def nonblocking_method( self ):
        """
        Example method implementing one of this manager's instructions.
        
        This is the main point of all for external objects. There is an
        underlying companion method, `_nonblocking_method`, which actually
        carries out the instruction. This method (`nonblocking_method`) is
        a helper method which simply puts the instruction on the queue
        to be dispatched later.
        
        Nonblocking:
        This method will add the instruction to the queue and then return. 
        The instruction may not have been handled by the time this method 
        returns. 
        """
        self._parent_connection.send( ['_nonblocking_method',] )
    
    def _nonblocking_method( self ):
        """
        The underlying companion method to `nonblocking_method`. 
        Should not be called directly. Instead, should be executed by the
        manager's dispatcher.
        """
        print "done!"
    
    
    def blocking_method( self ):
        """
        Similar to the other example method (`nonblocking_method`), but
        this this method implements an instruction that returns data.
        
        Blocking:
        This method will block until the internal subprocess has dispatched the
        underlying instruction and received its response.
        """
        self._parent_connection.send( ['_blocking_method',] )
        ret = self._parent_connection.recv()  # blocks
        return ret
    
    def _blocking_method( self ):
        self._subproc_connection.send( ['result1', 'result2'] )
        print "done!"
        

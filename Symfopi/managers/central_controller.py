from multiprocessing import Process, Queue, Pipe
import collections
import time
import signal
from datetime import datetime as dt
import logging
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import threading
import json
import urlparse

from playback import PlaybackManager
from spotify_API import SpotifyAPIManager
from motion import MotionManager

        
class ThreadedHTTPServer( ThreadingMixIn, HTTPServer ):
    """Extension to BaseHTTPServer's HTTPServer with threaded connections,
    enabling asynchronous behaviour.
    
    Clearly, this enables usual race condition issues."""
    # Superb reference for Python's Base HTTP Server:
    #   http://www.doughellmann.com/PyMOTW/BaseHTTPServer/index.html#module-BaseHTTPServer
    # Also includes advice on automatic multi-threading.
    
    def __init__( self, server_addr, req_handler_class, central_controller,
                  controller_functions = {} ):
        """
        central_controller:
            the central controller object whose methods (functions) will be 
            called to fullfil HTTP requests
        controller_functions:
            indicates the controller functions that may be called, and
            the HTTP request method (GET, POST, etc.) from which they may
            be called. A dictionary where the key gives the HTTP request method
            and value is a list of function names.
        """
        HTTPServer.__init__( self, server_addr, req_handler_class )
        
        self.c_controller = central_controller
        self.c_funcs = controller_functions
        
    class HTTPRequestHandler( BaseHTTPRequestHandler ):
        """Class for objects representing a specific case of hanlding a 
        HTTP request. 
        Responds by calling the appropriate CentralController object's
        function, as specified by the request. First checks if the function
        being requested is permitted beforehand, using the HTTPServer's
        `c_funcs` dict."""
        
        def __init__( self, *oargs, **kwargs ):
            BaseHTTPRequestHandler.__init__( self, *oargs, **kwargs )
        
        def do_GET( self ):
            self.unified_handler( 'GET' )
        
        def do_POST( self ):
            self.unified_handler( 'POST' )
            
        def do_PUT( self ):
            self.unified_handler( 'PUT' )
        
        def unified_handler( self, http_req_method ):
            """Unified place to handle GET, POST, and PUT requests together."""
            
            # self.
            #    'client_address',
            #    'server',     the server object
            #    'command',
            #    'path',
            #    'request_version',
            #    'headers',
            #    'server_version',
            #    'sys_version',
            #    'error_message_format',
            #    'error_content_type',
            #    'protocol_version',
            #    'responses' 
            
            #
            # Parse the request
            req_url_endpath = self.path
            parse = urlparse.urlparse( req_url_endpath )
            # parse.scheme
            # parse.netloc
            # parse.path        path (/.../)
            # parse.params      params for last path element
            # parse.query       query component (?...)
            # parse.fragment
            
            path_str = parse.path
            query_str = parse.query 
            
            #
            # Parse and validate the path to get the function name
            if http_req_method not in self.server.c_funcs:
                # The acceptable methods dictionary did not mention
                # this type of HTTP request method
                print "no such path -- find approp HTTP code"
                return
            
            func_name = path_str.strip('/')
            
            acceptable_funcs = self.server.c_funcs[http_req_method]
            if not func_name in acceptable_funcs:
                print "function does not exist or not permitted -- find HTTP code"
                return 
            
            # func_name now deemed acceptable
            
            #
            # Prepare HTTP arguments for calling
            # Save as JSON
            json_args = []
            
            #
            # Function acceptable
            print "Function accepted"
            print "path:", path_str
            print "query:", query_str
            print "func name:", func_name
            getattr( self.server.c_controller, func_name )()
    

class CentralController( object ):
    """
    A central controller that handle the supporting managers.
    """
    
    def __init__( self ):
        """ """
        
    #
    #
    # Controller 
    #
    def start( self ):
        """ """
        
        #
        # Playback manager
        self.playback_manager = PlaybackManager()
        
        #
        # API manager
        self.api_manager = SpotifyAPIManager()
        
        #
        # Motion subprocess
        def motion_started_cb():
            print "Motion started"
            self.playback_manager.resume_playback()
        
        def motion_stopped_cb():
            print "Motion stopped"
            self.playback_manager.pause_playback()
        
        self.motion_manager = MotionManager( motion_started_cb, motion_stopped_cb )
                
        #
        # General set up 
        
        #
        # Manager set up
        #~self.motion_manager.enable_motion_monitor()
        
        #
        # HTTP server that represents the central controller API
        accepted_methods = {'GET':['get_current_playlist'], 
                            'POST':[], 
                            'PUT':['resume_playback',
                                   'pause_playback',
                                   'set_current_playlist', 
                                   'enable_motion_control', 
                                   'disable_motion_control' ], }
        httpd = ThreadedHTTPServer( ('',8000), ThreadedHTTPServer.HTTPRequestHandler, self,
                                    accepted_methods )
        # unconditional execution: httpd.serve_forever()

        global SIGTERM_SENT
        while not SIGTERM_SENT:
            httpd.handle_request()
        
        #
        # Finish up
        print "Safely stopping"
        self.stop()
    
    def stop( self ):
        print "Sending STOP instruction to managers"
        self.playback_manager.finish()
        self.api_manager.finish()
        self.motion_manager.finish()
        
        
if __name__ == '__main__':

    cc_daemon = CentralController()
    
    #
    # Rewire the signal handler
    global SIGTERM_SENT
    SIGTERM_SENT = False 
    def signal_handler_exit( sig, frame=None ):
        """Attempts a safe exit.
        """
        global SIGTERM_SENT
        SIGTERM_SENT = True
        #~ need to get working
    signal.signal( signal.SIGTERM, signal_handler_exit )
    
    #
    # Go go go
    cc_daemon.start()






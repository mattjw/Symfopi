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

from spotify.manager import SpotifySessionManager, SpotifyPlaylistManager, SpotifyContainerManager

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
    # Future:
    #   Consider refactor to replace homebrew code with some established 
    #   minimalist web framework for the HTTP server and API. E.g., CherryPy?
    
    def __init__( self, server_addr, req_handler_class, central_controller ):
        """
        central_controller:
            the central controller object whose methods (functions) will be 
            called to fullfil HTTP requests
        """
        HTTPServer.__init__( self, server_addr, req_handler_class )
        
        self.c_controller = central_controller
        self.registered_funcs = { 'GET':{}, 'PUT':{}, 'POST':{}  }  
    
    def register_api_function( self, pathname, func, http_method ):
        """Add a function that the server will respond to. 
        
        pathname: 
            matched to the URL path to indicate that the function should be
        called
        func: 
            function handle that will be called
        http_method: 
            the HTTP method that the function must be called with (e.g., GET)
        """
        if http_method not in self.registered_funcs:
            self.registered_funcs[http_method] = {}
        
        self.registered_funcs[http_method][pathname] = func
    
    class HTTPRequestHandler( BaseHTTPRequestHandler ):
        """Class for objects representing a specific case of hanlding a 
        HTTP request. 
        
        Responds by calling the appropriate CentralController object's
        function, as specified by the request. First checks if the function
        being requested is permitted beforehand, using the HTTPServer's
        `c_funcs` dict.
        
        == CONVENTIONS FOR 'DO' FUNCTIONS ==
        
        All HTTP query arguments are translated to a dictionary and passed on 
        to the "do_" function call as a single argument.
        
        A "do_" function is expected to return either a JSON-able object or
        None. If None, then the HTTP handler will return an empty payload
        (empty string).
        If not None, the object returned by the do function is translated to 
        JSON and returned.
        
        The do function is responsible for handling the HTTP arguments in the
        passed-in dictionary. The function should check for unexpected
        query arguments and raise an ArgumentError as appropriate.
        When such an error is encountered, the HTTP request handler
        will send back a 400 HTTP error and the error's message as the HTTP 
        payload.
        """
        
        def __init__( self, *oargs, **kwargs ):
            BaseHTTPRequestHandler.__init__( self, *oargs, **kwargs )
        
        def do_GET( self ):
            self.unified_handler( 'GET' )
        
        def do_POST( self ):
            self.unified_handler( 'POST' )
            
        def do_PUT( self ):
            self.unified_handler( 'PUT' )
        
        def unified_handler( self, http_req_method ):
            """Unified place to handle HTTP requests sent over various methods."""
            
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
            if http_req_method not in self.server.registered_funcs:
                # The acceptable methods dictionary did not mention
                # this type of HTTP request method
                print "no such HTTP request method"
                return
            
            func_name = path_str.strip('/')
            
            if not func_name in self.server.registered_funcs[http_req_method]:
                print "function does not exist or not permitted for the given HTTP method"
                return 
            
            func_handle = self.server.registered_funcs[http_req_method][func_name]
                        
            #
            # Prepare HTTP arguments for calling
            # Save as JSON
            qargs_dict = urlparse.parse_qs( query_str, keep_blank_values=True )
            
            #
            # Run the function and handle sending back the headers and response
            try:
                ret = func_handle( qargs_dict )
            except (ArgumentError,) as ex:
                errmsg = ex.message
                self.send_response( 400 )  # 400: bad request, do not retry w/o correction
                self.end_headers()
                self.wfile.write( errmsg )
            else:
                if ret is not None:
                    response_str = json.dumps( ret )
                else:
                    response_str = ""
            
                self.send_response( 200 )
                self.end_headers()
                self.wfile.write( response_str )
                
            
class ArgumentError( RuntimeError ):
    pass
    

class CentralController( object ):
    """
    A central controller that handles the supporting managers.
    """
    
    def __init__( self ):
        """ """
    
    #
    #
    # Top-level API functions
    #
    def do_set_playback_enabled( self, qargs_dict ):
        """ """
    
    def do_set_motion_control_enabled( self, qargs_dict ):
        #
        # Input handling
        if 'flag' not in qargs_dict:
            raise ArgumentError( "Missing argument: flag" )
        flag = qargs_dict.pop( 'flag' )[0]
        if qargs_dict:
            raise ArgumentError( "Unexpected arguments: " + ','.join(qargs_dict.keys())  )
            
        #
        # Do it
        if flag == 'true':
            self.motion_manager.enable_motion_monitor()
        elif flag == 'false':
            self.motion_manager.disable_motion_monitor()
        else:
            raise ArgumentError( "Cannot understand flag value '%s'" % flag )

    def do_next_track( self, qargs_dict ):
        """ """

    def do_get_current_playlist( self, qargs_dict ):
        """
        Expected args:
        * None
        
        Return data:
        { playlist_name, playlist_index }
        """
        assert len(qargs_dict) == 0
        ret = { 'playlist_name':'test_playlist', 'playlist_index': 33 }
        return ret 
    
    def do_set_current_playlist( self, qargs_dict ):
        """ """
        
        print "do -- set current playlist"
    
    #
    #
    # Controller 
    #
    def start( self ):
        """ """
        #
        # Credentials 
        spotify_username = "xyz"
    	spotify_password = "123"
        spotify_api_key = "sdsad323wd"
        
        #
        # Playback manager
        self.playback_manager = PlaybackManager( spotify_username, spotify_password, spotify_api_key )
        
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
        httpd = ThreadedHTTPServer( ('',8000), ThreadedHTTPServer.HTTPRequestHandler, self )
        
        httpd.register_api_function( 'get_current_playlist', 
                                     self.do_get_current_playlist,
                                     'GET' )

        httpd.register_api_function( 'set_playback_enabled', 
                                     self.do_set_playback_enabled,
                                     'PUT' )
                                  
        httpd.register_api_function( 'set_motion_control_enabled', 
                                     self.do_set_motion_control_enabled,
                                     'PUT' )
                                  
        httpd.register_api_function( 'next_track', 
                                     self.do_next_track,
                                     'PUT' )
                                  
        httpd.register_api_function( 'set_current_playlist', 
                                     self.do_set_current_playlist,
                                     'PUT' )
        
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






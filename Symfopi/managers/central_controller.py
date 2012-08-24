from multiprocessing import Process, Queue, Pipe
import collections
import time
import signal
from datetime import datetime as dt
import logging
from playback import PlaybackManager
from spotify_API import SpotifyAPIManager
from motion import MotionManager


class CentralController( object ):
    """
    A central controller that handle the supporting managers.
    """
    
    def __init__( self ):
        """
        """

    #
    #
    # SIGNAL HANDLING
    #
    def signal_exit( self, sig, frame=None ):
        """Attempts a safe exit.
        
        Instructions waiting in subprocess queues will be handled before
        stopping them. Instructions subsequent to the call to
        this method will not be handled. """
        
        print "Sending STOP instruction to managers"
        self.playback_manager.stop_process()
        self.api_manager.stop_process()
        self.motion_manager.stop_process()
        # Doing the above should allow `start()` to reach the 
        # join and finish up lines?
        
        #self.playback_manager.process.join()
        #print "playback manager stopped"
        
        #self.api_manager.process.join()
        #print "API manager stopped"
        
        #self.motion_manager.process.join()
        #print "Motion manager stopped"
        
        #exit(0)
    
    #
    #
    # Controller 
    #
    def start( self ):
        """
        """
        
        print "~START"
        
        #
        # Playback subprocess
        self.playback_manager = PlaybackManager()
        
        #
        # API subprocess
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
        
        print "~SUBPROCS"
        
        #
        # Start subprocs
        wrapper_f = lambda sig,frame: self.signal_exit( sig, frame )
        signal.signal( signal.SIGTERM, wrapper_f )  # process kill
        #  signal.signal( signal.SIGINT, wrapper_f )  # should not override
        # because interrupt comes from separate process. neeeds testing.
        # if a SIGINT is sent, the system automatically sends them all to the 
        # manager subprocesses. Thus, the manager subprocess also need
        # to have signal handlers?
        
        self.playback_manager.process.start()
        self.api_manager.process.start()
        self.motion_manager.process.start()
        
        #
        # Setup on running subprocs
        self.motion_manager.enable_motion_monitor()
        
        #
        # Testing
        print "~SUBPROCS DONE"
        
        #
        # Finish up
        self.playback_manager.process.join()
        self.api_manager.process.join()
        self.motion_manager.process.join()
    
        
if __name__ == '__main__':
    cc_daemon = CentralController()
    cc_daemon.start()






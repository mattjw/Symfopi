import collections
import time
import signal
from datetime import datetime as dt
import logging
import threading
import random 


class MotionMonitorMocker( threading.Thread ):
    """A mocker object for testing a motion monitor in the app.
    
    Also serves to demonstrate how the real motion monitor should act. 
    """
    
    def __init__( self, motion_started_callback, motion_stopped_callback ):
        threading.Thread.__init__( self )
        
        self.__motion_stopped_cb = motion_stopped_callback
        self.__motion_started_cb = motion_started_callback
        
        self.__stop_requested = False 
    
    def stop():
        self.__stop_requested = True 
    
    def run( self ):
        #~ Long sleep durations in thread mean long .join() waits for parent
        # caller after a stop request
        while not self.__stop_requested:
            # Period of motion
            play_dur = random.uniform( 10, 15 )
            self.__motion_started_cb()
            time.sleep( play_dur )
        
            # Period of no motion 
            stop_dur = random.uniform( 4, 8 )
            self.__motion_stopped_cb()
            time.sleep( stop_dur )


class MotionManager( object ):
    
    def __init__( self, motion_started_callback, motion_stopped_callback ):
        """
        Directly pauses or resume playback. 
        [Temporary design. A mocking object. Future: two callbacks given
        to the motion monitor thread. One call back for doing something
        when motion is sensed and another for when motion stops.]
        """
        super(MotionManager,self).__init__()
        self.__motion_monitor_thread = None
        self.__motion_started_cb = motion_started_callback
        self.__motion_stopped_cb = motion_stopped_callback

    def enable_motion_monitor( self ):
        """
        Enable motion monitoring.
        
        If monitoring is already enabled, it will be restarted.
        """
        # Disable if already running
        if self.__motion_monitor_thread is not None:
            self.disable_motion_monitor()
        
        # Enable
        assert self.__motion_monitor_thread is None
        self.__motion_monitor_thread = MotionMonitorMocker( self.__motion_started_cb, self.__motion_stopped_cb )
        self.__motion_monitor_thread.setDaemon( True )
        self.__motion_monitor_thread.start()
    
    def is_enabled( self ):
        """ """
        if self.__motion_monitor_thread is None:
            return False 
        else:
            if self.__motion_monitor_thread.isAlive():
                return True
            else:
                return False 
    
    def disable_motion_monitor( self ):
        """Disable motion monitoring.
        
        If monitoring is already disabled, no effect. Blocks until the motion
        monitor thread succesfully stops.
        """
        if self.__motion_monitor_thread is not None:
            self.__motion_monitor_thread.stop()
            self.__motion_monitor_thread.join()
            self.__motion_monitor_thread = None 
        
    def finish():
        """Finish and tidy up the manager."""
        self.disable_motion_manager()





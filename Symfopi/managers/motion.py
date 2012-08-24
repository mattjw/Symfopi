from multiprocessing import Process, Queue, Pipe
import collections
import time
import signal
from datetime import datetime as dt
import logging
import threading
import random 

from abstract_manager import AbstractManager


class MotionMonitorMocker( threading.Thread ):
    def __init__( self, motion_started_callback, motion_stopped_callback ):
        threading.Thread.__init__( self )
        
        self.__motion_stopped_cb = motion_stopped_callback
        self.__motion_started_cb = motion_started_callback
        
        self.__stop_requested = False 
    
    def stop():
        self.__stop_requested = True 
    
    def run( self ):
        print "~RUN?"
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


class MotionManager( AbstractManager ):
    
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
        self._parent_connection.send( ['_enable_motion_monitor'] )
        
    def _enable_motion_monitor( self ):
        # Disable if already running
        if self.__motion_monitor_thread is not None:
            self._disable_motion_monitor()
        
        # Enable
        assert self.__motion_monitor_thread is None
        self.__motion_monitor_thread = MotionMonitorMocker( self.__motion_started_cb, self.__motion_stopped_cb )
        self.__motion_monitor_thread.start()
    
    
    def is_enabled( self ):
        """
        """
        self._parent_connection.send( ['_is_enabled',] )
        ret = self._parent_connection.recv()  # blocks
        return ret
        
    def _is_enabled( self ):
        if self.__motion_monitor_thread is None:
            self._subproc_connection.send( False )  # return False
        else:
            if self.__motion_monitor_thread.isAlive():
                self._subproc_connection.send( True )  # return True
            else:
                self._subproc_connection.send( False )  # return True
    
        
    def disable_motion_monitor( self ):
        """Disable motion monitoring.
        
        If monitoring is already disabled, no effect.
        """
        self._parent_connection.send( ['_disable_motion_monitor'] )
    
    
    def _disable_motion_monitor( self ):
        if self.__motion_monitor_thread is not None:
            self.__motion_monitor_thread.stop()
            self.__motion_monitor_thread.join()
            self.__motion_monitor_thread = None 
        






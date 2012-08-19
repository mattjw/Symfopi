from multiprocessing import Process, Queue, Pipe
import collections
import time
import signal
from datetime import datetime as dt
import logging
import threading
import random 

from abstract_manager import AbstractManager


class PlaybackManager( AbstractManager ):
    """A manager for audio playback.
    """
    def __init__( self ):
        super(PlaybackManager,self).__init__()
        self._is_playing = False 
        self.__curr_pl_indx = None 
        
    def pause_playback( self ):
        """Pause music playback. No change if playback was already paused.
        
        Nonblocking:
        This method will add the instruction to the queue and then return. 
        The instruction may not have been handled by the time this method 
        returns. 
        """
        self._parent_connection.send( ['_pause_playback',] )
    
    def _pause_playback( self ):
        print "pause playback called"
        if not self._is_playing:
            print " > Already paused; no need to do anything."
        else:
            print " > Pausing playback."
            self._is_playing = False 


    def resume_playback( self ):
        """Initiate playback or resume playback from a paused state. 
        No change if playback is already occurring.
        
        Nonblocking:
        This method will add the instruction to the queue and then return. 
        The instruction may not have been handled by the time this method 
        returns. 
        """
        self._parent_connection.send( ['_resume_playback',] )

    def _resume_playback( self ):
        print "unpause playback called"
        if self._is_playing:
            print " > Playback already occurring. Do nothing."
        else:
            print " > Switching from paused to begin playback."
            
            pl_indx = self.__curr_pl_indx
            
            #~ play the playlist at pl_indx
            
            self._is_playing = True


    def set_current_playlist( self, playlist_index ):
        """Change the current playlist. If a song is currently being played,
        a song from the new playlist will be selected at random and played.
        
        Nonblocking:
        This method will add the instruction to the queue and then return. 
        The instruction may not have been handled by the time this method 
        returns. 
        """
        self._parent_connection.send( ['_set_current_playlist',playlist_index] )
        
    def _set_current_playlist( self, playlist_index ):
        print "set current playlist called"
        print "[set pl] halting for 0.5 seconds"
        time.sleep(0.5)
        print "[set pl] done"
        self.__curr_pl_indx = playlist_index 
        
        if self._is_playing:
            # if the manager is playing, then we need to restart it with the
            # new song
            self._pause_playback()
            self._resume_playback()
            
            


class SpotifyAPIManager( AbstractManager ):
    """A manager for retrieving information from the Spotify API.
    """
    def get_playlists_list( self ):
        """Return a list of the user's playlists.
        
        Blocking:
        This method will block until the internal subprocess has dispatched the
        underlying instruction and received its response.
        """
        self._parent_connection.send( ['_get_playlists_list',] )
        ret = self._parent_connection.recv()  # blocks
        return ret
    
    def _get_playlists_list( self ):        
        print "get PL called"
        print "[get PL list] halting for 5 seconds"
        time.sleep(5.0)
        print "[get PL list] done"
        
        pllist = ['playlist1','playlist2', 'playlist3',]
        
        self._subproc_connection.send( pllist )


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
        






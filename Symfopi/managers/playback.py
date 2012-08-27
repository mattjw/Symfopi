import collections
import time
import signal
from datetime import datetime as dt
import logging
import threading
import random 

from abstract_manager import AbstractManager


class PlaybackManager( object ):
    """A manager for audio playback.
    """
    def __init__( self ):
        self._is_playing = False 
        self.__curr_pl_indx = None 
        
    def pause_playback( self ):
        """Pause music playback. No change if playback was already paused.
        """
        print "pause playback called"
        if not self._is_playing:
            print " > Already paused; no need to do anything."
        else:
            print " > Pausing playback."
            self._is_playing = False 

    def resume_playback( self ):
        """Initiate playback or resume playback from a paused state. 
        No change if playback is already occurring.
        """
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
        """
        print "set current playlist called"
        print "[set pl] halting for 0.5 seconds"
        time.sleep(0.5)
        print "[set pl] done"
        self.__curr_pl_indx = playlist_index 
        
        if self._is_playing:
            # if the manager is playing, then we need to restart it with the
            # new song
            self.pause_playback()
            self.resume_playback()
    
    def finish():
        """Finish and tidy up the manager."""
        pass 
        # TO DO: stop the PySpotify session?
            





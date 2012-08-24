from multiprocessing import Process, Queue, Pipe
import collections
import time
import signal
from datetime import datetime as dt
import logging
import threading
import random 

from abstract_manager import AbstractManager


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

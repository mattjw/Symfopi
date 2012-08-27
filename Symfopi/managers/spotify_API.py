import collections
import time
import signal
from datetime import datetime as dt
import logging
import threading
import random 


class SpotifyAPIManager( object ):
    """A manager for retrieving information from the Spotify API.
    """
    def get_playlists_list( self ):
        """Return a list of the user's playlists.
        """
        print "get PL called"
        print "[get PL list] halting for 5 seconds"
        time.sleep(5.0)
        print "[get PL list] done"
        
        pllist = ['playlist1','playlist2', 'playlist3',]
        
        return pllist
        
    def finish():
        """Finish and tidy up the manager."""
        pass 
        # TO DO: stop the PySpotify session?
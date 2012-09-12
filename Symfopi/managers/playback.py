import collections
import time
import signal
from datetime import datetime as dt
import logging
import threading
import random 

from abstract_manager import AbstractManager

from spotify import ArtistBrowser, Link, ToplistBrowser
from spotify.audiosink import import_audio_sink
from spotify.manager import SpotifySessionManager, SpotifyPlaylistManager, \
    SpotifyContainerManager
    

class PlaybackManager( object ):
    """A manager for audio playback.
    """
    def __init__( self, username, password, api_key ):
        self._is_playing = False 
        self.__curr_pl_indx = None 
        
        self.sp_username = username
        self.sp_password = password
        self.sp_api_key = api_key 
        
        self.jukebox = SpotifyJukebox( username=username, password=password, remember_me=True, application_key=api_key )
        
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
            

#
# 

class SpotifyJukebox(SpotifySessionManager):
    """
    Adapted from the Jukebox example program in PySpotifyLib.
    """

    queued = False
    playlist = 2
    track = 0
    appkey_file = os.path.join(os.path.dirname(__file__), 'spotify_appkey.key')

    def __init__(self, *a, **kw):
        #
        # Prevent the Spotify Session Manager from trying to read the appkey from file 
        self.appkey_file = None
        self.application_key = kw['application_key']
        
        #
        # Parent constructor
        SpotifySessionManager.__init__(self, *a, **kw)
        
        #
        # Standard set up
        self.audio = AudioSink(backend=self)
        # MJW self.ui = JukeboxUI(self)
        self.ctr = None
        self.playing = False
        self._queue = []
        self.playlist_manager = JukeboxPlaylistManager()
        self.container_manager = JukeboxContainerManager()
        self.track_playing = None
        print "Logging in, please wait..."

    def new_track_playing(self, track):
        self.track_playing = track
    
    #
    # Overridden SpotifySessionManager callbacks.
    
    def logged_in(self, session, error):
        """Callback. Called when the login completes."""
        if error:
            print error
            return
        self.session = session
        self.ctr = session.playlist_container()
        self.container_manager.watch(self.ctr)
        self.starred = session.starred()
        # MJW self.ui.start()

    def logged_out(self, session):
        """Callback. The user has or has been logged out from Spotify."""
        #MJW self.ui.cmdqueue.append("quit")
        
    def end_of_track(self, sess):
        """Callback. Playback has reached the end of the current track."""
        self.audio.end_of_track()

    #
    # Other SpotifySessionManager overrides.

    def music_delivery_safe(self, *args, **kwargs):
        """Overrides parent method."""
        return self.audio.music_delivery(*args, **kwargs)

    #
    # Other jukebox methods.
    
    def load_track(self, track):
        if self.playing:
            self.stop()
        self.new_track_playing(track)
        self.session.load(track)  # loads the specified track on the player
        print "Loading %s" % track.name()

    def load(self, playlist, track):
        if self.playing:
            self.stop()
        if 0 <= playlist < len(self.ctr):
            pl = self.ctr[playlist]
        elif playlist == len(self.ctr):
            pl = self.starred
        spot_track = pl[track]
        self.new_track_playing(spot_track)
        self.session.load(spot_track)
        print "Loading %s from %s" % (spot_track.name(), pl.name())

    def load_playlist(self, playlist):
        if self.playing:
            self.stop()
        if 0 <= playlist < len(self.ctr):
            pl = self.ctr[playlist]
        elif playlist == len(self.ctr):
            pl = self.starred
        print "Loading playlist %s" % pl.name()
        if len(pl):
            print "Loading %s from %s" % (pl[0].name(), pl.name())
            self.new_track_playing(pl[0])
            self.session.load(pl[0])
        for i, track in enumerate(pl):
            if i == 0:
                continue
            self._queue.append((playlist, i))

    def queue(self, playlist, track):
        if self.playing:
            self._queue.append((playlist, track))
        else:
            print 'Loading %s', track.name()
            self.load(playlist, track)
            self.play()

    def play(self):
        self.audio.start()
        self.session.play(1)  # pause playback if '0', otherwise play
        print "Playing"
        self.playing = True

    def stop(self):
        self.session.play(0)
        print "Stopping"
        self.playing = False
        self.audio.stop()

    def next(self):
        self.stop()
        if self._queue:
            t = self._queue.pop(0)
            self.load(*t)
            self.play()
        else:
            self.stop()

    def search(self, *args, **kwargs):
        self.session.search(*args, **kwargs)  # returns a Results class

    def browse(self, link, callback):
        if link.type() == link.LINK_ALBUM:
            browser = self.session.browse_album(link.as_album(), callback)  # browse an album. Once metadata loaded, the callback is called
            while not browser.is_loaded():
                time.sleep(0.1)
            for track in browser:
                print track.name()
        if link.type() == link.LINK_ARTIST:
            browser = ArtistBrowser(link.as_artist())
            while not browser.is_loaded():
                time.sleep(0.1)
            for album in browser:
                print album.name()

    def watch(self, p, unwatch=False):
        if not unwatch:
            print "Watching playlist: %s" % p.name()
            self.playlist_manager.watch(p)
        else:
            print "Unatching playlist: %s" % p.name()
            self.playlist_manager.unwatch(p)

    def toplist(self, tl_type, tl_region):
        print repr(tl_type)
        print repr(tl_region)
        def callback(tb, ud):
            for i in xrange(len(tb)):
                print '%3d: %s' % (i+1, tb[i].name())

        tb = ToplistBrowser(tl_type, tl_region, callback)

    def shell(self):
        import code
        shell = code.InteractiveConsole(globals())
        shell.interact()
    

    ## playlist callbacks ##
    class JukeboxPlaylistManager(SpotifyPlaylistManager):
        def tracks_added(self, p, t, i, u):
            print 'Tracks added to playlist %s' % p.name()

        def tracks_moved(self, p, t, i, u):
            print 'Tracks moved in playlist %s' % p.name()

        def tracks_removed(self, p, t, u):
            print 'Tracks removed from playlist %s' % p.name()


    ## container calllbacks ##
    class JukeboxContainerManager(SpotifyContainerManager):
        def container_loaded(self, c, u):
            container_loaded.set()

        def playlist_added(self, c, p, i, u):
            print 'Container: playlist "%s" added.' % p.name()

        def playlist_moved(self, c, p, oi, ni, u):
            print 'Container: playlist "%s" moved.' % p.name()

        def playlist_removed(self, c, p, i, u):
            print 'Container: playlist "%s" removed.' % p.name()



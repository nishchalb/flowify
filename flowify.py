import spotipy

def get_playlists(sp):
    """ Get the current user's playlists
    
    Args:
        sp (spotipy.client.Spotify): A spotipy client with an auth token

    Returns:
        list: A list containing spotify playlist objects represented as dicts
    """
    user = sp.current_user()
    playlists = []
    s_playlists = sp.user_playlists(user['id'])

    while s_playlists['next']:
        for playlist in s_playlists['items']:
            if (not playlist['collaborative']) and playlist['owner']['id'] == user['id']:
                playlists.append(playlist)
        s_playlists = sp.next(s_playlists)

    return playlists

def get_tracks_from_playlist(sp, playlist):
    """ Get a list of the tracks in a given playlist

    Args:
        sp (spotipy.client.Spotify): A spotipy client with an auth token
        playlist (dict): A dictionary representing a spotify playlist

    Returns:
        list: A list containing spotify track objects represented as dicts
    """
    user = sp.current_user()
    results = sp.user_playlist(user['id'], playlist['id'], fields='tracks,next')
    s_tracks = results['tracks']
    tracks = []

    while True:
        for track in s_tracks['items']:
            tracks.append(track['track'])
        if not s_tracks['next']:
            break
        s_tracks = sp.next(s_tracks)

    return tracks

def feature_vector_from_track(sp, track):
    audio_features = sp.audio_features([track['id']])


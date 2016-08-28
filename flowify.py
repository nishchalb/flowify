import spotipy
import peewee

db = peewee.SqliteDatabase('audio_features.db')

class Track(peewee.Model):
    track_id = peewee.CharField(primary_key=True)
    acousticness = peewee.FloatField()
    danceability = peewee.FloatField()
    energy = peewee.FloatField()
    instrumentalness = peewee.FloatField()
    key = peewee.IntegerField()
    liveness = peewee.FloatField()
    loudness = peewee.FloatField()
    mode = peewee.IntegerField()
    speechiness = peewee.FloatField()
    tempo = peewee.FloatField()
    time_signature = peewee.IntegerField()
    valence = peewee.FloatField()

    class Meta:
        database = db

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
    """ Construct a feature vector from a given track

    Args:
        sp (spotipy.client.Spotify): A spotipy client with an auth token
        track (dict): A dictionary representing a spotify track object

    Returns:
        list: A list representing a feature vector for the given track
    """
    # First check if the features for this track are already stored
    if Track.select().where(Track.track_id == track['id']).count() > 0:
        track_features = Track.get(Track.track_id == track['id'])
    else:
        # Get result and add to database
        audio_features = sp.audio_features([track['id']])[0]
        track_features = Track.create(
                track_id = audio_features['id'],
                acousticness = audio_features['acousticness'],
                danceability = audio_features['danceability'],
                energy = audio_features['energy'],
                instrumentalness = audio_features['instrumentalness'],
                key = audio_features['key'],
                liveness = audio_features['liveness'],
                loudness = audio_features['loudness'],
                mode = audio_features['mode'],
                speechiness = audio_features['speechiness'],
                tempo = audio_features['tempo'],
                time_signature = audio_features['time_signature'],
                valence = audio_features['valence'])
    # Now construct vector
    vector = []
    vector.append(track['artists'][0]['id'])
    vector.append(track_features.acousticness)
    vector.append(track_features.danceability)
    vector.append(track_features.energy)
    vector.append(track_features.instrumentalness)
    vector.append(track_features.key)
    vector.append(track_features.liveness)
    vector.append(track_features.loudness)
    vector.append(track_features.mode)
    vector.append(track_features.speechiness)
    vector.append(track_features.tempo)
    vector.append(track_features.time_signature)
    vector.append(track_features.valence)

    return vector


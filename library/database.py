import enum
import os.path
import datetime
import flask_sqlalchemy


db = flask_sqlalchemy.SQLAlchemy()


class Track(db.Model):
    __bind_key__ = 'library'
    __tablename__ = 'track'

    # The ID of the track
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # The location of the file
    location = db.Column(db.String, nullable=False)
    # The artist of the track
    artist = db.Column(db.String)
    # The title of the track
    title = db.Column(db.String)
    # The length of the track in seconds
    length = db.Column(db.Float)


class TrackPlay(db.Model):
    __bind_key__ = 'library'
    __tablename__ = 'track_play'

    # The ID of the track
    track = db.Column(db.Integer, db.ForeignKey('track.id'), primary_key=True)
    # The time and date it was played
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class TrackTags(db.Model):
    __bind_key__ = 'library'
    __tablename__ = 'track_tags'

    # The ID of the track
    track = db.Column(db.Integer, db.ForeignKey('track.id'), primary_key=True)
    # The tag to assign to the track
    tag = db.Column(db.String, primary_key=True)


class Library(db.Model):
    __bind_key__ = 'library'
    __tablename__ = 'library'

    # The ID of this base directory
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # A base directory for the library
    location = db.Column(db.String, nullable=False)


class Playlist(db.Model):
    __bind_key__ = 'library'
    __tablename__ = 'playlist'

    # The ID of the playlist
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # The name of the playlist
    name = db.Column(db.String, nullable=False)


class PlaylistTrack(db.Model):
    __bind_key__ = 'library'
    __tablename__ = 'playlist_track'

    # The playlist that this track is in
    playlist = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False, primary_key=True)
    # The track entry for the playlist
    track = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=False)
    # The index in the playlist of the track to change the order
    index = db.Column(db.Integer, nullable=False, primary_key=True)


class LivePlayerState(enum.Enum):
    # The player is currently playing a track
    playing = 0
    # The player is paused
    paused = 1


class LivePlayer(db.Model):
    __bind_key__ = 'library'
    __tablename__ = 'live_player'

    # The ID of the playlist
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # The name of the playlist
    name = db.Column(db.String, nullable=False)
    # The state of the playlist
    state = db.Column(db.Enum(LivePlayerState), nullable=False)
    # The playlist that contains the jingles
    jingle_playlist = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=True)
    # The number of tracks to play before playing a jingle
    jingle_count = db.Column(db.Integer, nullable=True)
    # The number of tracks played since the last jingle
    jingle_plays = db.Column(db.Integer, nullable=False)


class LivePlayerType(enum.Enum):
    # After this track finishes move to the next
    play_next = 0
    # After this track finishes pause until someone starts again
    pause_after = 1
    # Continue playing this track until someone moves it on
    loop = 2


class LivePlayerTrack(db.Model):
    __bind_key__ = 'library'
    __tablename__ = 'live_player_track'

    # The playlist that this track is in
    playlist = db.Column(db.Integer, db.ForeignKey('live_player.id'), nullable=False, primary_key=True)
    # The track entry for the playlist
    track = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=False)
    # The index in the playlist of the track to change the order
    index = db.Column(db.Integer, nullable=False, primary_key=True)
    # The type of the entry
    type = db.Column(db.Enum(LivePlayerType), nullable=False)


def init_app(app):
    """
    Configure the database for the given Flask application
    :param app:  The Flask application to configure for
    """
    binds = app.config.get('SQLALCHEMY_BINDS', {})
    binds['library'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'library.db')
    app.config['SQLALCHEMY_BINDS'] = binds
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    db.create_all(bind='library', app=app)

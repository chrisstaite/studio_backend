import enum
import os.path
import datetime
import sqlalchemy.ext.declarative
import sqlalchemy.orm

# The base type for all of the tables
Base = sqlalchemy.ext.declarative.declarative_base()


class Track(Base):
    __tablename__ = 'track'

    # The ID of the track
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    # The location of the file
    location = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # The artist of the track
    artist = sqlalchemy.Column(sqlalchemy.String)
    # The title of the track
    title = sqlalchemy.Column(sqlalchemy.String)
    # The length of the track in seconds
    length = sqlalchemy.Column(sqlalchemy.Float)


class TrackPlay(Base):
    __tablename__ = 'track_play'

    # The ID of the track
    track = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('track.id'), primary_key=True)
    # The time and date it was played
    time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)


class TrackTags(Base):
    __tablename__ = 'track_tags'

    # The ID of the track
    track = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('track.id'), primary_key=True)
    # The tag to assign to the track
    tag = sqlalchemy.Column(sqlalchemy.String, primary_key=True)


class Library(Base):
    __tablename__ = 'library'

    # The ID of this base directory
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    # A base directory for the library
    location = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class Playlist(Base):
    __tablename__ = 'playlist'

    # The ID of the playlist
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    # The name of the playlist
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class PlaylistTrack(Base):
    __tablename__ = 'playlist_track'

    # The playlist that this track is in
    playlist = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('playlist.id'), nullable=False, primary_key=True
    )
    # The track entry for the playlist
    track = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('track.id'), nullable=False)
    # The index in the playlist of the track to change the order
    index = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True)


class LivePlayerState(enum.Enum):
    # The player is currently playing a track
    playing = 0
    # The player is paused
    paused = 1


class LivePlayer(Base):
    __tablename__ = 'live_player'

    # The ID of the playlist
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    # The name of the playlist
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # The state of the playlist
    state = sqlalchemy.Column(sqlalchemy.Enum(LivePlayerState), nullable=False)
    # The playlist that contains the jingles
    jingle_playlist = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('playlist.id'), nullable=True)
    # The number of tracks to play before playing a jingle
    jingle_count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    # The number of tracks played since the last jingle
    jingle_plays = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


class LivePlayerType(enum.Enum):
    # After this track finishes move to the next
    play_next = 0
    # After this track finishes pause until someone starts again
    pause_after = 1
    # Continue playing this track until someone moves it on
    loop = 2


class LivePlayerTrack(Base):
    __tablename__ = 'live_player_track'

    # The playlist that this track is in
    playlist = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('live_player.id'), nullable=False, primary_key=True
    )
    # The track entry for the playlist
    track = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('track.id'), nullable=False)
    # The index in the playlist of the track to change the order
    index = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True)
    # The type of the entry
    type = sqlalchemy.Column(sqlalchemy.Enum(LivePlayerType), nullable=False)


engine = sqlalchemy.create_engine('sqlite:///' + os.path.join(os.path.dirname(__file__), 'library.db'))
Base.metadata.create_all(engine)
Session = sqlalchemy.orm.sessionmaker(bind=engine)

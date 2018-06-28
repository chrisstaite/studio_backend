import os.path
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
    artist = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # The title of the track
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)


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
    track = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('track.id'), nullable=False, primary_key=True)
    # The index in the playlist of the track to change the order
    index = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


engine = sqlalchemy.create_engine('sqlite:///' + os.path.join(os.path.dirname(__file__), 'library.db'))
Base.metadata.create_all(engine)
Session = sqlalchemy.orm.sessionmaker(bind=engine)

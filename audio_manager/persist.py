import flask_sqlalchemy
import os.path
import enum


db = flask_sqlalchemy.SQLAlchemy()


class InputTypes(enum.Enum):
    device = 0


class Input(db.Model):
    __bind_key__ = 'audio_manager'
    __tablename__ = 'input'

    # The UUID of the Input
    id = db.Column(db.String, primary_key=True, nullable=False)
    # The name of the Input
    display_name = db.Column(db.String, nullable=False)
    # The type of the input
    type = db.Column(db.Enum(InputTypes), nullable=False)
    # The parameters to construct that type
    parameters = db.Column(db.String, nullable=False)


class OutputTypes(enum.Enum):
    device = 0
    icecast = 1
    multiplex = 2
    file = 3


class Output(db.Model):
    __bind_key__ = 'audio_manager'
    __tablename__ = 'output'

    # The UUID of the Output
    id = db.Column(db.String, primary_key=True, nullable=False)
    # The name of the Output
    display_name = db.Column(db.String, nullable=False)
    # The UUID of the source of this channel
    input = db.Column(db.String, nullable=True)
    # The type of the output
    type = db.Column(db.Enum(OutputTypes), nullable=False)
    # The parameters to construct that type
    parameters = db.Column(db.String, nullable=False)


class Mixer(db.Model):
    __bind_key__ = 'audio_manager'
    __tablename__ = 'mixer'

    # The UUID of the mixer
    id = db.Column(db.String, primary_key=True, nullable=False)
    # The name of the mixer
    display_name = db.Column(db.String, nullable=False)
    # The number of output channels
    output_channels = db.Column(db.Integer, nullable=False)


class MixerChannel(db.Model):
    __bind_key__ = 'audio_manager'
    __tablename__ = 'mixer_channel'

    # The UUID of the mixer channel
    id = db.Column(db.String, primary_key=True, nullable=False)
    # The UUID of the mixer this channel is for
    mixer = db.Column(db.String, nullable=False)
    # The UUID of the source of this channel
    input = db.Column(db.String, nullable=False)
    # The volume of this channel
    volume = db.Column(db.Float, nullable=False)


def init_app(app):
    """
    Configure the database for the given Flask application
    :param app:  The Flask application to configure for
    """
    binds = app.config.get('SQLALCHEMY_BINDS', {})
    binds['audio_manager'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'state.db')
    app.config['SQLALCHEMY_BINDS'] = binds
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    db.create_all(bind='audio_manager', app=app)

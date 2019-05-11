import sqlalchemy.ext.declarative
import sqlalchemy.orm
import os.path
import enum

# The base type for all of the tables
Base = sqlalchemy.ext.declarative.declarative_base()


class InputTypes(enum.Enum):
    device = 0


class Input(Base):
    __tablename__ = 'input'

    # The UUID of the Input
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, nullable=False)
    # The name of the Input
    display_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # The type of the input
    type = sqlalchemy.Column(sqlalchemy.Enum(InputTypes), nullable=False)
    # The parameters to construct that type
    parameters = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class OutputTypes(enum.Enum):
    device = 0
    icecast = 1
    multiplex = 2
    file = 3


class Output(Base):
    __tablename__ = 'output'

    # The UUID of the Output
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, nullable=False)
    # The name of the Output
    display_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # The UUID of the source of this channel
    input = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # The type of the output
    type = sqlalchemy.Column(sqlalchemy.Enum(OutputTypes), nullable=False)
    # The parameters to construct that type
    parameters = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class Mixer(Base):
    __tablename__ = 'mixer'

    # The UUID of the mixer
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, nullable=False)
    # The name of the mixer
    display_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # The number of output channels
    output_channels = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


class MixerChannel(Base):
    __tablename__ = 'mixer_channel'

    # The UUID of the mixer channel
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, nullable=False)
    # The UUID of the mixer this channel is for
    mixer = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # The UUID of the source of this channel
    input = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # The volume of this channel
    volume = sqlalchemy.Column(sqlalchemy.Float, nullable=False)


engine = sqlalchemy.create_engine('sqlite:///' + os.path.join(os.path.dirname(__file__), 'state.db'))
Base.metadata.create_all(engine)
Session = sqlalchemy.orm.sessionmaker(bind=engine)

from . import output
from . import input
from . import mixer
from . import live_player
from . import exception
from . import persist


def init_app(app):
    """
    Configure the database for the given Flask application and then
    restore all of the data from the database
    :param app:  The Flask application to configure for
    """
    persist.init_app(app)
    input.Inputs.restore()
    live_player.LivePlayers.restore()
    output.Outputs.restore()
    mixer.Mixers.restore()
    output.Outputs.restore_inputs()

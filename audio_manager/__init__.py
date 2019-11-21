from . import output
from . import input
from . import mixer
from . import live_player
from . import exception


def _restore():
    input.Inputs.restore()
    live_player.LivePlayers.restore()
    output.Outputs.restore()
    mixer.Mixers.restore()
    output.Outputs.restore_inputs()


_restore()

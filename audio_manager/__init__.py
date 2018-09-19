from . import output
from . import input
from . import mixer
from . import exception


def _restore():
    input.Inputs.restore()
    output.Outputs.restore()
    mixer.Mixers.restore()
    output.Outputs.restore_inputs()


_restore()

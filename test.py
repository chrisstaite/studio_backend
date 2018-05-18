import time
import audio.file
import audio.output_device
import audio.input_device
import audio.mixer

block_size = 1024
speaker = audio.output_device.OutputDevice('Built-in Output', block_size)
file = audio.file.File(
    '/Users/chris/Music/iTunes/iTunes Media/Music/Men at Work/The Best of Eighties/23 Down Under.mp3',
    block_size,
    speaker
)
mic = audio.input_device.InputDevice('Built-in Microphone', block_size)
mixer = audio.mixer.Mixer(block_size, 2)
mixer.add_input(file)
mixer.set_volume(file, 0.1)
mixer.add_input(mic)
mixer.set_volume(mic, 1.0)
with speaker, mic:
    speaker.set_input(mixer)
    file.play()
    try:
        while True:
            time.sleep(1)
    finally:
        file.stop()
        mixer.remove_input(file)
        speaker.set_input(None)

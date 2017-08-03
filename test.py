import time
import audio.input_device
import audio.output_device
import audio.meter

mic = audio.input_device.InputDevice('Built-in Microphone', 1024)
speaker = audio.output_device.OutputDevice('Built-in Output', 1024)
with mic:
    with speaker:
        speaker.set_input(mic)
        meter = audio.meter.Meter()
        meter.set_source(mic)
        try:
            while True:
                print(meter.current_level())
                time.sleep(0.1)
        finally:
            meter.set_source(None)
            speaker.set_input(None)

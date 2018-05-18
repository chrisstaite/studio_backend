import flask_restful
import audio


class OutputDevice(flask_restful.Resource):

    def get(self):
        return audio.output_device.OutputDevice.devices()

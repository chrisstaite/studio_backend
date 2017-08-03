
class Input(object):

    def __init__(self):
        self._callbacks = []

    def add_callback(self, callback):
        """
        Add a callback to this input device
        :param callback:  The callback to add
        """
        self._callbacks.append(callback)

    def remove_callback(self, callback):
        """
        Remove a callback from this input device
        :param callback:  The callback to remove
        """
        self._callbacks.remove(callback)

    def notify_callbacks(self, blocks):
        """
        Notify the callbacks that are registered of a new input block
        :param blocks:  The blocks to notify the callback with
        """
        for callback in self._callbacks:
            callback(self, blocks)

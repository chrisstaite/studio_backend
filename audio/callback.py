
class Callback(object):
    """
    The basic super class to manage callbacks
    """

    def __init__(self):
        """
        Initialise the input with no callbacks
        """
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

    def notify_callbacks(self, *args, **kwargs):
        """
        Notify the callbacks that are registered of a new input block
        """
        for callback in self._callbacks:
            callback(self, *args, **kwargs)

    def has_callbacks(self):
        """
        Whether there are currently any callbacks for this instance
        :return:  True if there are callbacks, False if not
        """
        return len(self._callbacks) > 0

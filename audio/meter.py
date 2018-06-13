import numpy


class Meter(object):
    """
    A sound meter that uses listens to an input and determines the peaks
    """

    def __init__(self):
        """
        Create a peak meter for a given source
        """
        self._peaks = [0] * 100
        self._current_peak = 0
        self._source = None

    @property
    def input(self):
        return self._source

    @input.setter
    def input(self, source) -> None:
        """
        Set the current source of the meter
        :param source:  The source or None to clear the source
        """
        if self._source == source:
            return
        if self._source is not None:
            self._source.remove_callback(self._callback)
        self._source = source
        if self._source is not None:
            self._source.add_callback(self._callback)

    def current_level(self) -> int:
        """
        Get the peak of the last block that was processed
        :return:  The current level
        """
        return self._peaks[self._current_peak]

    def current_peak(self) -> int:
        """
        Get the maximum peak that is in the current list
        :return:  The maximum peak
        """
        return max(self._peaks)

    def _callback(self, _, blocks: numpy.array) -> None:
        """
        Process a block from the source
        :param blocks:  The block to get the peak for
        """
        peak = numpy.average(numpy.abs(blocks)) * 2
        next_peak = (self._current_peak + 1) % len(self._peaks)
        self._peaks[next_peak] = peak
        self._current_peak = next_peak

from abc import ABC, abstractmethod


class AreaSelector(ABC):

    @abstractmethod
    def select_area(self, ds):
        """
        Select a given area from the global dataset.

        The specific implementaiton of the method depends on the
        type of the area selector.

        Arguments
        ---------
        ds : xr.Dataset with global data

        Returns
        -------
        xr.Dataset : Dataset with only the selected region
        """

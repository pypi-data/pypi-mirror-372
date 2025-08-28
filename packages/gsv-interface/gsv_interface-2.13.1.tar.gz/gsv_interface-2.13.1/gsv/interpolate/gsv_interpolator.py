import smmregrid

from gsv.exceptions import MissingSourceGridError
from gsv.interpolate.weights import get_weights, get_weights_name


class GSVInterpolator:

    def __init__(self, output_grid, method="nn", logger=None):
        self.output_grid = output_grid
        self.interpolation_method = method
        self.logger = logger
        self.input_grid = None
        self.weights = {}

    def set_input_grid(self, input_grid):
        """
        Add docstrings
        """
        self.input_grid = input_grid

    def interpolate(self, da):
        """
        Add docstrings
        """
        if self.input_grid is None:
            raise MissingSourceGridError()

        weights_name = get_weights_name(
            da, self.input_grid, self.output_grid,
            self.interpolation_method
        )

        if weights_name not in self.weights:
            weights = get_weights(
                da, self.input_grid, self.output_grid,
                self.interpolation_method, self.logger
            )
            self.weights[weights_name] = weights

        da = smmregrid.regrid(da, weights=self.weights[weights_name])
        return da

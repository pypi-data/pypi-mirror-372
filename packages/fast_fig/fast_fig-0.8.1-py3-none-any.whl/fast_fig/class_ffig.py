"""FFig simplifies handling of matplotlib figures.

Key features:
- Predefined templates for consistent styling
- Figure instantiation in a class object
- Simplified plotting methods with smart defaults
- Automatic handling of DataFrames
- Context manager support for clean resource management

Basic usage:
```python
from fast_fig import FFig
fig = FFig()  # Create figure with default medium template
fig.plot([1, 2, 3])  # Simple plotting
fig.show()  # Display figure
```

Advanced usage:
```python
with FFig("l", nrows=2, sharex=True) as fig:  # Large template, 2 rows sharing x-axis
    fig.plot([1, 2, 3], label="First")  # Plot in first axis/subplot
    fig.title("First plot")
    fig.next_axis()  # Switch to second axis/subplot
    fig.plot([0, 1, 2], [0, 1, 4], label="Second")  # Plot with x,y data
    fig.legend()  # Add legend
    fig.grid()  # Add grid
    fig.xlabel("X values")  # Label x-axis
    fig.save("plot.png", "pdf")  # Save as PNG and PDF
```

The following handlers provide direct access to matplotlib functionality:
- fig.current_axis: Current axes instance
- fig.handle_plot: Current plot instance
- fig.handle_axis: All axes instances
- fig.handle_fig: Figure instance

@author: fstutzki
"""

from __future__ import annotations

# %%
__author__ = "Fabian Stutzki"
__email__ = "fast@fast-apps.de"


import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from packaging import version

if TYPE_CHECKING:
    from types import TracebackType

    import pandas as pd
    from matplotlib.lines import Line2D


from typing_extensions import Self

from . import presets

MAT_EXAMPLE = np.array([[1, 2, 3, 4, 5, 6, 7], np.random.randn(7), 2 * np.random.randn(7)])  # noqa: NPY002


# %%
class FFig:
    """FFig simplifies handling of matplotlib figures.

    Use as
    from fast_fig import FFig
    fig = FFig('m')
    fig.plot([0,1,2,3,4],[0,1,1,2,3])
    fig.save('test.png')

    Can also be used as a context manager:
    with FFig() as fig:
        fig.plot(data)
        fig.save('plot.png')
    # Figure automatically closed

    @author: fstutzki
    """

    def __enter__(self) -> Self:
        """Enter the context manager.

        Returns
        -------
        FFig
            The figure instance

        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager and close the figure.

        Parameters
        ----------
        exc_type : type[BaseException] | None
            The type of the exception that was raised
        exc_val : BaseException | None
            The instance of the exception that was raised
        exc_tb : TracebackType | None
            The traceback of the exception that was raised

        """
        self.close()

    def __init__(
        self: FFig,
        template: str = "m",
        nrows: int = 1,
        ncols: int = 1,
        **kwargs: int | str | bool | dict[str, Any] | None,
    ) -> None:
        """Initialize a new FFig instance.

        Parameters
        ----------
        template : str, optional
            Template name defining figure style, by default "m".
            Available templates: "m" (medium), "s" (small), "l" (large),
            "ol" (one-line), "oe" (one-equation), "square"
        nrows : int, optional
            Number of subplot rows, by default 1
        ncols : int, optional
            Number of subplot columns, by default 1
        **kwargs : int | str | bool | dict | None
            Additional keyword arguments:
            - isubplot : int
                Initial subplot index, by default 0
            - sharex : bool
                Share x-axis between subplots, by default False
            - sharey : bool
                Share y-axis between subplots, by default False
            - show : bool
                Show figure after saving, by default True
            - wspace : float | None
                Vertical space between subplots, by default None
            - hspace : float | None
                Horizontal space between subplots, by default None
            - presets : dict | str | Path | None
                Custom presets dictionary or path to JSON file, by default None
            - width : float
                Figure width in cm (from template or preset)
            - height : float
                Figure height in cm (from template or preset)
            - fontfamily : str
                Font family name (from template or preset)
            - fontsize : int
                Font size in points (from template or preset)
            - linewidth : float
                Line width in points (from template or preset)

        Example
        -------
        >>> fig = FFig()  # Default medium template
        >>> fig = FFig("l", nrows=2, sharex=True)  # Large template, 2 rows sharing x-axis
        >>> fig = FFig("s", presets="my_presets.json")  # Small template with custom presets

        """
        # Enable logger
        self.logger = logging.getLogger(self.__class__.__name__)

        kwargs.setdefault("isubplot", 0)
        kwargs.setdefault("sharex", False)
        kwargs.setdefault("sharey", False)
        kwargs.setdefault("show", True)
        kwargs.setdefault("wspace", None)
        kwargs.setdefault("hspace", None)
        kwargs.setdefault("presets", None)

        # Initialize dictionary with presets
        self.presets = presets.define_presets(kwargs["presets"])

        # Check if template exists (ignoring case), otherwise set template m (default)
        template = template.lower()
        if template not in self.presets:
            template = "m"

        # Fill undefined kwargs with presets
        for key in ["width", "height", "fontfamily", "fontsize", "linewidth"]:
            kwargs.setdefault(key, self.presets[template][key])

        # Apply parameters to matplotlib
        mpl.rc("font", size=kwargs["fontsize"])
        mpl.rc("font", family=kwargs["fontfamily"])
        mpl.rc("lines", linewidth=kwargs["linewidth"])

        # Convert colors to ndarray and scale to 1 instead of 255
        self.colors = {}
        for iname, icolor in self.presets["colors"].items():
            if np.max(icolor) > 1:
                self.colors[iname] = np.array(icolor) / 255

        # Define cycle with colors, color_seq and linestyle_seq
        self.set_cycle(self.colors, self.presets["color_seq"], self.presets["linestyle_seq"])

        # Store global variables
        self.figure_show = kwargs["show"]  # show figure after saving
        self.subplot_index = 0
        self.handle_bar = None
        self.handle_plot = None
        self.handle_surface = None
        self.linewidth = kwargs["linewidth"]

        # Create figure
        self.handle_fig = plt.figure()
        self.handle_fig.set_size_inches(kwargs["width"] / 2.54, kwargs["height"] / 2.54)
        self.subplot(
            nrows=nrows,
            ncols=ncols,
            index=kwargs["isubplot"],
            sharex=kwargs["sharex"],
            sharey=kwargs["sharey"],
            wspace=kwargs["wspace"],
            hspace=kwargs["hspace"],
        )

    def __getattr__(self: FFig, item: str):  # noqa: ANN204
        """Pass unkown methods to current_axis, handle_plot, handle_axis or handle_fig."""
        # Check attributes of current_axis
        if hasattr(self.current_axis, item):
            return getattr(self.current_axis, item)

        # Check attributes of handle_plt
        if hasattr(self.handle_plot, item):
            return getattr(self.handle_plot, item)

        # Check attributes of handle_axis
        if hasattr(self.handle_axis, item):
            return getattr(self.handle_axis, item)

        # Check attributes of handle_fig
        if hasattr(self.handle_fig, item):
            return getattr(self.handle_fig, item)

        msg = f"'{item}' cannot be processed as axis or figure property.'"
        raise AttributeError(msg)

    def set_current_axis(self: FFig, index: int | None = None) -> None:
        """Set current axis index."""
        # Overwrite subplot_index with named argument
        if index is None:
            self.subplot_index += 1
        else:
            self.subplot_index = index

        # Set current axe handle
        self.subplot_index = self.subplot_index % (self.subplot_nrows * self.subplot_ncols)
        if self.subplot_nrows == 1 and self.subplot_ncols == 1:
            self.current_axis = self.handle_axis
        elif self.subplot_nrows > 1 and self.subplot_ncols > 1:
            isuby = self.subplot_index // self.subplot_ncols
            isubx = self.subplot_index % self.subplot_ncols
            self.current_axis = self.handle_axis[isuby][isubx]
        else:
            self.current_axis = self.handle_axis[self.subplot_index]

    def next_axis(self: FFig) -> None:
        """Iterate current axis to next subplot."""
        self.set_current_axis(index=None)

    def subplot(  # noqa: PLR0913
        self: FFig,
        *args: int,
        nrows: int | None = None,
        ncols: int | None = None,
        index: int | None = None,
        wspace: float | None = None,
        hspace: float | None = None,
        sharex: bool | str = False,
        sharey: bool | str = False,
    ) -> None:
        """Set or create subplot configuration and select current axis.

        This method can be used in three ways:
        1. Select an existing subplot by index subplot(2), but you may also use next_axis()
        2. Create a new subplot grid with subplot(1,3)
        3. Create a new subplot grid with specific index with subplot(1,3,2)

        Parameters
        ----------
        *args : int
            Positional arguments can be:
            - Single int: subplot index to select
            - Two ints: (nrows, ncols) for new grid
            - Three ints: (nrows, ncols, index) for new grid with selection
        nrows : int | None, optional
            Number of rows in subplot grid, by default None
        ncols : int | None, optional
            Number of columns in subplot grid, by default None
        index : int | None, optional
            Index of subplot to select (0-based), by default None
        wspace : float | None, optional
            Vertical space between subplots, by default None
        hspace : float | None, optional
            Horizontal space between subplots, by default None
        sharex : bool | str, optional
            Share x-axis between subplots, by default False
            Can be bool or {'none', 'all', 'row', 'col'}
        sharey : bool | str, optional
            Share y-axis between subplots, by default False
            Can be bool or {'none', 'all', 'row', 'col'}

        Examples
        --------
        >>> fig.subplot(0)  # Select first subplot
        >>> fig.subplot()  # Select next subplot
        >>> fig.subplot(2, 2)  # Create 2x2 grid
        >>> fig.subplot(2, 2, 1)  # Create 2x2 grid and select index 1
        >>> fig.subplot(nrows=2, ncols=2, sharex=True)  # 2x2 grid sharing x-axis

        Notes
        -----
        - Subplot indices are 0-based and ordered row-wise
        - Creating a new grid clears the existing figure
        - When sharing axes, 'all' shares between all subplots,
          'row' shares within rows, 'col' shares within columns
        """
        if len(args) == 1:
            index = args[0]
        elif len(args) == 2:  # noqa: PLR2004
            nrows, ncols = args
        elif len(args) == 3:  # noqa: PLR2004
            nrows, ncols, index = args
        elif len(args) > 3:  # noqa: PLR2004
            msg = "Invalid arguments for subplot"
            raise ValueError(msg)

        if nrows is not None or ncols is not None:
            # Generate new subplot
            if nrows is None:
                nrows = 1
            if ncols is None:
                ncols = 1
            if index is None:
                index = 0
            self.subplot_nrows = nrows
            self.subplot_ncols = ncols
            self.subplot_sharex = sharex
            self.subplot_sharey = sharey
            self.subplot_wspace = wspace
            self.subplot_hspace = hspace

            self.handle_fig.clf()
            self.handle_axis = self.handle_fig.subplots(
                nrows=self.subplot_nrows,
                ncols=self.subplot_ncols,
                sharex=self.subplot_sharex,
                sharey=self.subplot_sharey,
            )
            self.handle_fig.subplots_adjust(wspace=self.subplot_wspace, hspace=self.subplot_hspace)

        self.set_current_axis(index=index)

    def bar_plot(self: FFig, *args: float | str | bool, **kwargs: float | str | bool) -> None:
        """Create a bar plot.

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to matplotlib's bar. Common usage:
            - x : array-like
                The x coordinates of the bars
            - height : array-like
                The height of the bars
            - width : float or array-like, optional
                The width(s) of the bars, default 0.8
        **kwargs : float | str | bool
            Additional keyword arguments passed to bar. Common ones:
            - color : color or list of colors
                The colors of the bars
            - alpha : float
                Transparency, between 0 (transparent) and 1 (opaque)
            - align : {'center', 'edge'}, default 'center'
                Alignment of the bars to the x coordinates
            - label : str
                Label for the legend
            - bottom : array-like, optional
                The y coordinates of the bottom edges of the bars

        Returns
        -------
        matplotlib.container.BarContainer
            Container with all the bars and optionally errorbars

        Examples
        --------
        >>> fig.bar_plot([1, 2, 3], [4, 5, 6])  # Simple bar plot
        >>> fig.bar_plot([1, 2, 3], [4, 5, 6], width=0.5, color='red')  # Customized bars
        >>> fig.bar_plot([1, 2], [4, 5], yerr=[0.5, 0.5])  # With error bars
        >>> fig.bar_plot([1, 2], [4, 5], bottom=[1, 1])  # Stacked bars
        """
        self.handle_bar = self.current_axis.bar(*args, **kwargs)
        return self.handle_bar

    def plot(
        self: FFig,
        data: list | np.ndarray | "pd.DataFrame" | "pd.Series" = MAT_EXAMPLE,  # noqa: UP037
        *args: float | str | bool,
        **kwargs: float | str | bool,
    ) -> list[Line2D]:
        """Generate a line plot.

        Parameters
        ----------
        data : array-like or DataFrame
            If array-like: First row is used as x-values for all other rows
            If DataFrame: Index is used as x-values, each column as separate line
        *args : float | str | bool
            Additional positional arguments passed to matplotlib's plot function
            Common usage includes format strings like 'ro' for red circles
        **kwargs : float | str | bool
            Additional keyword arguments passed to matplotlib's plot function
            Common ones include: label, color, linestyle, marker, alpha

        Returns
        -------
        list[Line2D]
            List of line objects representing the plotted data

        """
        plot_objects = []

        try:
            import pandas as pd

            is_dataframe = isinstance(data, pd.DataFrame)
        except ImportError:
            is_dataframe = False

        if is_dataframe:
            # Plot each column of the DataFrame
            for column in data.columns:
                lines = self.current_axis.plot(
                    data.index, data[column], *args, label=column, **kwargs
                )
                plot_objects.extend(lines)
            # Set x-label based on index type
            if isinstance(data.index, pd.DatetimeIndex):
                self.set_xlabel("Date")
            elif data.index.name:
                self.set_xlabel(data.index.name)
        elif np.ndim(data) > 1:
            if np.shape(data)[0] > np.shape(data)[1]:
                data = data.T
            for imat in data[1:]:
                lines = self.current_axis.plot(data[0, :], imat, *args, **kwargs)
                plot_objects.extend(lines)
        elif (
            len(args) > 0
            and isinstance(args[0], (list, tuple))
            and all(np.shape(entry) == np.shape(data) for entry in args[0])
        ):
            for y in args[0]:
                lines = self.current_axis.plot(data, y, *args[1:], **kwargs)
                plot_objects.extend(lines)
        else:
            lines = self.current_axis.plot(data, *args, **kwargs)
            plot_objects.extend(lines)

        self.handle_plot = plot_objects
        return plot_objects

    def semilogx(
        self: FFig, *args: float | str | bool, **kwargs: float | str | bool
    ) -> list[Line2D]:
        """Create a plot with logarithmic x-axis scaling.

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to plot()
        **kwargs : float | str | bool
            Keyword arguments passed to plot()

        Returns
        -------
        list[Line2D]
            List of line objects representing the plotted data

        Example
        -------
        >>> fig.semilogx([1, 10, 100], [1, 2, 3])

        """
        lines = self.plot(*args, **kwargs)
        self.current_axis.set_xscale("log")
        return lines

    def semilogy(
        self: FFig, *args: float | str | bool, **kwargs: float | str | bool
    ) -> list[Line2D]:
        """Create a plot with logarithmic y-axis scaling.

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to plot()
        **kwargs : float | str | bool
            Keyword arguments passed to plot()

        Returns
        -------
        list[Line2D]
            List of line objects representing the plotted data

        Example
        -------
        >>> fig.semilogy([1, 2, 3], [1, 10, 100])

        """
        lines = self.plot(*args, **kwargs)
        self.current_axis.set_yscale("log")
        return lines

    def fill_between(
        self: FFig,
        *args: float | str | bool,
        color: list | None = None,
        alpha: float = 0.1,
        linewidth: float = 0,
        **kwargs: float | str | bool,
    ) -> mpl.collections.PolyCollection:
        """Fill the area between two curves.

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to matplotlib's fill_between. Common usage:
            - x : array-like
                The x coordinates
            - y1, y2 : array-like
                The y coordinates between which to fill
        color : list | None, optional
            Color for filling, by default None (uses last plot color)
        alpha : float, optional
            Transparency, by default 0.1
        linewidth : float, optional
            Width of the boundary line, by default 0
        **kwargs : float | str | bool
            Additional keyword arguments passed to fill_between

        Returns
        -------
        mpl.collections.PolyCollection
            The filled area

        Example
        -------
        >>> x = np.linspace(0, 2, 100)
        >>> y1 = np.sin(2*np.pi*x)
        >>> y2 = np.sin(2*np.pi*x) + 0.2
        >>> fig.fill_between(x, y1, y2, alpha=0.3)

        """
        if color is None:
            color = self.last_color()
        return self.current_axis.fill_between(
            *args,
            color=color,
            alpha=alpha,
            linewidth=linewidth,
            **kwargs,
        )

    def last_color(self) -> np.ndarray:
        """Return last color code used by plot.

        Returns
        -------
        np.ndarray
            RGB color array

        Raises
        ------
        ValueError
            If no plot exists yet

        """
        if self.handle_plot is None or len(self.handle_plot) == 0:
            msg = "No plot exists yet to get color from"
            raise ValueError(msg)
        return self.handle_plot[0].get_color()

    def pcolor(
        self: FFig,
        *args: float | str | bool,
        **kwargs: float | str | bool,
    ) -> mpl.collections.QuadMesh:
        """Create a pseudocolor plot of a 2D array.

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to matplotlib's pcolormesh. Common usage:
            - C : array-like
                2D array of color values
            - X, Y : array-like, optional
                Coordinates of the quadrilateral corners
        **kwargs : float | str | bool
            Keyword arguments passed to matplotlib's pcolormesh. Common ones:
            - cmap : str or Colormap, default='nipy_spectral'
                Colormap to use
            - vmin, vmax : float, optional
                Minimum and maximum values for colormap scaling
            - shading : {'flat', 'nearest', 'gouraud'}, optional
                How to shade the colormap

        Returns
        -------
        mpl.collections.QuadMesh
            The pseudocolor plot

        Example
        -------
        >>> x, y = np.meshgrid(np.linspace(-2, 2, 100), np.linspace(-2, 2, 100))
        >>> z = np.exp(-(x**2 + y**2))
        >>> fig.pcolor(z)
        >>> fig.colorbar()  # Add a colorbar

        """
        kwargs.setdefault("cmap", "nipy_spectral")
        self.handle_surface = self.current_axis.pcolormesh(*args, **kwargs)
        return self.handle_surface

    def pcolor_log(
        self: FFig,
        *args: float | str | bool,
        vmin: float | None = None,
        vmax: float | None = None,
        **kwargs: float | str | bool,
    ) -> mpl.collections.QuadMesh:
        """Create a pseudocolor plot with logarithmic color scaling.

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to matplotlib's pcolormesh. Common usage:
            - C : array-like
                2D array of color values (must be positive for log scale)
            - X, Y : array-like, optional
                Coordinates of the quadrilateral corners
        vmin : float | None, optional
            Minimum value for logarithmic scaling, by default None.
            If None, uses the minimum of the data
        vmax : float | None, optional
            Maximum value for logarithmic scaling, by default None.
            If None, uses the maximum of the data
        **kwargs : float | str | bool
            Additional keyword arguments passed to matplotlib's pcolormesh.
            Same as pcolor() with the addition of logarithmic normalization

        Returns
        -------
        mpl.collections.QuadMesh
            The pseudocolor plot with logarithmic color scaling

        Example
        -------
        >>> x, y = np.meshgrid(np.linspace(-2, 2, 100), np.linspace(-2, 2, 100))
        >>> z = np.exp(-(x**2 + y**2)) + 1  # Add 1 to ensure positive values
        >>> fig.pcolor_log(z, vmin=0.1, vmax=2)
        >>> fig.colorbar()

        """
        kwargs.setdefault("cmap", "nipy_spectral")
        kwargs_log = {}
        if vmin is not None:
            kwargs_log["vmin"] = vmin
        if vmax is not None:
            kwargs_log["vmax"] = vmax
        kwargs["norm"] = mpl.colors.LogNorm(**kwargs_log)
        self.handle_surface = self.current_axis.pcolormesh(*args, **kwargs)
        return self.handle_surface

    def pcolor_square(
        self: FFig,
        *args: float | str | bool,
        **kwargs: float | str | bool,
    ) -> mpl.collections.QuadMesh:
        """Create a square pseudocolor plot with hidden axes.

        Similar to pcolor() but creates a plot with:
        - Equal aspect ratio (square)
        - Hidden axes and ticks
        - Default 'nipy_spectral' colormap

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to matplotlib's pcolormesh. Common usage:
            - C : array-like
                2D array of color values
            - X, Y : array-like, optional
                Coordinates of the quadrilateral corners
        **kwargs : float | str | bool
            Keyword arguments passed to matplotlib's pcolormesh.
            Same as pcolor() but with hidden axes

        Returns
        -------
        mpl.collections.QuadMesh
            The square pseudocolor plot

        Example
        -------
        >>> data = np.random.rand(10, 10)  # Create 10x10 random matrix
        >>> fig.pcolor_square(data)  # Plot as square with hidden axes
        >>> fig.colorbar()  # Optionally add a colorbar

        """
        kwargs.setdefault("cmap", "nipy_spectral")
        self.handle_surface = self.current_axis.pcolormesh(*args, **kwargs)
        self.current_axis.axis("off")
        self.current_axis.set_aspect("equal")
        self.current_axis.set_xticks([])
        self.current_axis.set_yticks([])
        return self.handle_surface

    def contour(
        self: FFig,
        *args: float | str | bool,
        **kwargs: float | str | bool,
    ) -> mpl.contour.QuadContourSet:
        """Create a 2D contour plot.

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to matplotlib's contour. Common usage:
            - Z : array-like
                The height values over which the contour is drawn
            - levels : int or array-like, optional
                Number of contour levels or list of levels
        **kwargs : float | str | bool
            Keyword arguments passed to matplotlib's contour. Common ones:
            - colors : color string or sequence of colors
            - alpha : float
            - linestyles : string or tuple

        Returns
        -------
        mpl.contour.QuadContourSet
            The contour plot object

        Example
        -------
        >>> x, y = np.meshgrid(np.linspace(-2, 2, 100), np.linspace(-2, 2, 100))
        >>> z = np.exp(-(x**2 + y**2))
        >>> fig.contour(z, levels=[0.2, 0.5, 0.8], colors='black')

        """
        self.handle_surface = self.current_axis.contour(*args, **kwargs)
        return self.handle_surface

    def scatter(
        self: FFig,
        *args: float | str | bool,
        **kwargs: float | str | bool,
    ) -> mpl.collections.PathCollection:
        """Create a scatter plot.

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to matplotlib's scatter. Common usage:
            - x, y : array-like
                The data positions
            - s : float | array-like, optional
                The marker size in points**2
            - c : color or array-like, optional
                The marker colors
        **kwargs : float | str | bool
            Keyword arguments passed to matplotlib's scatter. Common ones:
            - alpha : float
                The alpha blending value, between 0 (transparent) and 1 (opaque)
            - marker : str
                The marker style
            - cmap : str or Colormap
                A colormap for coloring the markers
            - label : str
                Label for the legend

        Returns
        -------
        mpl.collections.PathCollection
            The scatter plot collection

        Example
        -------
        >>> x = np.random.rand(50)
        >>> y = np.random.rand(50)
        >>> colors = np.random.rand(50)
        >>> fig.scatter(x, y, c=colors, s=500*colors, alpha=0.5, cmap='viridis')

        """
        self.handle_surface = self.current_axis.scatter(*args, **kwargs)
        return self.handle_surface

    def colorbar(
        self: FFig,
        *args: float | str | bool,
        **kwargs: float | str | bool,
    ) -> mpl.colorbar.Colorbar:
        """Add a colorbar to the current plot.

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to matplotlib's colorbar
        **kwargs : float | str | bool
            Keyword arguments passed to colorbar. Common ones:
            - label : str
                Label for the colorbar
            - orientation : {'vertical', 'horizontal'}
                Colorbar orientation

        Returns
        -------
        mpl.colorbar.Colorbar
            The colorbar object

        Example
        -------
        >>> fig.pcolor(data)
        >>> fig.colorbar(label='Values')

        """
        return self.handle_fig.colorbar(*args, self.handle_surface, ax=self.current_axis, **kwargs)

    def grid(
        self: FFig,
        *args: int | str,
        color: str = "grey",
        alpha: float = 0.2,
        **kwargs: int | str | bool,
    ) -> None:
        """Add a grid to the current plot.

        Parameters
        ----------
        *args : int | str
            Arguments passed to matplotlib's grid
        color : str, optional
            Grid line color, by default "grey"
        alpha : float, optional
            Grid line transparency, by default 0.2
        **kwargs : int | str | bool
            Additional keyword arguments passed to grid. Common ones:
            - which : {'major', 'minor', 'both'}
                The grid lines to apply to
            - axis : {'both', 'x', 'y'}
                The axis to apply the grid to
            - linestyle : str
                The line style of the grid

        Example
        -------
        >>> fig.plot(data)
        >>> fig.grid(alpha=0.3, linestyle='--')

        """
        self.current_axis.grid(*args, color=color, alpha=alpha, **kwargs)

    def set_xlim(self: FFig, xmin: float | list[float] = np.inf, xmax: float = -np.inf) -> None:
        """Set limits for current x-axis.

        Parameters
        ----------
        xmin : float | list[float], optional
            Minimum x value or [xmin, xmax] list, by default np.inf
            If np.inf, will use minimum of plotted data
        xmax : float, optional
            Maximum x value, by default -np.inf
            If -np.inf, will use maximum of plotted data
            Ignored if xmin is a list

        Examples
        --------
        >>> fig.set_xlim(0, 1)  # set limits to 0 and 1
        >>> fig.set_xlim([0, 1])  # same as above
        >>> fig.set_xlim()  # auto-set to data min and max

        """
        try:
            if np.size(xmin) == 2:  # noqa: PLR2004
                xmax = xmin[1]
                xmin = xmin[0]
            elif xmin == np.inf and xmax == -np.inf:
                for iline in self.current_axis.lines:
                    xdata = iline.get_xdata()
                    xmin = np.minimum(xmin, np.nanmin(xdata))
                    xmax = np.maximum(xmax, np.nanmax(xdata))
            if version.parse(mpl.__version__) >= version.parse("3"):
                if np.isfinite(xmin):
                    self.current_axis.set_xlim(left=xmin)
                if np.isfinite(xmax):
                    self.current_axis.set_xlim(right=xmax)
            else:
                if np.isfinite(xmin):
                    self.current_axis.set_xlim(xmin=xmin)
                if np.isfinite(xmax):
                    self.current_axis.set_xlim(xmax=xmax)
        except (ValueError, TypeError):
            self.logger.exception("Error setting x limits")

    def set_ylim(self: FFig, ymin: float | list[float] = np.inf, ymax: float = -np.inf) -> None:
        """Set limits for current y-axis.

        Parameters
        ----------
        ymin : float | list[float], optional
            Minimum y value or [ymin, ymax] list, by default np.inf
            If np.inf, will use minimum of plotted data
        ymax : float, optional
            Maximum y value, by default -np.inf
            If -np.inf, will use maximum of plotted data
            Ignored if ymin is a list

        Examples
        --------
        >>> fig.set_ylim(0, 1)  # set limits to 0 and 1
        >>> fig.set_ylim([0, 1])  # same as above
        >>> fig.set_ylim()  # auto-set to data min and max

        """
        try:
            if np.size(ymin) == 2:  # noqa: PLR2004
                ymax = ymin[1]
                ymin = ymin[0]
            elif ymin == np.inf and ymax == -np.inf:
                for iline in self.current_axis.lines:
                    ydata = iline.get_ydata()
                    ymin = np.minimum(ymin, np.nanmin(ydata))
                    ymax = np.maximum(ymax, np.nanmax(ydata))
            if version.parse(mpl.__version__) >= version.parse("3"):
                if np.isfinite(ymin):
                    self.current_axis.set_ylim(bottom=ymin)
                if np.isfinite(ymax):
                    self.current_axis.set_ylim(top=ymax)
            else:
                if np.isfinite(ymin):
                    self.current_axis.set_ylim(ymin=ymin)
                if np.isfinite(ymax):
                    self.current_axis.set_ylim(ymax=ymax)
        except (ValueError, TypeError):
            self.logger.exception("Error setting y limits")

    def legend(
        self: FFig,
        *args: float | str | bool,
        labels: str | list[str] | None = None,
        **kwargs: float | str | bool,
    ) -> None:
        """Insert legend based on labels given in plot(x,y,label='Test1') etc.

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to matplotlib's legend
        labels : str | list[str] | None, optional
            Labels to assign to the lines in the plot. If provided,
            overwrites existing labels, by default None
        **kwargs : float | str | bool
            Keyword arguments passed to matplotlib's legend

        """
        if labels is not None:
            for ilabel, iline in enumerate(self.current_axis.lines):
                iline.set_label(labels[ilabel])
        _, labels = self.current_axis.get_legend_handles_labels()
        if np.size(self.current_axis.lines) != 0 and len(labels) != 0:
            self.current_axis.legend(*args, **kwargs)

    def legend_entries(self) -> tuple[list[Line2D], list[str]]:
        """Return handle and labels of legend.

        Returns
        -------
        tuple[list[Line2D], list[str]]
            Tuple containing:
            - List of Line2D objects representing plot handles
            - List of strings representing labels

        """
        handles, labels = self.current_axis.get_legend_handles_labels()
        return handles, labels

    def legend_count(self) -> int:
        """Return number of legend entries.

        Returns
        -------
        int
            Number of entries in the legend

        """
        handles, _ = self.current_axis.get_legend_handles_labels()
        return np.size(handles)

    def set_cycle(
        self: FFig,
        colors: dict[str, list[int]],
        color_seq: list[str],
        linestyle_seq: list[str],
    ) -> None:
        """Set cycle for colors and linestyles (will be used in this order).

        Parameters
        ----------
        colors : dict[str, list[int]]
            Dictionary mapping color names to RGB values (0-255)
        color_seq : list[str]
            Sequence of color names to use from the colors dictionary
        linestyle_seq : list[str]
            Sequence of line styles to use (e.g., ['-', '--', ':', '-.'])

        Example
        -------
        >>> colors = {'blue': [33, 101, 146], 'red': [218, 4, 19]}
        >>> fig.set_cycle(colors, ['blue', 'red'], ['-', '--'])

        """
        # generate cycle from color_seq and linestyle_seq
        color_list = [colors[icolor] for icolor in color_seq if icolor in colors]
        cyc_color = np.tile(color_list, (np.size(linestyle_seq), 1))
        cyc_linestyle = np.repeat(linestyle_seq, np.shape(color_list)[0])
        try:
            mpl.rc(
                "axes",
                prop_cycle=(cycler("color", cyc_color) + cycler("linestyle", cyc_linestyle)),
            )
        except (ValueError, TypeError):
            self.logger.exception("set_cycle(): Cannot set cycle for color and linestyle")

    def set_parameters(self: FFig) -> None:
        """Set figure parameters for optimal layout.

        This function is called automatically by save() and show().
        It performs the following:
        - Applies tight_layout() to optimize spacing
        - Adjusts subplot spacing if specified during creation

        Notes
        -----
        If tight_layout fails, it will be logged but won't raise an error.
        Subplot spacing is only adjusted if:
        - hspace was specified and there are multiple rows
        - wspace was specified and there are multiple columns

        """
        try:
            self.handle_fig.tight_layout()
        except (ValueError, TypeError):
            self.logger.exception("set_parameters(): Tight layout cannot be set!")

        if self.subplot_hspace is not None and self.subplot_nrows > 1:
            self.handle_fig.subplots_adjust(hspace=self.subplot_hspace)
        if self.subplot_wspace is not None and self.subplot_ncols > 1:
            self.handle_fig.subplots_adjust(wspace=self.subplot_wspace)

    def watermark(
        self: FFig,
        img: str | Path,
        xpos: float = 100,
        ypos: float = 100,
        alpha: float = 0.15,
        zorder: float = 1,
        **kwargs: float | str | bool,
    ) -> None:
        """Include watermark image to plot.

        Parameters
        ----------
        img : str | Path
            Path to image file
        xpos : float
            X position of watermark
        ypos : float
            Y position of watermark
        alpha : float
            Transparency of watermark
        zorder : float
            Z-order of watermark
        **kwargs : float | str | bool
            Additional keyword arguments passed to figimage

        Raises
        ------
        FileNotFoundError
            If image file does not exist

        """
        img_path = Path(img)
        if img_path.is_file():
            self.handle_fig.figimage(img_path, xpos, ypos, alpha=alpha, zorder=zorder, **kwargs)
        else:
            msg = f"Watermark image not found: {img_path}"
            raise FileNotFoundError(msg)

    def show(self: FFig, *, block: bool = False) -> None:
        """Show figure in interactive console.

        Displays the figure in the current backend's interactive window.
        Automatically calls set_parameters() before showing.

        Parameters
        ----------
        block : bool, optional
            If True, blocks execution until the figure window is closed.
            If False (default), continues execution immediately.

        Notes
        -----
        - When block=False, the figure window remains interactive but may
          be closed or lose focus when the script continues executing
        - In Jupyter notebooks, the block parameter has no effect as figures
          are displayed differently
        - set_parameters() is called automatically to ensure optimal layout

        Examples
        --------
        >>> fig.plot(data)
        >>> fig.show()  # Non-blocking display
        >>> fig.show(block=True)  # Block until window closed
        """
        self.set_parameters()
        plt.show(block=block)

    def save(
        self: FFig,
        filename: str | Path | None,
        *args: float | str | bool,
        **kwargs: float | str | bool,
    ) -> list[Path]:
        """Save figure as image (png, pdf...).

        Parameters
        ----------
        filename : str | Path
            Base filename to save to. If no extension, defaults to .png
        *args : float | str | bool
            Can include:
            - Integer for DPI value
            - Strings for additional formats (e.g., 'pdf', '.pdf')
        **kwargs : float | str | bool
            Additional arguments passed to savefig. Common ones:
            - dpi : int, default=300
                The resolution in dots per inch
            - bbox_inches : str
                How to trim the figure
            - transparent : bool
                Whether to save with transparent background

        Returns
        -------
        list[Path]
            Returns list of paths to all files that were successfully saved.

        Examples
        --------
        >>> fig.save('plot.png', 600)  # Save as PNG with 600 dpi
        >>> fig.save('plot.png', 'pdf')  # Save as both PNG and PDF
        >>> fig.save('plot', '.png', '.pdf', '.svg')  # Save in multiple formats
        >>> paths = fig.save('plot.png')  # Get saved paths

        """
        kwargs.setdefault("dpi", 300)  # Default to 300 dpi
        saved_files = []

        filepath = Path(filename)
        format_set = set()

        if filepath.suffix == "":
            msg = f"FFig: Filepath {filepath} has no suffix, defaulting to .png!"
            self.logger.warning(msg)
            format_set.add(".png")
        else:
            format_set.add(filepath.suffix)

        for iarg in args:
            if isinstance(iarg, int):
                kwargs["dpi"] = iarg
            elif isinstance(iarg, str):
                if iarg.startswith("."):
                    format_set.add(iarg)
                else:
                    format_set.add("." + iarg)

        self.set_parameters()

        for iformat in format_set:
            ifilepath = filepath.with_suffix(iformat)
            try:
                ifilepath.parent.mkdir(parents=True, exist_ok=True)
                self.handle_fig.savefig(ifilepath, **kwargs)
                saved_files.append(ifilepath)
            except (FileNotFoundError, PermissionError, OSError):
                except_message = f"save(): Figure cannot be saved to {ifilepath}"
                self.logger.exception(except_message)

        if self.figure_show:
            plt.show()  # block=False)
        else:
            plt.draw()

        return saved_files

    def clear(self: FFig, *args: float | str | bool, **kwargs: float | str | bool) -> bool:
        """Clear figure content to reuse the figure.

        Clears all plots and axes but maintains the figure object,
        allowing it to be reused for new plots.

        Parameters
        ----------
        *args : float | str | bool
            Arguments passed to matplotlib's clf()
        **kwargs : float | str | bool
            Keyword arguments passed to matplotlib's clf()

        Returns
        -------
        bool
            True if clearing was successful, False otherwise

        Example
        -------
        >>> fig.plot(data1)
        >>> fig.clear()  # Clear for reuse
        >>> fig.plot(data2)  # Plot new data

        """
        try:
            self.handle_fig.clf(*args, **kwargs)
        except (ValueError, TypeError, AttributeError):
            self.logger.exception("Error clearing figure")
            return False
        else:
            return True

    def close(self: FFig) -> bool:
        """Close the figure and clean up resources.

        Closes the figure window and cleans up memory resources.
        After closing, the figure cannot be reused - create a new figure instead.

        Returns:
        -------
        bool
            True if closing was successful, False otherwise

        Notes:
        -----
        - Use clear() instead if you want to reuse the figure
        - This method is automatically called when using the context manager

        Example:
        -------
        >>> fig.plot(data)
        >>> fig.save('plot.png')
        >>> fig.close()  # Clean up when done

        """
        try:
            plt.close(self.handle_fig)
        except (ValueError, TypeError, AttributeError):
            self.logger.exception("Error closing figure")
            return False
        else:
            return True


# %%
if __name__ == "__main__":
    fig = FFig()
    fig.plot()
    fig.show()

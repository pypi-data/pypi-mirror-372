# Scientific Plots
Create and save plots in scientific style

## Table of Contents
[[_TOC_]]

## Overview
This python module includes useful methods and definitions for various python
projects.
The focus lies of on the automatic creation of a set of plots, which are
designed to be used in scientific journals, dissertations and presentations.
The most important components are the definitions of types compatible
for numpy, located in `types_.py`, and the typing stubs in `stubs/`. These
typing stubs are also distributed in this package.

## Plotting
The easiest way to implement the plotting features provided by this library, is
to use one of the predefined function in `scientific_plots.default_plots`.
Alternatively, any plotting functions can be decorated by using the
`apply_styles` decorator in `scientific_plots.plot_settings`.

For example, this could look like this:
```
import matplotlib.pyplot as plt
from scientific_plots.plot_settings import apply_styles

@apply_styles
def plot_something() -> None:
    """Example function."""
    plt.plot(...)
    ...
    plt.savefig("subfolder/your_plot_name.pdf")
```

The script will create a bunch of plots and place them in the given location
next to your given path. Thus, it is advisable to create a different subfolder
for new plots.

For three-dimensional plots, it is recommended to set the optional argument
*three_d* of the decorator to true:
```
@apply_styles(three_d=True)
def plot_function():
    ...
```

Alternatively, this package provides default plot settings in the submodule
*default_plots*. The provided function apply a default design, which should
look good in most situations.

```
from scientific_plots.default_plots import plot

plot(x, y, "x_label", "y_label", "subfolder/filename.pdf")
```

Besides this simple plot, this library also provides the following default
plots:
`plot_fit`: Plot data and a fit of this data.
```
def fit_function(x):
    ...
    # fit some data
    ...
    return y

plot_fit(
    x, y, fit_function, "x_label", "y_label",
    "subfolder"/"filename.pdf")`
```

`two_plots`: Plot two curves sharing a single y-axis.
```
two_plots(
    x1, y1, "label1",
    x2, y2, "label2",
    "xlabel", "ylabel", "subfolder"/"filename".pdf)
```

`two_axis_plots`: Plot two curves with two y-axis in a single graph.
```
two_axis_plots(
    x1, y1, "label1",
    x2, y2, "label2",
    "xlabel", "ylabel1", "ylabel2",
    "subfolder"/"filename".pdf)
```

All of those functions have the following command-line arguments:
- `logscale`: Plot the data double logarithmic.
- `single_log`: Plot the x-axis logarithmic.
- `single_log_y`: Plot the y-axis logarithmic.
- `xlim`: Set the limits on the x-axis manually.
- `ylim`: Set the limits on the y-axis manually.

### Preview-Mode
It is possible to only create a single plot for every called plot function
to save computation time. This 'preview' mode can be called by setting the
following global variable in `scientific_plots.plot_settings` to true:
```
import scientifc_plots.plot_settings
scientifc_plots.plot_settings.PREVIEW = True
```

## Types
Additional Vector like types for numpy-arrays are provided in
`scientifc_plots.types_`.  These types can be used for static type checking
using mypy.

## Typing Stubs
Addtional typing stubs for scipy, matplotlib and numba are provided and
installed by this package. These packages do not provide type hints on their
own.

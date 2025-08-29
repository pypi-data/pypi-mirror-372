# FaSt_Fig
FaSt_Fig is a wrapper for matplotlib that provides a simple interface for fast and easy plotting.

Key features:
- Predefined templates for consistent styling
- Figure instantiation in a class object
- Simplified plotting methods with smart defaults
- Automatic handling of DataFrames
- Context manager support for clean resource management
- Type hints and logging for better development experience

## Installation

```bash
pip install fast_fig
```

## Basic Usage

```python
from fast_fig import FFig
x = [1,2,3,4,5]
y1 = [2,4,5,6,10]
y2 = [1,3,2,6,9]

# Simple plot example
fig = FFig()
fig.plot(x,y1)
fig.show()

# Use large template and save figure to multiple formats
fig = FFig('l')
fig.plot(x,y)
fig.save('plot.png', 'pdf')
```

## Context Manager

FaSt_Fig can be used as a context manager for automatic resource cleanup:

```python
with FFig('l', nrows=2, sharex=True) as fig:  # Large template, 2 rows sharing x-axis
    fig.plot([1, 2, 2.5], label="First")  # Plot in first axis/subplot
    fig.set_title("First plot")
    fig.next_axis()  # Switch to second axis/subplot
    fig.plot([0, 1, 2], [0, 1, 4], label="Second")  # Plot with x,y data
    fig.legend()  # Add legend
    fig.grid()  # Add grid
    fig.set_xlabel("X values")  # Label x-axis
    fig.save("plot.png", "pdf")  # Save as PNG and PDF
    # Figure automatically closed when exiting the with block
```

## Plot Types

FaSt_Fig supports all plots of matplotlib.
The following plots have adjusted settings to improve their use.

```python
# Bar plots
fig.bar_plot(x, height)

# Logarithmic scales
fig.semilogx(x, y)  # logarithmic x-axis
fig.semilogy(x, y)  # logarithmic y-axis

# 2D plots
x, y = np.meshgrid(np.linspace(-2, 2, 100), np.linspace(-2, 2, 100))
z = np.exp(-(x**2 + y**2))

fig.pcolor(z)  # pseudocolor plot
fig.colorbar(label='Values')  # add colorbar


fig.pcolor_log(z)  # pseudocolor with logarithmic color scale

fig.contour(z, levels=[0.2, 0.5, 0.8])  # contour plot

# Scatter plots
fig.scatter(x, y, c=colors, s=sizes)  # scatter plot with colors and sizes
```

## DataFrame Support

FaSt_Fig has built-in support for pandas DataFrames:

```python
import pandas as pd

# Create a DataFrame with datetime index
df = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [2, 4, 6, 8]
}, index=pd.date_range('2024-01-01', periods=4))

fig = FFig()
fig.plot(df)  # Automatic handling:
              # - Each column becomes a line
              # - Column names become labels
              # - Index used as x-axis
              # - Date index sets x-label to "Date"
```

## Matplotlib interaction

FaSt_Fig provides direct access to matplotlib objects through these handlers:

- `fig.current_axis`: Current axes instance for active subplot
- `fig.handle_fig`: Figure instance for figure-level operations
- `fig.handle_plot`: Current plot instance(s)
- `fig.handle_axis`: All axes instances for subplot access
```python
fig.current_axis.set_yscale('log')  # Direct matplotlib axis methods
fig.handle_fig.tight_layout()  # Adjust layout
fig.handle_plot[0].set_linewidth(2)  # Modify line properties
fig.handle_axis[0].set_title('First subplot')  # Access any subplot
```

These handles provide full access to matplotlib's functionality when needed.

## Presets

FaSt_Fig comes with built-in presets that control figure appearance. Available preset templates:

- `m` (medium): 15x10 cm, sans-serif font, good for general use
- `s` (small): 10x8 cm, sans-serif font, suitable for small plots
- `l` (large): 20x15 cm, sans-serif font, ideal for presentations
- `ol` (Optics Letters): 8x6 cm, serif font, optimized for single line plots
- `oe` (Optics Express): 12x8 cm, serif font, designed for equation plots
- `square`: 10x10 cm, serif font, perfect for square plots

Each preset defines:
- `width`: Figure width in cm
- `height`: Figure height in cm
- `fontfamily`: Font family (serif or sans-serif)
- `fontsize`: Font size in points
- `linewidth`: Line width in points

You can use presets in three ways:

1. Use a built-in preset:
```python
fig = FFig('l')  # Use large preset
```

2. Load custom presets from a file:
```python
fig = FFig('m', presets='my_presets.yaml')  # YAML format
fig = FFig('m', presets='my_presets.json')  # or JSON format
```

3. Override specific preset values:
```python
fig = FFig('m', width=12, fontsize=14)  # Override width and fontsize
```

The preset system also includes color sequences and line styles that cycle automatically when plotting multiple lines:
- Default colors: blue, red, green, orange
- Default line styles: solid (-), dashed (--), dotted (:), dash-dot (-.)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Licensed under MIT License. See [LICENSE](LICENSE) for details.

## Author

Written by Fabian Stutzki (fast@fast-apps.de)

For more information, visit [www.fast-apps.de](https://www.fast-apps.de)
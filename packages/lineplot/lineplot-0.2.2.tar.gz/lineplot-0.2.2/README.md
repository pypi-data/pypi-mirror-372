# lineplot

A minimalist line plotting package for live updates from jupyter notebooks. Works on google colab.

## Installation

```bash
pip install lineplot
```

## Example usage

```python
from lineplot import LinePlot
import numpy as np
import time

plot = LinePlot()
for i in range(100):
    plot.add(loss=1 / (i + 1), acc=1 - np.random.rand() / (i + 1))
    time.sleep(0.25)
```

## Documentation

First, instanciating a line plot widget:
```
plot = lineplot.LinePlot(
  width="50%", 
  height="auto", 
  x_ticks=16, 
  y_ticks=5, 
  colors=['blue', 'green', 'red', 'gold', 'magenta', 'cyan', 'purple', 'orange', 'brown']
)
```
Width and height are expressed in CSS units. Colors are looped if there are more datasets than colors.

Then, values for different metrics can be added progressively. The plot updates automatically. 
```
plot.add(name=value, name2=value2...)
```

You can use `**{"name with spaces and special characters": value}` to use more exotic data serie names.

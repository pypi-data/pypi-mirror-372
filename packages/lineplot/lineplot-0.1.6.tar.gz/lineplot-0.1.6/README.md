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

plot = LinePlot('green', 'blue')
for i in range(100):
    plot.add(loss=1 / (i + 1), acc=1 - np.random.rand() / (i + 1))
    time.sleep(0.25)
```

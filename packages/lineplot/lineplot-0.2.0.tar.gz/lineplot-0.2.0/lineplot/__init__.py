"""
A minimalist line plotting package for live updates from jupyter notebooks. Works on google colab.

Example:

from lineplot import LinePlot
import numpy as np
import time

plot = LinePlot('green', 'blue')
for i in range(100):
    plot.add(loss=1 / (i + 1), acc=1 - np.random.rand() / (i + 1))
    time.sleep(0.25)
"""

__version__ = "0.2.0"

from IPython.display import display, HTML, Javascript
import random, json

class LinePlot:
    def __init__(self, width="50%", height="auto", colors=['blue', 'green', 'red', 'gold', 'magenta', 'cyan', 'purple', 'orange', 'brown']):
      """Instanciates a new line plot. A color needs to be provided for each metric."""
      self.width = width
      self.height = height
      self.colors = colors
      self.id = random.randint(1, 10000000)
      self.values = {}
      self.script = display(HTML('<canvas style="width: {self.width}; height: {self.height}"></canvas>'), display_id=True)

    def add(self, **metrics):
      """Adds metrics to the plot, specified as named arguments"""
      for key, value in metrics.items():
        if key not in self.values:
          self.values[key] = []
        self.values[key].append(value)

      dataset = []
      for (key, value), color in zip(self.values.items(), self.colors[:len(self.values.keys())]):
        dataset.append({
          'name': key,
          'values': value,
          'color':  color,
        })
        
      self.script.update(HTML(f'''
  <canvas id="linePlot" style="width: {self.width}; height: {self.height}"></canvas>
  <script>
    function f() {{
    const datasets = {json.dumps(dataset)};

    const canvas = document.getElementById('linePlot');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    const ctx = canvas.getContext('2d');

    const width = canvas.width;
    const height = canvas.height;
    const padding = 60;

    // Find overall min and max across all datasets
    const allValues = datasets.flatMap(d => d.values);
    const minVal = Math.min(...allValues);
    const maxVal = Math.max(...allValues);
    const numPoints = datasets[0].values.length;

    // Scale function: maps data value to y coordinate
    function getY(value) {{
      const scaled = (value - minVal) / (maxVal - minVal);
      return height - padding - scaled * (height - 2 * padding);
    }}

    // X spacing between points
    const stepX = (width - 2 * padding) / (numPoints - 1);

    // Add Y-axis grid lines, ticks, and labels
    const numYTicks = 5;
    for (let i = 0; i <= numYTicks; i++) {{
      const value = minVal + (i / numYTicks) * (maxVal - minVal);
      const y = getY(value);

      // Grid line
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.strokeStyle = "#ccc";
      ctx.lineWidth = 1;
      ctx.stroke();

      // Label
      ctx.font = "12px Arial";
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";
      ctx.fillStyle = "#000";
      ctx.fillText(value.toFixed(5), padding - 8, y);
    }}

    // Add X-axis grid lines, ticks, and labels
    const numXTicks = 15;
    for (let i = 0; i < numXTicks; i++) {{
      const index = Math.round(i * (numPoints - 1) / (numXTicks - 1));
      const x = padding + index * stepX;
      const y = height - padding;

      // Grid line
      ctx.beginPath();
      ctx.moveTo(x, padding);
      ctx.lineTo(x, y);
      ctx.strokeStyle = "#eee";
      ctx.lineWidth = 1;
      ctx.stroke();

      // Label (index)
      ctx.font = "12px Arial";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = "#000";
      ctx.fillText(i, x, y + 8);
    }}

    // Draw each dataset
    datasets.forEach(ds => {{
      ctx.beginPath();
      ctx.moveTo(padding, getY(ds.values[0]));
      ds.values.forEach((val, i) => {{
        const x = padding + i * stepX;
        const y = getY(val);
        ctx.lineTo(x, y);
      }});
      ctx.strokeStyle = ds.color;
      ctx.lineWidth = 2;
      ctx.stroke();
    }});

    // Draw axes
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 2;
    ctx.stroke();


    // Draw legend (centered at top)
    const legendHeight = 20;
    const legendSpacing = 80; // horizontal spacing between legend items
    const legendTotalWidth = (datasets.length - 1) * legendSpacing + 80;
    let legendX = (width - legendTotalWidth) / 2;
    const legendY = 20;

    ctx.font = "14px Arial";
    datasets.forEach(ds => {{
      // Color box
      ctx.fillStyle = ds.color;
      ctx.fillRect(legendX, legendY, 15, 15);

      // Text
      ctx.fillStyle = "#000";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillText(ds.name, legendX + 20, legendY + 8);

      // Move to next item
      legendX += legendSpacing;
    }});
    }}
    f();
  </script>
'''))


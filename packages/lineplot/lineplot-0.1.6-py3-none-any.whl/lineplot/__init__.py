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

__version__ = "0.1.6"

from IPython.display import display, HTML, Javascript
import random, json

class LinePlot:
    def __init__(self, *colors):
      """Instanciates a new line plot. A color needs to be provided for each metric."""
      if colors == []:
        colors = ['red', 'green', 'blue', 'gold', 'magenta', 'cyan']
      self.id = random.randint(1, 10000000)
      self.values = {}
      display(HTML(f"""
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<div style="width: 50%">
  <canvas id="chart{self.id}"></canvas>
</div>
"""))
      display(Javascript(f"""
function f() {{
  const self = document.getElementById('chart{self.id}');
  self.chart = new Chart(self.getContext('2d'), {{
      type: 'line',
      data: {{
        labels: [],
        datasets: []
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: true,
        animation: false,
      }}
    }});

  const mapping = {{}};
  const colors = {json.dumps(colors)};

  self.chart_add = function(metrics) {{
    self.chart.data.labels.push(self.chart.data.labels.length);
    for (const [key, values] of Object.entries(metrics)) {{
      if (mapping[key] === undefined) {{
        mapping[key] = self.chart.data.datasets.length;
        self.chart.data.datasets.push({{
          label: key,
          data: values,
          borderWidth: 1,
          borderColor: colors[mapping[key] % colors.length],
          backgroundColor: colors[mapping[key] % colors.length],
          pointStyle: false,
        }});
      }} else {{
        self.chart.data.datasets[mapping[key]].data = values;
      }}
    }}
    self.chart.update();
  }}
}}
f();
"""))
      self.script = display(HTML('<script></script>'), display_id=True)

    def add(self, **metrics):
      """Adds metrics to the plot, specified as named arguments"""
      for key, value in metrics.items():
        if key not in self.values:
          self.values[key] = []
        self.values[key].append(value)
      self.script.update(Javascript(f'''
const self = document.getElementById('chart{self.id}');
self.chart_add({json.dumps(self.values)});
'''))


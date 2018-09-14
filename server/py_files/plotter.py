# At the moment this is a test graph to make sure the process works using bokeh.
import os
from bokeh.plotting import figure, output_file, show

# prepare some data
x = [1, 2, 3, 4, 5, 8, 10]
y = [6, 7, 2, 4, 5, 2, 6]

# output to static HTML file
output_file("temporary_graph.html")

# create a new plot with a title and axis labels
p = figure(title="simple line example", x_axis_label='x', y_axis_label='y')

# add a line renderer with legend and line thickness
p.line(x, y, legend="Temp.", line_width=2)

# show the results
show(p)

# Create new plotter.pug file
os.system("pugit < temporary_graph.html > client/views/plotter.pug")
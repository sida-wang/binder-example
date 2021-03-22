import pandas as pd

from bokeh.io import curdoc, show, output_notebook
from bokeh.layouts import row, column
from bokeh.models import (CDSView, ColorBar, ColumnDataSource,
                          CustomJS, CustomJSFilter, 
                          GeoJSONDataSource, HoverTool,
                          LinearColorMapper, Slider, ContinuousColorMapper,
                          Slider,
                          TapTool, OpenURL, Circle, RangeSlider, CheckboxButtonGroup,
                          Toggle)
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
#output_notebook()

def toggle_callback(toggle):
    js=CustomJS(args=dict(toggle=toggle), code="""
    if (toggle.button_type=="danger") {
    toggle.button_type="success"
    toggle.label='Active'
    }
    else {
    toggle.button_type="danger"
    toggle.label='Inactive'    
    }
""")
    return js

class Filter:

    def __init__(self, name, slider, toggle):
        self.name = name
        self.slider_ = slider
        self.toggle_ = toggle

STATISTICS = ['record_min_temp', 'actual_min_temp', 'average_min_temp', 'average_max_temp', 'actual_max_temp', 'record_max_temp']
X_RANGE = [16000000, 16600000]
Y_RANGE = [-4850000, -4150000]

tile_provider = get_provider('CARTODBPOSITRON')

tools = ["pan, wheel_zoom, box_zoom, reset, tap"]

p = figure(plot_width=1000,
            x_axis_type="mercator", y_axis_type="mercator",
            x_axis_label="Longitude", y_axis_label="Latitude",
            x_range=X_RANGE, y_range=Y_RANGE, tools=tools,
            title='Bores', output_backend='webgl')
p.add_tile(tile_provider)

filter_list = {}

for var in ['var1', 'var2', 'var3']:
    min_ = 0
    max_ = 100
    slider = RangeSlider(start=min_, end=max_, step=0.1, 
                         value=(min_,max_), title=f'{var} range')
    toggle = Toggle(label="Inactive", button_type="danger", aspect_ratio=3)
    toggle.js_on_click(toggle_callback(toggle))
    filter_list[var] = Filter(var, slider, toggle)

controls = column([row(filter.slider_, filter.toggle_) for key, filter in filter_list.items()])

layout = row(controls, p)

#show(layout)
curdoc().add_root(layout)
#curdoc().title = "Weather"

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point

from bokeh.io import curdoc, show, output_notebook
from bokeh.layouts import row, column
from bokeh.models import (CDSView, ColorBar, ColumnDataSource,
                          CustomJS, CustomJSFilter, 
                          GeoJSONDataSource, HoverTool,
                          LinearColorMapper, Slider, ContinuousColorMapper,
                          BooleanFilter, WheelZoomTool,
                          TapTool, OpenURL, Circle, RangeSlider, CheckboxButtonGroup,
                          Toggle)
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON, get_provider

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

npoints = 100

xpoints = np.random.randint(X_RANGE[0],X_RANGE[1],npoints)
ypoints = np.random.randint(Y_RANGE[0],Y_RANGE[1],npoints)

test_points = [Point(i) for i in zip(xpoints, ypoints)]

gdf = gpd.GeoDataFrame({'var1':np.random.randint(0,100,npoints),
                       'var2':np.random.randint(0,100,npoints),
                       'var3':np.random.randint(0,100,npoints)}, geometry=test_points)
geosource = GeoJSONDataSource(geojson=gdf.to_json())

test_view = CDSView(source=geosource, filters=[BooleanFilter(booleans=[True]*len(gdf))])

tile_provider = get_provider('CARTODBPOSITRON')

tools = ["pan, wheel_zoom, box_zoom, reset, tap"]

p = figure(plot_width=1000,
            x_axis_type="mercator", y_axis_type="mercator",
            x_axis_label="Longitude", y_axis_label="Latitude",
            x_range=X_RANGE, y_range=Y_RANGE, tools=tools,
            title='Bores', output_backend='webgl')
p.add_tile(tile_provider)
points_render = p.circle(x='x',y='y', source=geosource, view=test_view, size=10)

p.toolbar.logo = None
p.toolbar.active_scroll = p.select_one(WheelZoomTool)
p.add_tools(HoverTool(renderers=[points_render],
                      tooltips=[('Var1','@var1'),
                               ('Var2','@var2'),
                               ('Var3','@var3')]))

filter_list = {}

for var in ['var1', 'var2', 'var3']:
    min_ = 0
    max_ = 100
    slider = RangeSlider(start=min_, end=max_, step=0.1, 
                         value=(min_,max_), title=f'{var} range')
    toggle = Toggle(label="Inactive", button_type="danger", aspect_ratio=3)
    toggle.js_on_click(toggle_callback(toggle))
    filter_list[var] = Filter(var, slider, toggle)
    

def update_plot(attrname, old, new):
    mask = [True]*len(gdf)
    for key, filter in filter_list.items():
        if filter.toggle_.active:
            mask = mask & (gdf[key] >= filter.slider_.value[0]) & (gdf[key] <= filter.slider_.value[1])
    test_view.filters[0] = BooleanFilter(booleans=mask)

for _,filter in filter_list.items():
    filter.slider_.on_change('value',update_plot)
    filter.toggle_.on_change('active',update_plot)
    
controls = column([row(filter.slider_, filter.toggle_) for key, filter in filter_list.items()])

layout = row(controls, p, name='layout')

#show(layout)
curdoc().add_root(layout)
#curdoc().title = "Weather"

"""
map_util.py
Visualizing US state data on a geographical colormap
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as Basemap
from matplotlib.colors import rgb2hex
from matplotlib.patches import Polygon

def usa_state_colormap(state_dict, title='', colorbar_title=''):
    """
    Plot data as a function of US state onto a geographical colormap
    
    Parameters
    ----------
    state_dict : dict
        Keys are states, and values are the feature value to be converted to color
    title : str
        Title of plot
    colorbar_title : str
        Colorbar axis label
    
    Code adapted from:
    https://stackoverflow.com/questions/39742305/how-to-use-basemap-python-to-plot-us-with-50-states

    Required shape files (st9_d00...) acquired from:
    https://github.com/matplotlib/basemap/tree/master/examples
    """
    
    # Lambert Conformal map of lower 48 states.
    plt.figure(figsize=(10,8))
    m = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
            projection='lcc',lat_1=33,lat_2=45,lon_0=-95)
    # draw state boundaries.
    # data from U.S Census Bureau
    # http://www.census.gov/geo/www/cob/st2000.html
    shp_info = m.readshapefile('st99_d00','states',drawbounds=True)

    # choose a color for each state based on population density.
    colors={}
    statenames=[]
    cmap = plt.cm.viridis # use 'hot' colormap
    vmin = np.min(list(state_dict.values()))
    vmax = np.max(list(state_dict.values()))
    for shapedict in m.states_info:
        statename = shapedict['NAME']
        # skip DC and Puerto Rico.
        if statename not in ['District of Columbia','Puerto Rico']:
            pop = state_dict[statename]
            # calling colormap with value between 0 and 1 returns
            # rgba value.  Invert color range (hot colors are high
            # population), take sqrt root to spread out colors more.
            colors[statename] = cmap((pop-vmin)/(vmax-vmin))[:3]
        statenames.append(statename)
    
    # cycle through state names, color each one.
    ax = plt.gca() # get current axes instance
    for nshape,seg in enumerate(m.states):
        # skip DC and Puerto Rico.
        if statenames[nshape] not in ['Puerto Rico', 'District of Columbia']:
        # Offset Alaska and Hawaii to the lower-left corner. 
            if statenames[nshape] == 'Alaska':
            # Alaska is too big. Scale it down to 35% first, then transate it. 
                seg = list(map(alaska_transform, seg))
            if statenames[nshape] == 'Hawaii':
                seg = list(map(hawaii_transform, seg))

            color = rgb2hex(colors[statenames[nshape]]) 
            poly = Polygon(seg,facecolor=color,edgecolor=color)
            ax.add_patch(poly)
    plt.title(title, size=15)
            
    # Make colorbar
    # Make a figure and axes with dimensions as desired.
    fig = plt.figure(figsize=(8.5, 1))
    ax1 = fig.add_axes([0.05, 0.4, 0.9, 0.15])

    # Set the colormap and norm to correspond to the data for which
    # the colorbar will be used.
    cmap = mpl.cm.viridis
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    # ColorbarBase derives from ScalarMappable and puts a colorbar
    # in a specified axes, so it has everything needed for a
    # standalone colorbar.  There are many more kwargs, but the
    # following gives a basic continuous colorbar with ticks
    # and labels.
    cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                    norm=norm,
                                    orientation='horizontal')
    cb1.set_label(colorbar_title, size=15)
    return ax
    
    
def alaska_transform(xy):
    """Transform Alaska's geographical placement so fits on US map"""
    x, y = xy
    return (0.3*x + 1000000, 0.3*y-1100000)


def hawaii_transform(xy):
    """Transform Hawaii's geographical placement so fits on US map"""
    x, y = xy
    return (x + 5250000, y-1400000)

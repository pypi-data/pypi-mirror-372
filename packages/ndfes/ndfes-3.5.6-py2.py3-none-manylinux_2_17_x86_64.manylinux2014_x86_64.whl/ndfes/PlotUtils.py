#!/usr/bin/env python3


class LineStyle(object):
    """An object to store matplotlib line style parameters

    Attributes
    ----------
    show : bool, default=True
        Indicates if the line should be drawn

    linewidth : float, default=1
        The thickness of the line

    linestyle : str, default='-'
        The line style; e.g., 
        '-'  : solid
        '--' : dashed
        ':'  : dotted

    color : str or RBGA tuple, default='k'
        The line color. It can be a matplotlit color code ('k'=black) or
        a (R,B,G,A) tuple, where the elements are floats from 0 to 1, which
        control the red, blue, green, and alpha (transparency) of the color.
        The default is opaque black.  If this class is used to describe
        contour lines, then one cannot use the RBGA tuple

    alpha : float, default=1
        Transparency of the line (1=opaque)

    tmax : float
        A value from 0 to 1 that indicates the length of the line that
        should be drawn.  This is only valid if the line is obtained from
        a parametric spline.

    zorder : int, default=1
        The matplotlib drawing order. Higher values are drawn on top of lower
        values

    interp : bool, default=True
        If true, then interpolate the path from the spline. If false, then
        plot lines between the spline control points.

    Methods
    -------
    """
    
    def __init__(self):
        self.show = True
        self.linewidth = 1
        self.linestyle='-'
        self.color = 'k'
        self.alpha = 1
        self.tmax=1
        self.zorder=1
        self.interp = True

        
class SurfaceStyle(object):
    """An object to store matplotlib surface style parameters

    Attributes
    ----------
    show : bool, default=True
        Indicates if the line should be drawn

    alpha_occupied : float, default=1
        Transparency of the surface in the regions occupied with samples

    alpha_unoccupied : float, default=0
        Transparency of the surface in the regions not occupied by samples

    percent_white : float, default=0
        If 0, then the surface colors are determined from a colormap. If it
        is 1, then the surface is white. Intermediate values scale the colors
        to whiteness.

    percent_height : float, default=0
        If 0, then the surface is drawn on the back wall of the 3d plot.
        If 1, then the surface intersecting the path is drawn.
        Intermediate values push the surface from the wall toward the path
        in analogy to a rubber plane.

    linewidth : float, default=1
        The thickness of the line

    shade : bool, default=False
        Whether to shade the facecolors

    antialiased : bool, default=False
        Whether to draw with antialiasing

    zorder : int, default=1
        The matplotlib drawing order. Higher values are drawn on top of lower
        values

    Methods
    -------
    """
    def __init__(self):
        self.show = True
        self.alpha_occupied = 1
        self.alpha_unoccupied = 0
        self.percent_white = 0
        self.percent_height = 0
        self.linewidth = 0
        self.edgecolors = None
        self.shade=False
        self.antialiased=False
        self.zorder = 1



class AxesStyle(object):
    """A class that stores the matplotlib style parameters for an axes

    Attributes
    ----------
    label : str
        The description of the axes

    base : float
        The major tick stride

    labelpad : float
        The padding applied to the axes label

    tickpad : float
        The padding applied to the tick labels

    ticks : matplotlib.ticker.MultipleLocator
        The class that assigns plot ticks

    Methods
    -------
    """
    def __init__(self,label=r"X",base=1.0):
        """
        Parameters
        ----------
        label : str, default="X"
            The description of the axes

        base : float, default=1.0
            The major tick stride
        """
        self.label = label
        self.base = base
        self.labelpad = 0
        self.tickpad = 0
        self.base=-1
        self.SetTicks(base)

    def SetTicks(self,base):
        """Reset the ticks object if the stride changes
        
        Parameters
        ----------
        base : float
            The major tick stride
        
        Returns
        -------
        None
        """
        
        import matplotlib.ticker as plticker
        if base != self.base:
            self.base = base
            self.ticks = plticker.MultipleLocator(base=base)

            
class AxesLabels(object):
    """A class that collects the axes styles for multiple axes

    Attributes
    ----------
    axes : AxesStyle
        The style of each axes
    
    Methods
    -------
    """
    
    def __init__(self,ndim):
        """
        Parameters
        ----------
        ndim : int
            The number of axes dimensions to store
        """
        if ndim > 3:
            raise Exception("ndim too large %i"%(ndim))
        labels = ["X","Y","Z"]
        self.axes = []
        for dim in range(ndim):
            self.axes.append( AxesStyle(labels[dim],1.0) )

            
    def ApplyToPlot(self,ax,order=None):
        """Set the labels and ticks to a plot

        Parameters
        ----------
        ax : matplotlib.axes.AxesSubplot
            The plot to modify

        order : list of int, optional
            The list of axes to modify. If None, then all axes are modified.
            Note that order=[1,0] would apply the y-axes style to the x-axes
            and the x-axes style to the y-axes. This can be useful when
            applying style to 2d projections of 3d data

        Returns
        -------
        None
        """
        
        if order is None:
            order = [i for i in range(len(self.axes))]
        elif len(order) > len(self.axes):
            raise Exception("len(order) too large %i"%(len(order)))

        i = order[0]
        ax.set_xlabel(self.axes[i].label,
                      labelpad=self.axes[i].labelpad)
        ax.tick_params(axis='x',which='major',
                       pad=self.axes[i].tickpad)
        ax.xaxis.set_major_locator(self.axes[i].ticks)

        if len(order) > 1:
            i = order[1]
            ax.set_ylabel(self.axes[i].label,
                          labelpad=self.axes[i].labelpad)
            ax.tick_params(axis='y',which='major',
                           pad=self.axes[i].tickpad)
            ax.yaxis.set_major_locator(self.axes[i].ticks)

        if len(order) > 2:
            i = order[2]
            ax.set_zlabel(self.axes[i].label,
                          labelpad=self.axes[i].labelpad)
            ax.tick_params(axis='z',which='major',
                           pad=self.axes[i].tickpad)
            ax.zaxis.set_major_locator(self.axes[i].ticks)



def ContourFmt(x):
    """
    Custom formatter that removes trailing zeros, e.g. "1.0" becomes "1". This
    is typically used as an argument to matplotlib's clabel method to inline
    contour values while plotting; e.g.,

    ax.clabel(labeled_contours, inline=True, fontsize=8, fmt=ContourFmt)

    Parameters
    ----------
    x : float
        
    Returns
    -------
    str
        The string representation of the numerical value with removed trailing
        zeros (and possibly decimal point)
    """
    
    from matplotlib import pyplot as plt

    s = f"{x:.1f}"
    if s.endswith("0"):
        s = f"{x:.0f}"
    return rf"{s}" if plt.rcParams["text.usetex"] else f"{s}"




class ColorAndContours(object):
    """A class to store information on the heatmap color scheme and contour
    levels to draw

    Attributes
    ----------
    cmap : matplotlib.colors.ListedColormap
        The colormap to be used to assign colors to values. This map 
        contains an extra region to make values > Zmax be drawn 
        transparently.

    colorbar_cmap : matplotlib.colors.ListedColormap
        The colormap to be used when drawing a colormap legend (colorbar)

    Zmin : float
        The smallest Z-value to appear on the colorbar

    Zmax : float
        The largest valid Z-value to consider

    colormax : float
        The largest Z-value to appear on the colorbar

    clipcolormax : float
        Z-values larger than this value will be clipped

    clevels : numpy.array
        The contour levels to be found

    contour_spacing : float
        The spacing between contour levels

    Methods
    -------
    """
    
    def __init__(self,Zmin,Zmax,clipmax=None,alpha=1,name="jet"):
        """
        Parameters
        ----------
        Zmin : float
            The lowest value to consider. Values lower than Zmin will be
            colored the same as Zmin

        Zmax : float
            The largest value to color. Values above Zmax will be 
            transparent, so Zmax should usually be the largest observation

        clipmax : float, default = None
            The largest value of the color range. All values between clipmax
            and Zmax will have the same color.

        name : str, default = "shifted_jet"
            The matplotlib colormap scheme

        """

        import copy
        import numpy as np
        import matplotlib.cm as cm
        from matplotlib.colors import ListedColormap

        self.Zmin = Zmin
        self.Zmax = Zmax
    
        #
        # Define the heat map color scheme
        #

        #
        # We could naively choose the heatmap color scale to go from
        # Zmin to Zmax, however, the free energy surface may sample
        # areas that have very large free energy values, which would
        # make the interesting areas of the plot to have a near
        # constant color.  Furthermore, we want to make the areas of
        # the plot that we have not sampled transparent.  If we were
        # to simply choose the colors to scale from "Zmin" to
        # "colormax" (rather than "Zmax") then all areas higher in
        # energy than "colormax" would be made transparent ...that
        # is not what we want to have happen. Instead, we will
        # create a new colormap that extends the region of the
        # highest color, so all energies between "colormax" and
        # "Zmax" have a constant color. This requires us to scale
        # the map so that the lowest-to-highest color goes from
        # Zmin-to-colormax.
        #
        # Furthermore, we will need to also keep a copy of the
        # unscaled colormap specifically for drawing the colorbar,
        # because we want the legend to scale from Zmin-to-colormax
        # (even though we are plotting the heatmap from Zmin-to-Zmax
        # with a scaled color scheme).
        #
        # clipcolormax
        #     If the free energy is larger than this value, then
        #     make that area transparent.  clipcolormax should be
        #     greater than or equal to colormax
        #
        # colormax
        #     If the free energy is larger than this value (but
        #     smaller than colormax should be less than or equal to
        #     clipcolormax
        #
        self.clipcolormax = Zmax
        if clipmax is None:
            self.colormax = min( Zmin + 50., self.clipcolormax )
        else:
            self.colormax = clipmax


            
        #
        # The new color map is created from a list of 256 elements.
        # Each element is a 4-vector (R,G,B,Alpha) describing the
        # color. In other words, element 128 (index 127) is the
        # color half-way through the scale.
        #
        # imax
        #     The integer that the unscaled colormap should end at.
        #     All integers above this should have the same color
        #     (color 255 in the colorbar colormap)
        #
        # colorbar_cmap
        #     The original colormap that traverses the range
        #     Zmin-to-Zmax. We need to keep this to draw the
        #     colorbar, which we shall label as going from
        #     Zmin-to-colormax
        #
        # colors
        #     A list of 256 color values
        #
        # cmap
        #     The colormap we use in imshow to draw the colors in
        #     the range Zmin-to-colormax and then a constant color
        #     from colormax-to-Zmax
        #
    
        imax = int(256*(self.colormax-Zmin)/(self.clipcolormax-Zmin))
        #imax = int(256*(self.clipcolormax-Zmin)/(self.colormax-Zmin))
        #print(Zmin,Zmax,self.colormax,self.clipcolormax,imax)
        self.colorbar_cmap = copy.copy(cm.get_cmap(name,256))
        #print(self.colorbar_cmap(np.linspace(0,1,imax)).shape)
        #print(np.array([self.colorbar_cmap(1.)]*(256-imax)).shape)
        if imax < 256:
            colors = np.vstack( (self.colorbar_cmap(np.linspace(0,1,imax)),
                                 [self.colorbar_cmap(1.)]*(256-imax) ))
        else:
            colors = self.colorbar_cmap(np.linspace(0,1,imax))
        colors[:,-1] *= alpha
        self.cmap = ListedColormap(colors,name="shifted"+name)

        #
        # If a free energy value is larger than the color scale
        # maximum, then set it's alpha channel to 0 (fully
        # transparent). For the shifted_cmap, the color scale
        # maximum is Zmax (which is defined below (the vmax key to
        # the matplotlib functions).
        #
    
        self.cmap.set_bad(alpha=0)
        self.cmap.set_over(alpha=0)

        #
        # Define the contour levels
        #
        # contour_spacing
        #     The spacing (kcal/mol) between contours
        #
        # levels_to_print
        #     A list of integer contour levels (0 being the contour
        #     at Zmin, and 1 being the contour at
        #     Zmin+contour_spacing, etc...). If the index of a level
        #     appears in the list, then the numerical value of the
        #     contour will be drawn along with the contour line.
        #     Alternatively, if a contour index does not appear in
        #     the list, then the contour line is drawn without
        #     drawing the numerical value.
        #
        # levels
        #     A temporary array of all possible contour levels. One
        #     would normally set this range from Zmin to Zmax in
        #     steps of contour_spacing, but if one gets too many
        #     contour lines that it makes the plot unreadable
        #     (because the surface is sampled at very high
        #     energies), then one might lower the upper bound to be
        #     something less than Zmax.
        #
        # unlabeled_levels
        #     The contour energy levels to draw lines for but NOT
        #     draw numerical values
        #
        # labeled_levels
        #     The contour energy levels to draw lines for AND draw
        #     numerical values
        #
    
        if Zmax-Zmin <= 25.:
            self.contour_spacing = 2.5
        else:
            self.contour_spacing = 5.0
        self.levels = np.arange( Zmin, Zmax, self.contour_spacing,
                                 dtype=float )
    

    def DrawColorbar(self,fig,pad=0.03,labelpad=2,cax=None,ax=None,label="kcal/mol"):
        """Add a colorbar to a figure

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure to be modified

        pad : float, default=0.02
            The amount of whitespace between the colorbar and plot area

        labelpad : float, default=2
            The amount of whitespace between the colorbar and its text label

        cax : matplotlib.Axes, default=None
            If one is plotting multiple heat maps and wants only 1 colorbar,
            then one can call 
               cax = fig.add_axes([left,bottom,width,height])
            to get a colorbar axes

        label : str, default="kcal/mol"
            The energy units

        Returns
        -------
        cb : matplotlib.colorbar.Colorbar
            The instance of the colorbar added to the figure
        
        cticker : matplotlib.ticker.MultipleLocator
            Object that controls the tick labels on the colorbar
        """

        import matplotlib.cm as cm
        import matplotlib.ticker as plticker

        cbar = cm.ScalarMappable( cmap=self.colorbar_cmap )
        cbar.set_array( [self.Zmin,self.colormax] )
        spacing = self.GetContourSpacing()
        cticker = plticker.MultipleLocator(base=spacing)
        myax=None
        if cax is None:
            myax = ax
        cb = fig.colorbar(cbar, orientation='vertical',
                          ticks=cticker, pad=pad, cax=cax, ax=myax)
        cb.set_label(label,labelpad=labelpad)
        return cb,cticker

    def GetContourSpacing(self):
        spacing = self.contour_spacing
        if self.colormax - self.Zmin > 40:
            spacing *= 2
        return spacing

    def CptColorsFromValues(self,v):
        """Assigns a (red,green,blue,alpha) color to each input value

        Parameters
        ----------
        v : numpy.array, size=(npt,)
            The input values

        Returns
        -------
        cv : numpy.array, size=(npt,4)
            The red, blue, green, alpha assignment for each input value
        """

        from matplotlib.colors import Normalize
        norm = Normalize( vmin=self.Zmin, vmax=self.clipcolormax )
        return self.cmap(norm(v))
    


def extract_contour_data(contour_set,levels):
    import numpy as np
    from matplotlib.patches import Polygon, Path
    contours = []


    # Generate contours
    #contour_set = plt.contour(vorticity.lon, vorticity.lat, vorticity, levels=levels,
    #                          colors='red' if is_cyclonic else 'blue')

    # Check if get_paths() is not available (old version)
    if not hasattr(contour_set, 'get_paths'):
        # Old version: iterate over each layer
        for i, collection in enumerate(contour_set.collections):
            # get each path in the layer (level)
            for path in collection.get_paths():
                # Process path
                #contours.append( Polygon(path.vertices) )
                contours.append(path)
    else:
        # New version: iterate over get_paths() and generate paths from segments
        # In new version get_paths() returns one joined path per level that has to be split up first to get each contour

        paths_by_layer = []
        for i, joined_paths_in_layer in enumerate(contour_set.get_paths()):
            separated_paths_in_layer = []
            path_vertices = []
            path_codes = []
            for verts, code in joined_paths_in_layer.iter_segments():
                if code == Path.MOVETO:
                    if path_vertices:
                        separated_paths_in_layer.append(Path(np.array(path_vertices), np.array(path_codes)))
                    path_vertices = [verts]
                    path_codes = [code]
                elif code == Path.LINETO:
                    path_vertices.append(verts)
                    path_codes.append(code)
                elif code == Path.CLOSEPOLY:
                    path_vertices.append(verts)
                    path_codes.append(code)
            if path_vertices:
                separated_paths_in_layer.append(Path(np.array(path_vertices), np.array(path_codes)))
                #separated_paths_in_layer.append(path_vertices)

            paths_by_layer.append(separated_paths_in_layer)

        for i, paths_in_layer in enumerate(paths_by_layer):
            # Process path
            for path in paths_in_layer:
                #contours.append( Polygon(path.vertices) )
                contours.append(path)
                #contours.append( path )
    return contours




def GetContourLines(mgridx,mgridy,mgridz,levels):
    """Computes contour lines from a 2d meshgrid

    Parameters
    ----------
    mgridx : numpy.array, shape=(nx,ny)
        A meshgrid representation of the slow index

    mgridy : numpy.array, shape=(nx,ny)
        A meshgrid representation of the fast index

    mgridz : numpy.array, shape=(nx,ny)
        A meshgrid representation of the values

    levels : list of float
        The contour levels to find

    Returns
    -------
    clines : matplotlib.contour.QuadContourSet
        The matplotlib representation of the contours. To extract the line
        segments for each contour level, use:
    
        for contour_level in clines.collections:
            # Each level found level has 1-or-more paths
            for path in contour_level.get_paths():
                # A path is a collection of (x,y) points
                verts = path.vertices
                for pt in verts:
                    print("x:",pt[0],"y:",pt[1])
        
    """
    import matplotlib.pyplot as plt
    import numpy as np
        
    tempfig = plt.figure()
    tempax = tempfig.add_subplot(111)
    #clines = tempax.contour(mgridx,mgridy,np.ma.array(mgridz,mask=(mgridz==np.nan)),levels,algorithm='mpl2014')
    clines = tempax.contour(mgridx,mgridy,mgridz,levels,algorithm='mpl2014')

    clines = extract_contour_data(clines,levels)
    tempax.remove()
    plt.close(tempfig)
    tempax=None
    tempfig=None

    return clines

    

def Plot2dHistogram(fig,ax,model,axlabels,csty,shift_fes=True,full=True,bounds=None):
    """Draw a 2d heatmap of the FES
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure containing the plot

    ax : matplotlib.axes.AxesSubplot
        The 2d plot to draw the heatmap

    model : ndfes.FES
        The object containing the free energy bin values
    
    axlabels : ndfes.AxesLabels
        The axes tick and label styles

    csty : ndfes.LineStyle
        The contour line style

    full : bool, default=True
        If full=False, then the grid covers the smallest possible range
        of occupied bins. Otherwise, it covers the full range of
        the virtual grid

    bounds : numpy.array, shape=(ndim,2), optional
        If not None, then bounds is the min and max value of the
        plot along each dimension, and the value of full is ignored

    Returns
    -------
    None
    """
    
    import numpy as np
    from . GridUtils import GetPtsFromRegGrid
    
    # ------------------------------------------------------------
    # Get the regular grid points and FES values
    # ------------------------------------------------------------
    #
    # mgrid : numpy.array, shape=(2,nx,ny)
    #     Collection of meshgrids that define the positions of the
    #     histogram bin centers
    #
    # gridpts : numpy.array, shape=(nx*ny,2)
    #     Representation of the meshgrid as a series of points
    #
    # vals : numpy.array, shape=(nx*ny,)
    #     The free energy values at the bin centers
    #
    # mask : numpy.array, shape=(nx*ny,), dtype=bool
    #     True if the bin center is occupied by samples
    #
    # ranges : numpy.array, shape=(ndim,2), dtype=float, optional
    #     The min and max plot range in each dimension. If None,
    #     then the bounds are determined from the model checkpoint
    #     file.
    #
    
    mgrid   = np.array( model.GetRegGridCenters(full=full,bounds=bounds) )
    gridpts = GetPtsFromRegGrid(mgrid)
    vals    = np.array(model.GetBinValues(gridpts))
    mask    = model.GetOccMask(gridpts)

    #
    # minval : float
    #     The minimum fes value
    #
    
    if shift_fes:
        #minval = min([ v for v in vals if v is not None ])
        #model.ShiftBinValues( minval )
        model.ShiftFES(None)
        vals = np.array(model.GetBinValues(gridpts))
    
    # ------------------------------------------------------------
    # Get the plot colors
    # ------------------------------------------------------------
    #
    # nx : int
    #     The number of points in the x-direction
    #
    # ny : int
    #     The number of points in the y-direction
    #
    # maxval : float
    #     The maximum FES value
    #
    # colordata : ndfes.ColorAndContours
    #     Object that assigns color values and contour levels
    #
    # mvals : numpy.array, shape=(nx,ny)
    #     A meshgrid of masked FES values. If the grid point
    #     is in an unoccipied area, then it is assigned a large
    #     energy value
    #
    # colors : numpy.array, shape=(nx,ny,4)
    #     A meshgrid of (r,g,b,a) color values
    #
    
    nx = mgrid.shape[1]
    ny = mgrid.shape[2]
    minval = min([ v for v in vals if v is not None ])
    maxval = max([ v for v in vals if v is not None ])
    colordata = ColorAndContours(minval,maxval)
    # Note: vals is a mixture of datatypes, but we need inform numpy
    # that mvals is an array of floats so we can pass mvals to the
    # matplotlib routines
    mvals = np.array(np.where(mask,vals,1.e+5),dtype=float).reshape(nx,ny)
    fvals = np.array(np.where(mask,vals,np.inf),dtype=float).reshape(nx,ny)
    
    # ------------------------------------------------------------
    # Draw the figure
    # ------------------------------------------------------------
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # 1. Create contour lines
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    levels_to_label = [2,4,6,8]
    unlabeled_levels=[]
    labeled_levels=[]
    for i in range(len(colordata.levels)):
        if i in levels_to_label:
            labeled_levels.append(colordata.levels[i])
        else:
            unlabeled_levels.append(colordata.levels[i])

    unlabeled_contours = ax.contour(
        mgrid[0,:,:], mgrid[1,:,:], fvals.reshape(nx,ny),
        levels=unlabeled_levels,
        colors=csty.color,
        linewidths=csty.linewidth,
        linestyles=csty.linestyle,
        alpha=csty.alpha)

    labeled_contours = ax.contour(
        mgrid[0,:,:], mgrid[1,:,:], fvals.reshape(nx,ny),
        levels=labeled_levels,
        colors=csty.color,
        linewidths=csty.linewidth,
        linestyles=csty.linestyle,
        alpha=csty.alpha)

    #
    # The clabel command will show the numerical values of
    # the contour lines right were the lines are. If you
    # uncomment this, you'll still have contour lines, but
    # the numerical values won't be included
    #

    ax.clabel(labeled_contours, inline=True, fontsize=7,
              fmt=ContourFmt)
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # 2. The colored heatmap
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    #
    # Define the range of the plot axis
    #

    extent = model.GetRegGridExtent(full=full,bounds=bounds)
    dx = extent[1]-extent[0]  # xmax - xmin
    dy = extent[3]-extent[2]  # ymax - ymin
    aspect = dx/dy

    #
    # matplotlib function optional arguments
    #
    
    contour_kwargs = {
        'extent': extent,  # range of plot
        'aspect': aspect,  # shape of plot
        'origin': 'lower', 
        'vmin': colordata.Zmin,
        'vmax': colordata.Zmax,
        'cmap': colordata.cmap, # the colormap
        'interpolation': None # heatmap smoothing method
    }

    # Note: 2d heatmap plots have the y-axis as the slow axis, so we
    # need to transpose our meshgrid of values
    ax.imshow(mvals.T, **contour_kwargs )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # 3. The colorbar and axes labels
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # colordata.DrawColorbar(fig,pad=0.04,labelpad=2)
    # axlabels.ApplyToPlot(ax)

    cax = None
    cb,cticker = colordata.DrawColorbar(fig,pad=0.015,labelpad=0,cax=cax,ax=ax,label=model.EneUnits)
    cb.ax.tick_params(labelsize=8,rotation=90)
    for t in cb.ax.get_yticklabels():
        t.set_fontsize(8)
        #cb.set_label(None)
    axlabels.ApplyToPlot(ax)
    return cb,cticker

    

def Plot2dPath(fig,ax,path_crds,mgrid,model,axlabels,csty,lsty,
               minene=None,maxene=None,full=True,bounds=None,
               range180=False):
    """Draw a 2d heatmap of the FES with a free energy pathway
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure containing the plot

    ax : matplotlib.axes.AxesSubplot
        The 2d plot to draw the heatmap

    path_crds : numpy.array, shape=(npts,2)
        The (x,y) coordinates for each point along the path

    mgrid : numpy.array, shape=(2,nx,ny)
        The collection of (nx,ny) meshgrids to draw the pixels. The slow
        index is the meshgrid for X and the fast index is the meshgrid
        for Y

    model : ndfes.FES
        The object containing the free energy bin values

    axlabels : ndfes.AxesLabels
        The axes tick and label styles

    csty : ndfes.LineStyle
        The contour line style

    lsty : ndfes.LineStyle
        The path line style

    minene : float, optional, default=None
        The lowest energy to plot. If None, then it is the smallest
        encountered value.  This is useful to choose the minimum
        of the path to being the zero of energy, whereas there
        might be a noisey random fluctuation somewhere else on 
        the FES that technically has a lower energy.

    maxene : float, optional, default=None
        The largest energy to plot. If None, then it is the largest
        encountered value

    full : bool, default=True
        If full=False, then the grid covers the smallest possible range
        of occupied bins. Otherwise, it covers the full range of
        the virtual grid

    bounds : numpy.array, shape=(ndim,2), optional
        If not None, then bounds is the min and max value of the
        plot along each dimension, and the value of full is ignored

    range180 : bool, default=False
        If False, then the path is wrapped to [0,360), else
        it is wrapped to [-180,180). This has no effect on
        dimensions that are not periodic.

    Returns
    -------
    cc : ColorsAndContours
       Only useful to know the scale and contour levels

    cbar : ColorBar
       The matplotlib colorbar object

    cticker : 
       The matplotlib colorbar ticker object
    """

    import numpy as np
    from . GridUtils import GetPtsFromRegGrid

    # ------------------------------------------------------------
    # Get the regular grid points and FES values
    # ------------------------------------------------------------
    #
    # gridpts : numpy.array, shape=(nx*ny,2)
    #     Representation of the meshgrid as a series of points
    #
    # vals : numpy.array, shape=(nx*ny,)
    #     The free energy values at the bin centers
    #
    # mask : numpy.array, shape=(nx*ny,), dtype=bool
    #     True if the bin center is occupied by samples
    #
    
    gridpts = GetPtsFromRegGrid(mgrid)
    vals    = model.CptInterp(gridpts,k=100).values
    mask    = model.GetOccMask(gridpts)
    #mask    = [ True for m in mask ]
    vals    = np.where(mask,vals,None)

    # ------------------------------------------------------------
    # Get the plot colors
    # ------------------------------------------------------------
    #
    # nx : int
    #     The number of points in the x-direction
    #
    # ny : int
    #     The number of points in the y-direction
    #
    # maxval : float
    #     The maximum FES value
    #
    # colordata : ndfes.ColorAndContours
    #     Object that assigns color values and contour levels
    #
    # mvals : numpy.array, shape=(nx,ny)
    #     A meshgrid of masked FES values. If the grid point
    #     is in an unoccipied area, then it is assigned a large
    #     energy value
    #
    # colors : numpy.array, shape=(nx,ny,4)
    #     A meshgrid of (r,g,b,a) color values
    #
    
    nx = mgrid.shape[1]
    ny = mgrid.shape[2]
    maxobs = max([ v for v in vals if v is not None ])
    if minene is None:
        minval = min([ v for v in vals if v is not None ])
    else:
        minval = minene
    if maxene is None:
        maxval = max([ v for v in vals if v is not None ])
    else:
        maxval = maxene
        
    colordata = ColorAndContours(minval,max(maxobs,maxval),clipmax=maxval+1.e-8)
    # Note: vals is a mixture of datatypes, but we need inform numpy
    # that mvals is an array of floats so we can pass mvals to the
    # matplotlib routines
    mvals = np.array(np.where(mask,vals,1.e+5),dtype=float).reshape(nx,ny)
    fvals = np.array(np.where(mask,vals,np.inf),dtype=float).reshape(nx,ny)

    # ------------------------------------------------------------
    # Draw the figure
    # ------------------------------------------------------------
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # 1. Create contour lines
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    levels_to_label = [2,4,6,8]
    unlabeled_levels=[]
    labeled_levels=[]
    for i in range(len(colordata.levels)):
        if i in levels_to_label:
            labeled_levels.append(colordata.levels[i])
        else:
            unlabeled_levels.append(colordata.levels[i])

    unlabeled_contours = ax.contour(
        mgrid[0,:,:], mgrid[1,:,:], fvals.reshape(nx,ny),
        levels=unlabeled_levels,
        colors=csty.color,
        linewidths=csty.linewidth,
        linestyles=csty.linestyle,
        alpha=csty.alpha)

    labeled_contours = ax.contour(
        mgrid[0,:,:], mgrid[1,:,:], fvals.reshape(nx,ny),
        levels=labeled_levels,
        colors=csty.color,
        linewidths=csty.linewidth,
        linestyles=csty.linestyle,
        alpha=csty.alpha)

    #
    # The clabel command will show the numerical values of
    # the contour lines right were the lines are. If you
    # uncomment this, you'll still have contour lines, but
    # the numerical values won't be included
    #

    ax.clabel(labeled_contours, inline=True, fontsize=7,
              fmt=ContourFmt)
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # 2. The colored heatmap
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    #
    # Define the range of the plot axis
    #

    extent = model.GetRegGridExtent(full=full,bounds=bounds)
    dx = extent[1]-extent[0]  # xmax - xmin
    dy = extent[3]-extent[2]  # ymax - ymin
    aspect = dx/dy

    #
    # matplotlib function optional arguments
    #
    
    contour_kwargs = {
        'extent': extent,  # range of plot
        'aspect': aspect,  # shape of plot
        'origin': 'lower', 
        'vmin': colordata.Zmin,
        'vmax': colordata.Zmax,
        'cmap': colordata.cmap, # the colormap
        'interpolation': None # heatmap smoothing method
    }

    # Note: 2d heatmap plots have the y-axis as the slow axis, so we
    # need to transpose our meshgrid of values
    ax.imshow(mvals.T, **contour_kwargs )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # 3. The path line
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if path_crds is not None:
        segs = model.grid.WrapPathSegments(path_crds,range180=range180)
        for seg in segs:
            ax.plot( seg[:,0], seg[:,1],
                     linestyle=lsty.linestyle,
                     linewidth=lsty.linewidth,
                     color=lsty.color,
                     alpha=lsty.alpha )
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # 4. The colorbar and axes labels
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #colordata.DrawColorbar(fig,pad=0.04,labelpad=2)
    #axlabels.ApplyToPlot(ax)

    cax = None
    cb,cticker = colordata.DrawColorbar(fig,pad=0.015,labelpad=0,cax=cax,ax=ax,label=model.EneUnits)
    cb.ax.tick_params(labelsize=8,rotation=90)
    for t in cb.ax.get_yticklabels():
        t.set_fontsize(8)
        #cb.set_label(None)
    axlabels.ApplyToPlot(ax)
    return colordata,cb,cticker



def GetPathCrdsAndColors(self):
    import numpy as np
    if self.linestyle.interp:
        nt = int(500*self.linestyle.tmax)+1
        ts = np.linspace(0,self.linestyle.tmax,nt)
        path_crds = np.array([ self.path.GetValue(t) for t in ts])
    else:
        path_crds = []
        for i in range(self.path.t.shape[0]):
            #print(i,self.path.t[i],self.linestyle.tmax)
            if self.path.t[i] <= self.linestyle.tmax+1.e-9:
                path_crds.append( self.path.x[i,:] )
        path_crds = np.array( path_crds )
        #print(path_crds.shape,path_crds)
    N = path_crds.shape[0]
    if self.linestyle.color is None:
        pvals = self.model.CptInterp( path_crds, k=100. ).values
        pmask = np.array(self.model.GetOccMask( path_crds ))
        pmaskedvals = np.where(pmask,pvals,1.e+5)
        colors = []
        for i in range(N-1):
            if not pmask[i] or not pmask[i+1]:
                colors.append([0,0,0,1])
            else:
                gapval = 0.5*(pmaskedvals[i]+pmaskedvals[i+1])
                cs = self.colorobj.CptColorsFromValues([gapval])
                colors.append( cs[0] )
    else:
        colors = [self.linestyle.color]*(N-1)
    return path_crds,colors
        

class PathProj3D(object):
    """A class for drawing planes and lines of a free energy pathway in
    3-dimensions.  The 3D projection of the path consists of 4 main
    components: (1) xy-plane, (2) xz-plane, (3) yz-plane, (4) the pathway
    drawn in 3d space.  If the planes are projected onto their corresponding
    "wall" of the 3d cube, then one can also draw contours on the planes
    and a shadow/projection of the 3d path onto the wall.

    Formally, the xy-plane is defined by constructing a radial basis function
    that returns the z-values of the path, given the (x,y)-values of the path.
    The plane is then the evaluation of the radial basis function at arbitrary
    (x,y) values which may not reside on the path to get the plane's
    corresponding z-value.  Because this results in a unqiue z-value for any
    (x,y)-pair, one can lookup the free energy at all points on the plane
    and draw the plane as a projection on the cube's (x,y,zmin) "wall".
    The xz- and yz-planes are defined similarly.

    Attributes
    ----------
    face : str
        Either 'xy', 'xz', or 'yz', indicating which plane is being drawn

    path : ndfes.PGPRCurve or ndfes.PCurve
        Parametric curve of the pathway. It must have a method 
        path.GetValue(t) that returns the 3-dimensional coordinate of the
        path at the specified t-value

    extents : list, len=4
        The min and max values of the area being plotted. For the xy-plane, 
        it stores the values [xmin,xmax,ymin,ymax]

    surfacestyle : SurfaceStyle
        Plotting options for the surface

    linestyle : LineStyle
        Plotting option for the projection of the path onto the plane

    contourstyle : LineStyle
        Plotting option for the contours

    hmin : float
        The minimum height of the surface; e.g., the "back wall" of the cube
        For a xy-plane, this is the maximum z-value of the drawn plot

    hmax : float
        The maximum height of the surface; e.g., the "front wall" of the cube
        For a xy-plane, this the minimum z-value of th drawn plot

    mgslow : numpy.array, shape(ns,nf)
        The meshgrid of the plane's slow index.  For a xy-plane, "x" is the
        slow index and "y" is the fast index.  The shape's ns and nf is the
        size of the grid in the slow and fast directions, respectively.

    mgfast : numpy.array, shape(ns,nf)
        The meshgrid of the plane's fast index.

    colorobj : ColorAndContours
        The object that assigns colors and contour levels

    occ : numpy.array of bool, shape=(ns*nf,)
        True if the meshgrid plane lies within a bin occupied by samples
        False if it lies in an unoccupied area

    mgc : numpy.array, shape=(ns*nf,4)
        The (R,G,B,A) color value of each point on the plane

    mgv : numpy.array, shape=(ns,nf)
        The interpolated free energy value at each point on the plane

    mgmv : numpy.array, shape=(ns,nf)
        The masked free energy value at each point on the plane. If the
        point on the plane is in an unoccupied area, then the value is
        set to a very large value

    clines : matplotlib.contour.QuadContourSet
        The matplotlib representation of the contours


    Methods
    -------
    """
    
    def __init__(self,face,extents,path,mesh,model,colorobj):
        """
        Parameters
        ----------
        face : str
            Either 'xy', 'xz', or 'yz', indicating which plane is being drawn

        extents : list, len=6
            The min and max values of the 3d area being plotted. 
            It stores the values [xmin,xmax,ymin,ymax,zmin,zmax]

        path : ndfes.PGPRCurve or ndfes.PCurve
            Parametric curve of the pathway. It must have a method 
            path.GetValue(t) that returns the 3-dimensional coordinate of the
            path at the specified t-value

        mesh : numpy.array, shape=(3,nx,ny,nz)
            The meshgrid of drawn data

        model : ndfes.FES or derived object
            The object that tracks grid information and bin occupancies

        colorobj : ndfes.ColorAndContours
            The object controlling colors and contour levels
        """
        from scipy.interpolate import Rbf
        import numpy as np

        self.face = face
        self.path = path
        
        self.surfacestyle = SurfaceStyle()
        self.linestyle = LineStyle()
        self.contourstyle = LineStyle()

        self.linestyle.linewidth = 1.5
        self.contourstyle.linewidth = 1
        self.contourstyle.alpha_occupied = 0.7
        self.contourstyle.alpha_unoccupied = 0.3
        self.model = model

        path_crds = np.array([ self.path.GetValue(t,extrapolate=True)
                               #for t in np.linspace(-0.1,1.1,300)]) 
                               for t in np.linspace(0,1,300)]) 

        if self.face == 'xy':
            self.extents = [ extents[i] for i in [0,1,2,3] ]
            self.hmin = extents[4]
            self.hmax = extents[5]
            self.mgslow = mesh[0,:,:,0]
            self.mgfast = mesh[1,:,:,0]
            ns = self.mgslow.shape[0]
            nf = self.mgslow.shape[1]
            rbf = Rbf( path_crds[:,0], path_crds[:,1], path_crds[:,2],
                       function='linear' )
            self.mgh = rbf(self.mgslow,self.mgfast)
            pcrds = np.array( [self.mgslow.T,self.mgfast.T,self.mgh.T] ).T
            pcrds = pcrds.reshape(ns*nf,3)
            self.surfacestyle.zorder = 2
            self.contourstyle.zorder = 8
            self.linestyle.zorder = 8
            
        elif self.face == 'xz':
            self.extents = [ extents[i] for i in [0,1,4,5] ]
            self.hmin = extents[3]
            self.hmax = extents[2]
            self.mgslow = mesh[0,:,0,:]
            self.mgfast = mesh[2,:,0,:]
            ns = self.mgslow.shape[0]
            nf = self.mgslow.shape[1]
            rbf = Rbf( path_crds[:,0], path_crds[:,2], path_crds[:,1],
                       function='linear' )
            self.mgh = rbf(self.mgslow,self.mgfast)
            pcrds = np.array( [self.mgslow.T,self.mgh.T,self.mgfast.T] ).T
            pcrds = pcrds.reshape(ns*nf,3)
            self.surfacestyle.zorder = 4
            self.contourstyle.zorder = 5
            self.linestyle.zorder = 9
            
        elif self.face == 'yz':
            self.extents = [ extents[i] for i in [2,3,4,5] ]
            self.hmin = extents[0]
            self.hmax = extents[1]
            self.mgslow = mesh[1,0,:,:]
            self.mgfast = mesh[2,0,:,:]
            ns = self.mgslow.shape[0]
            nf = self.mgslow.shape[1]
            rbf = Rbf( path_crds[:,1], path_crds[:,2], path_crds[:,0],
                       function='linear' )
            self.mgh = rbf(self.mgslow,self.mgfast)
            pcrds = np.array( [self.mgh.T,self.mgslow.T,self.mgfast.T] ).T
            pcrds = pcrds.reshape(ns*nf,3)
            self.surfacestyle.zorder = 6
            self.contourstyle.zorder = 7
            self.linestyle.zorder = 10

        #self.datarange = [ self.mgslow[0,0], self.mgslow[-1,0],
        #                   self.mgfast[0,0], self.mgfast[0,-1] ]
            
        pvals = model.CptInterp( pcrds, k=100. ).values
        pmask = np.array(model.GetOccMask( pcrds ))
        pmaskedvals = np.where(pmask,pvals,1.e+5)
        self.colorobj = colorobj
        self.mgv  = pvals.reshape( (ns,nf) )
        self.mgmv = pmaskedvals.reshape( (ns,nf) )
        self.mgc = colorobj.CptColorsFromValues(pmaskedvals)
        self.occ = np.where(pmask,1.,0.)
        for i in range(len(pmask)):
            if not pmask[i]:
                self.mgc[i,:3] = 1
        self.mgc = self.mgc.reshape(ns,nf,4)
        self.occ = self.occ.reshape(ns,nf)

        pnvals = np.where(pmask,pvals,np.nan)
        self.clines = GetContourLines( self.mgslow, self.mgfast,
                                       pnvals.reshape(ns,nf),
                                       colorobj.levels )


        cblk = (0,0,0,1)
        ctrn = (0,0,0,0)

        #for icline,cline in enumerate(self.clines.collections):
        #    for ipath,path in enumerate(cline.get_paths()):
        #        v = path.vertices
        for ipath,path in enumerate(self.clines):
                #v = path.get_xy()
                v=path.vertices
        
                z = rbf(v[:,0],v[:,1])
                path.crds = np.zeros( (z.shape[0],3) )
                if self.face == 'xy':
                    path.crds[:,0] = v[:,0]
                    path.crds[:,1] = v[:,1]
                    path.crds[:,2] = z
                elif self.face == 'xz':
                    path.crds[:,0] = v[:,0]
                    path.crds[:,1] = z
                    path.crds[:,2] = v[:,1]
                elif self.face == 'yz':
                    path.crds[:,0] = z
                    path.crds[:,1] = v[:,0]
                    path.crds[:,2] = v[:,1]
                occ = model.GetOccMask(path.crds)
                path.colors = np.array([ cblk if o else ctrn for o in occ ])

                        

    def imshow(self,ax):
        """Draws the surface, contours, and line on a 3d axes

        Parameters
        ----------
        ax : matplotlib.axes.AxesSubplot
            The matplotlib object to draw the plane
        """
        
        import numpy as np
        
        if self.surfacestyle.show and \
           (self.surfacestyle.alpha_occupied > 0 or
            self.surfacestyle.alpha_unoccupied > 0):
            
            w = self.surfacestyle.percent_height
            h = w * self.hmax + (1-w) * self.hmin
            if self.hmin < self.hmax:
                h = np.where(self.mgh > h,h,self.mgh)
            else:
                h = np.where(self.mgh < h,h,self.mgh)
                
                
            w = self.surfacestyle.percent_white
            c = (1-w) * self.mgc
            for i in range(3):
                c[:,:,i] += w
                
            c[:,:,3] = self.surfacestyle.alpha_occupied * self.occ \
                + self.surfacestyle.alpha_unoccupied * ( 1-self.occ )
            
            if self.face == 'xy':
                x = self.mgslow
                y = self.mgfast
                z = h
            elif self.face == 'xz':
                x = self.mgslow
                y = h
                z = self.mgfast
            elif self.face == 'yz':
                x = h
                y = self.mgslow
                z = self.mgfast

            ax.plot_surface(x,y,z,
                facecolors=c,
                linewidth=self.surfacestyle.linewidth,
                rstride=1,
                cstride=1,
                antialiased=self.surfacestyle.antialiased,
                #edgecolors=self.surfacestyle.edgecolors,
                shade=self.surfacestyle.shade,
                zorder=self.surfacestyle.zorder)

            
        if self.surfacestyle.percent_height == 0 and \
           self.contourstyle.alpha > 0 and \
           self.contourstyle.show:
        
            #for cline in self.clines.collections:
            #    for path in cline.get_paths():
            for path in self.clines:
                    v = path.crds
 
                    if self.face == 'xy':
                        v=np.array( [ [v[ipt,0],v[ipt,1],self.hmin]
                                      for ipt in range(v.shape[0]) ] )
                    elif self.face == 'xz':
                        v=np.array( [ [v[ipt,0],self.hmin,v[ipt,2]]
                                      for ipt in range(v.shape[0]) ] )
                    elif self.face == 'yz':
                        v=np.array( [ [self.hmin,v[ipt,1],v[ipt,2]]
                                      for ipt in range(v.shape[0]) ] )

                    if len(v) > 0:
                        ax.plot(v[:,0],v[:,1],v[:,2],
                            linewidth=self.contourstyle.linewidth,
                            linestyle=self.contourstyle.linestyle,
                            color=self.contourstyle.color,
                            alpha=self.contourstyle.alpha,
                            zorder=self.contourstyle.zorder)

        
        if self.surfacestyle.percent_height == 0 and \
           self.linestyle.tmax > 0 and \
           self.linestyle.alpha > 0 and \
           self.linestyle.show:

            path_crds,gap_colors = GetPathCrdsAndColors(self)
            
            if self.face == 'xy':
                path_crds[:,2] = self.hmin
            elif self.face == 'xz':
                path_crds[:,1] = self.hmin
            elif self.face == 'yz':
                path_crds[:,0] = self.hmin

            if self.linestyle.color is not None:
                ax.plot(*path_crds.T,
                        linewidth=self.linestyle.linewidth,
                        linestyle=self.linestyle.linestyle,
                        color=self.linestyle.color,
                        alpha=self.linestyle.alpha,
                        zorder=self.linestyle.zorder)
            else:
                N = path_crds.shape[0]
                for i in range(N-1):
                    ax.plot(*path_crds[i:i+2,:].T,
                            linewidth=self.linestyle.linewidth,
                            linestyle=self.linestyle.linestyle,
                            color=gap_colors[i],
                            alpha=self.linestyle.alpha,
                            zorder=self.linestyle.zorder)


        
    def plot2d(self,ax):
        """Draws the surface, contours, and line on a 2d axes

        Parameters
        ----------
        ax : matplotlib.axes.Axes3DSubplot
            The matplotlib object to draw the plane
        """

        import numpy as np
        
        datarange = [ self.mgslow[0,0], self.mgslow[-1,0],
                      self.mgfast[0,0], self.mgfast[0,-1] ]
        
        wx = self.extents[1]-self.extents[0]  # xmax - xmin
        wy = self.extents[3]-self.extents[2]  # ymax - ymin
        aspect = wx/wy

        contour_kwargs = {
            'extent': datarange,  # range of plot
            'aspect': aspect,  # shape of plot
            'origin': 'lower', 
            'interpolation': None # heatmap smoothing method
        }

        w = self.surfacestyle.percent_white
        c = (1-w) * self.mgc
        for i in range(3):
            c[:,:,i] += w
                
        c[:,:,3] = self.surfacestyle.alpha_occupied * self.occ \
            + self.surfacestyle.alpha_unoccupied * ( 1-self.occ )

        ax.imshow( c.swapaxes(0,1),
                   **contour_kwargs,
                   zorder=self.surfacestyle.zorder)




        if self.contourstyle.alpha > 0 and \
           self.contourstyle.show:

            ns = self.mgslow.shape[0]
            nf = self.mgfast.shape[1]
            vals = np.where(self.occ.reshape(ns,nf),self.mgv,np.nan)


            levels_to_label = [2,4,6,8]
            unlabeled_levels=[]
            labeled_levels=[]
            for i in range(len(self.colorobj.levels)):
                if i in levels_to_label:
                    labeled_levels.append(self.colorobj.levels[i])
                else:
                    unlabeled_levels.append(self.colorobj.levels[i])
            
            labeled_contours = ax.contour(
                self.mgslow, self.mgfast, vals,
                levels=labeled_levels,
                linewidths=self.contourstyle.linewidth,
                linestyles=self.contourstyle.linestyle,
                colors=self.contourstyle.color,
                alpha=self.contourstyle.alpha,
                zorder=self.contourstyle.zorder)

            unlabeled_contours = ax.contour(
                self.mgslow, self.mgfast, vals,
                levels=unlabeled_levels,
                linewidths=self.contourstyle.linewidth,
                linestyles=self.contourstyle.linestyle,
                colors=self.contourstyle.color,
                alpha=self.contourstyle.alpha,
                zorder=self.contourstyle.zorder)

            #
            # The clabel command will show the numerical values of the
            # contour lines right were the lines are. If you uncomment
            # this, you'll still have contour lines, but the numerical
            # values won't be included
            #
        
            #ax.clabel(labeled_contours, inline=True, fontsize=8,
            #          fmt=ndfes.ContourFmt)


        
        if self.linestyle.tmax > 0 and \
           self.linestyle.alpha > 0 and \
           self.linestyle.show:

            path_crds,gap_colors = GetPathCrdsAndColors(self)
                        
            if self.face == 'xy':
                x = path_crds[:,0]
                y = path_crds[:,1]
            elif self.face == 'xz':
                x = path_crds[:,0]
                y = path_crds[:,2]
            elif self.face == 'yz':
                x = path_crds[:,1]
                y = path_crds[:,2]

            if self.linestyle.color is not None:
                ax.plot(x,y,
                        linewidth=self.linestyle.linewidth,
                        linestyle=self.linestyle.linestyle,
                        color=self.linestyle.color,
                        alpha=self.linestyle.alpha,
                        zorder=self.linestyle.zorder)
            else:
                N = path_crds.shape[0]
                for i in range(N-1):
                    ax.plot(x[i:i+2],y[i:i+2],
                            linewidth=self.linestyle.linewidth,
                            linestyle=self.linestyle.linestyle,
                            color=gap_colors[i],
                            alpha=self.linestyle.alpha,
                            zorder=self.linestyle.zorder)

        
        ax.set_xlim(self.extents[0],self.extents[1])
        ax.set_ylim(self.extents[2],self.extents[3])
        ax.grid(zorder=1)




        
        
class PathCube(object):
    """A class that can draw: (1) a 3d cube, and (2) 2d projections
    of the 3d cube.

    Attributes
    ----------
    linestyle : LineStyle
        Drawing properties of the 3d-line tracing the path

    extents : list, len=6
        The minimum and maximum values of the drawable area
        [xmin,xmax,ymin,ymax,zmin,zmax]

    path : ndfes.PGPRCurve or ndfes.PCurve
        A parametric spline describing the path

    xy : PathProj3D
        Projection of the path onto the xy-plane

    xz : PathProj3D
        Projection of the path onto the xz-plane

    yz : PathProj3D
        Projection of the path onto the yz-plane

    Methods
    -------
    """
    
    def __init__(self,extents,path,mesh,model,colorobj):
        """
        Parameters
        ----------
        extents : list, len=6
            The min and max values of the 3d area being plotted. 
            It stores the values [xmin,xmax,ymin,ymax,zmin,zmax]

        path : ndfes.PGPRCurve or ndfes.PCurve
            Parametric curve of the pathway. It must have a method 
            path.GetValue(t) that returns the 3-dimensional coordinate of the
            path at the specified t-value

        mesh : numpy.array, shape=(3,nx,ny,nz)
            The meshgrid of drawn data

        model : ndfes.FES or derived object
            The object that tracks grid information and bin occupancies

        colorobj : ndfes.ColorAndContours
            The object controlling colors and contour levels
        """
        
        self.linestyle = LineStyle()
        self.linestyle.zorder = 11
        self.linestyle.linewidth = 4
        self.extents = extents
        self.path = path
        self.model = model
        self.colorobj = colorobj
        self.xy = PathProj3D('xy',extents,path,mesh,model,colorobj)
        self.xz = PathProj3D('xz',extents,path,mesh,model,colorobj)
        self.yz = PathProj3D('yz',extents,path,mesh,model,colorobj)

    def imshow(self,ax):
        """Draws the surfaces, contours, and lines on a 3d axes

        Parameters
        ----------
        ax : matplotlib.axes.AxesSubplot
            The matplotlib object to draw the plane
        """

        import numpy as np
        
        for plane in [self.xy,self.xz,self.yz]:
            plane.imshow(ax)
            
        if self.linestyle.tmax > 0 and \
           self.linestyle.alpha > 0 and \
           self.linestyle.show:

            #nt = int(500*self.linestyle.tmax)+1
            #ts = np.linspace(0,self.linestyle.tmax,nt)
            #path_crds = np.array([ self.path.GetValue(t) for t in ts])

            path_crds,gap_colors = GetPathCrdsAndColors(self)
            
            if self.linestyle.color is not None:
                ax.plot(*path_crds.T,
                        linewidth=self.linestyle.linewidth,
                        linestyle=self.linestyle.linestyle,
                        color=self.linestyle.color,
                        alpha=self.linestyle.alpha,
                        zorder=self.linestyle.zorder)
            else:
                N = path_crds.shape[0]
                for i in range(N-1):
                    ax.plot(*path_crds[i:i+2,:].T,
                            linewidth=self.linestyle.linewidth,
                            linestyle=self.linestyle.linestyle,
                            color=gap_colors[i],
                            alpha=self.linestyle.alpha,
                            zorder=self.linestyle.zorder)
                
        ax.set_xlim(self.extents[0],self.extents[1])
        ax.set_ylim(self.extents[2],self.extents[3])
        ax.set_zlim(self.extents[4],self.extents[5])
        
            
    def SetLineStyle(self, *initial_data, **kwargs):
        """Apply the listed attributes to the lines within all planes
        and the 3D path

        Parameters
        ----------
        initial_data : named attributes, optional
            Any attribute in the LineStyle class
        
        kwargs : dictionary of attributes, optional
            Any attribute in the LineStyle class

        Examples
        --------
        SetLineStyle(show=True,linewidth=1,linestyle='-',color='k')

        kwargs={'show': True, 'linewidth':1, 'linestyle':'-', 'color'='k'}
        SetLineStyle(kwargs)
        """
        
        styles = [ self.xy.linestyle,
                   self.xz.linestyle,
                   self.yz.linestyle,
                   self.linestyle ]
        for dictionary in initial_data:
            for key in dictionary:
                for style in styles:
                    setattr(style, key, dictionary[key])
        for key in kwargs:
            for style in styles:
                setattr(style, key, kwargs[key])


    def SetSurfaceStyle(self, *initial_data, **kwargs):
        """Apply the listed attributes to the surface planes

        Parameters
        ----------
        initial_data : named attributes, optional
            Any attribute in the SurfaceStyle class
        
        kwargs : dictionary of attributes, optional
            Any attribute in the SurfaceStyle class

        Examples
        --------
        SetSurfaceStyle(show=True,alpha_unoccupied=0,percent_white=0)

        kwargs={'show': True,'alpha_unoccupied':0,'percent_white':0}
        SetSurfaceStyle(kwargs)
        """
        
        styles = [ self.xy.surfacestyle,
                   self.xz.surfacestyle,
                   self.yz.surfacestyle ]
        for dictionary in initial_data:
            for key in dictionary:
                for style in styles:
                    setattr(style, key, dictionary[key])
        for key in kwargs:
            for style in styles:
                setattr(style, key, kwargs[key])

                
    def SetContourStyle(self, *initial_data, **kwargs):
        """Apply the listed attributes to the contours in all planes

        Parameters
        ----------
        initial_data : named attributes, optional
            Any attribute in the LineStyle class
        
        kwargs : dictionary of attributes, optional
            Any attribute in the LineStyle class

        Examples
        --------
        SetContourStyle(show=True,linewidth=1,linestyle='-',color='k')

        kwargs={'show': True, 'linewidth':1, 'linestyle':'-', 'color'='k'}
        SetContourStyle(kwargs)
        """
        
        styles = [ self.xy.contourstyle,
                   self.xz.contourstyle,
                   self.yz.contourstyle ]
        for dictionary in initial_data:
            for key in dictionary:
                for style in styles:
                    setattr(style, key, dictionary[key])
        for key in kwargs:
            for style in styles:
                setattr(style, key, kwargs[key])




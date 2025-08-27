""" Line chart and color mpa Widgets based on pyqtgraph library
Copyright Nanosurf AG 2021
License - MIT
"""

from __future__ import print_function
import enum
from typing import Optional
import numpy as np

from PySide6 import QtGui

import pyqtgraph as pg
import pyqtgraph.functions as fn
import nanosurf.lib.datatypes.sci_channel as sci_channel
import nanosurf.lib.datatypes.sci_stream as sci_stream
from nanosurf.lib.gui import nsf_colors

pg.setConfigOption('foreground', 'w')
pg.setConfigOption('background', 'k')
pen1D = pg.mkPen(color='w', width=2)
color_nsf_second_line = nsf_colors.NSFColorsTuple.Soft_White
color_nsf_main_line = nsf_colors.NSFColorsTuple.Orange

class NSFChart(pg.GraphicsLayoutWidget):

    class Axis(enum.Enum):
        bottom = "bottom"
        left = "left"
        right = "right"
        top = "top"

    class AxisText:
        def __init__(self, name: str = "", unit: str = ""):
            self.name = name
            self.unit = unit

    
    def __init__(self, title: str = "Chart Plot", logmodex=False, logmodey=False, labelsize=12, titelsize=14):
        pg.GraphicsLayoutWidget.__init__(self)
        self.labelsize = labelsize
        self.titlesize = titelsize
        self.logmode_x = logmodex 
        self.logmode_y = logmodey
        self.axis_text = {axisname: NSFChart.AxisText() for axisname, _ in NSFChart.Axis.__members__.items()} 
        
        font = QtGui.QFont()
        font.setPixelSize(self.labelsize )

        self.plot:pg.PlotItem = self.addPlot()
        self.plot.setLogMode(self.logmode_x,self.logmode_y)
        self.plot.getAxis(NSFChart.Axis.bottom.value).tickFont = font
        self.plot.getAxis(NSFChart.Axis.bottom.value).setStyle(tickTextOffset = 3, tickLength = 5)
        self.plot.getAxis(NSFChart.Axis.left.value).tickFont = font
        self.plot.getAxis(NSFChart.Axis.left.value).setStyle(tickLength = 5)

        self.set_label(NSFChart.Axis.bottom, "X-Axis")
        self.set_label(NSFChart.Axis.left, "Y-Axis")
        self.set_title(title)

        self.plot_layers:List[pg.PlotDataItem] = [None, None]
        self.plot_layers[1] = self.plot.plot(pen = color_nsf_second_line)
        self.plot_layers[0] = self.plot.plot(pen = color_nsf_main_line) 
                                              
        self.view_box = self.plot.vb
        self.view_box.setMouseMode(1) # single mouse button mode
        self.plot.scene().sigMouseMoved.connect(self._move_cross_hair_cursor)
        self.plot.scene().leaveEvent = self._mouse_left_event_handler
        self.setMinimumHeight(200)
        self.setMinimumWidth(200)

        self._add_cross_hair_cursor()
        self._create_marker()
        self.clear_plots()

    def set_title(self, title: str):
        self.plot_title = title
        self._show_title(self.plot_title)

    def get_title(self) -> str:
        return self.plot_title

    def set_label(self, axis: Axis, label: str):
        self.axis_text[axis.value].name = label
        self._show_label(axis)

    def set_unit(self, axis: Axis, unit: str):
        self.axis_text[axis.value].unit = unit
        self._show_label(axis)

    def set_range_x(self, left:float, right:float):
        if self.logmode_x:
            self.plot.setXRange(np.log10(left), np.log10(right))
        else:
            self.plot.setXRange(left, right)

    def set_range_y(self, bottom:float, top:float):
        if self.logmode_x:
            self.plot.setYRange(np.log10(bottom), np.log10(top))
        else:
            self.plot.setYRange(bottom, top)
    
    def set_log_mode_x(self, log_mode:bool = True):
        self.logmode_x = log_mode
        self.plot.setLogMode(self.logmode_x, self.logmode_y)

    def set_log_mode_y(self, log_mode:bool = True):
        self.logmode_y = log_mode
        self.plot.setLogMode(self.logmode_x, self.logmode_y)

    def set_data_point_symbols(self, symbols: str | list[str], layer:int=0):
        self.plot_layers[layer].setSymbol(symbols)

    def plot_data(self, y: list | np.ndarray, x: Optional[list | np.ndarray] = None, layer_index: int = 0, max_index:int=None):
        
        if isinstance(x, np.ndarray):
            x = x.tolist()
        if isinstance(y, np.ndarray):
            y = y.tolist()
            
        if layer_index < len( self.plot_layers):
            p = self.plot_layers[layer_index]

            if x is not None:
                x_data = x     
            else:
                x_data = [x for x in range(len(y))]

            if max_index is None:
                max_index = len(y)
            p.setData(x=x_data[:max_index], y=y[:max_index])

    def plot_channel(self, channel:sci_channel.SciChannel, layer_index: int = 0, max_index:int=None):
        if layer_index < len( self.plot_layers):
            p = self.plot_layers[layer_index]
            self.set_label(NSFChart.Axis.left, channel.name) 
            self.set_unit(NSFChart.Axis.left, channel.unit) 
            if max_index is None:
                max_index = len(channel.value)            
            p.setData(y=channel.value[:max_index]) 

    def plot_stream(self, stream: sci_stream.SciStream, channel_index: int = 0, layer_index: int = 0, max_index:int=None):
        if layer_index < len( self.plot_layers):
            p = self.plot_layers[layer_index]
            ch = stream.get_channel(channel_index)
            self.set_label(NSFChart.Axis.bottom, stream.x.name) 
            self.set_label(NSFChart.Axis.left, ch.name) 
            self.set_unit(NSFChart.Axis.bottom, stream.x.unit) 
            self.set_unit(NSFChart.Axis.left, ch.unit) 
            if max_index is None:
                max_index = len(ch.value)
            p.setData(x=stream.x.value[:max_index], y=ch.value[:max_index]) 

    def extend_plot_layers(self, num_layers: int):
        if num_layers > len(self.plot_layers):
            missing_layers = num_layers - len(self.plot_layers)
            self.plot_layers.extend([self.plot.plot(pen = color_nsf_second_line) for i in range(missing_layers)])

    def clear_plots(self):
        for p in self.plot_layers:
            p.setData(x=[], y=[])    

    def get_plot_layer(self, layer_index: int): 
        if layer_index < len(self.plot_layers): 
            return  self.plot_layers[layer_index]
        return None

    def get_plot_layer_count(self) -> int:
        return len(self.plot_layers) 
        
    def set_marker(self, x: float | list[float], y: float | list[float]):
        if isinstance(x, float):
            self.plt_marker.setData(x=[x],y=[y])            
        else:
            self.plt_marker.setData(x=x,y=y)            

    def clear_marker(self):
        self.plt_marker.setData(x=[],y=[])   

    # implementation -------------------------------------------------

    def _show_title(self, title: str):
        self.plot.setTitle(title=title, size=f"{self.titlesize}px")

    def _show_label(self, axis:Axis):
        self.plot.setLabel(axis.value, text=f'<span style="font-size:{self.labelsize}pt">{self.axis_text[axis.value].name}</span>', units=self.axis_text[axis.value].unit)

    def _create_marker(self):
        self.plt_marker = self.plot.plot(pen=color_nsf_second_line, symbol='+', symbolSize=15, ) 

    def _add_cross_hair_cursor(self):
        self.cursor_vLine = pg.InfiniteLine(angle=90, movable=False)
        self.cursor_hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plot.addItem(self.cursor_vLine, ignoreBounds=True)
        self.plot.addItem(self.cursor_hLine, ignoreBounds=True)
        self.cursor_vLine.setPos(-1000)
        self.cursor_hLine.setPos(-1000)
        
    def _move_cross_hair_cursor(self, event):
        pos = event
        if self.plot.sceneBoundingRect().contains(pos):
            mousePoint = self.view_box.mapSceneToView(pos)
            x = mousePoint.x()
            y = mousePoint.y()
            self.cursor_vLine.setPos(x)
            self.cursor_hLine.setPos(y)

            if self.logmode_x:
                x = 10**x
            if self.logmode_y:
                y = 10**y
            x_unit =self.plot.getAxis(NSFChart.Axis.bottom.value).labelUnits
            y_unit =self.plot.getAxis(NSFChart.Axis.left.value).labelUnits
            self._show_title(f"x={fn.siFormat(x,suffix=x_unit, precision=3)} y={fn.siFormat(y,suffix=y_unit, precision=3)}")

    def _mouse_left_event_handler(self, event):
        self._show_title(self.plot_title)
        self._clear_cross_hair_cursor()

    def _clear_cross_hair_cursor(self):
        self.cursor_vLine.setPos(-1000)
        self.cursor_hLine.setPos(-1000)
                           

class NSFColormap(pg.GraphicsLayoutWidget):

    class Axis(enum.Enum):
        bottom = "bottom"
        left = "left"
        right = "right"
        top = "top"
        z = "z"

    class AxisText:
        def __init__(self, name: str = "", unit: str = ""):
            self.name = name
            self.unit = unit

    def __init__(self, title: str = "Colormap Plot", logmodex: bool = False, logmodey: bool = False, labelsize: int = 14, titlesize: int = 16):
        pg.GraphicsLayoutWidget.__init__(self)
        self.label_size = labelsize
        self.title_size = titlesize
        self.logmode_x = logmodex 
        self.logmode_y = logmodey  
        self.axis_text = {axis_name: NSFColormap.AxisText() for axis_name, _ in NSFColormap.Axis.__members__.items()} 

        self.data_points = (0,0)
        self.data_matrix = np.array([], ndmin=2)    
 
        font = QtGui.QFont()
        font.setPixelSize(self.label_size)

        self.plot = self.addPlot()
        self.plot.setLogMode(self.logmode_x, self.logmode_y)
        self.plot.getAxis(NSFColormap.Axis.bottom.value).tickFont = font
        self.plot.getAxis(NSFColormap.Axis.bottom.value).setStyle(tickTextOffset = 3, tickLength = 5)
        self.plot.getAxis(NSFColormap.Axis.left.value).tickFont = font
        self.plot.getAxis(NSFColormap.Axis.left.value).setStyle(tickLength = 5)

        self.colormap = pg.ImageItem()
        self.plot.addItem(self.colormap)
        self.plot.invertY(False)

        self.set_title(title)
        self._add_cross_hair_cursor()
        self.colormap.hoverEvent = self._move_cross_hairs
        self.set_label(NSFColormap.Axis.bottom, "X-Axis")
        self.set_label(NSFColormap.Axis.left, "Y-Axis")
        self._show_title(self.plot_title)
        self.histogram = pg.HistogramLUTWidget()
        self.histogram.setImageItem(self.colormap)
        self.histogram.gradient.loadPreset('spectrum')
        self.histogram.hide()

        self.setMinimumHeight(200)
        self.setMinimumWidth(200)

    def set_label(self, axis: Axis, label: str):
        self.axis_text[axis.value].name = label
        self._show_label(axis)

    def set_unit(self, axis: Axis, unit: str):
        self.axis_text[axis.value].unit = unit
        self._show_label(axis)

    def set_title(self, title: str):
        self.plot_title = title
        self._show_title(self.plot_title)

    def set_range_x(self, left:float, right:float):
        if self.logmode_x:
            self.plot.setXRange(np.log10(left), np.log10(right))
        else:
            self.plot.setXRange(left, right)

    def set_range_y(self, bottom:float, top:float):
        if self.logmode_x:
            self.plot.setYRange(np.log10(bottom), np.log10(top))
        else:
            self.plot.setYRange(bottom, top)
    
    def set_log_mode_x(self, log_mode:bool = True):
        self.logmode_x = log_mode
        self.plot.setLogMode(self.logmode_x, self.logmode_y)

    def set_log_mode_y(self, log_mode:bool = True):
        self.logmode_y = log_mode
        self.plot.setLogMode(self.logmode_x, self.logmode_y)


    def set_data_points(self, x: int, y: int):
        """ Defines the number of data points of the 2D matrix
            With this the matrix of data to show is defined.
            Update of the matrix is done by the plot_xxxxx() functions
        """
        self.data_points = (x,y)
        xx , _ = np.meshgrid(np.zeros(x), np.zeros(y), indexing='ij')
        self.data_matrix = xx

    def set_xy_range(self, x: np.ndarray, y:np.ndarray):
        """ Defines the x/y range for the matrix in physical units

        Parameters
        ----------
        x, y: ndarray
            in these arrays the range of each axis is defined.
            The min and max values are used to define the left/right or bottom/top values of the axes
            So, the array content can be just two values [min, max] or a full stream of data of any length
        """
        # prepare ImageItem transformation:
        left   = np.min(x)
        right  = np.max(x)
        bottom = np.min(y)
        top    = np.max(y)
        
        tr = QtGui.QTransform()  
        tr.rotate(90.0)
        tr.scale(+1.0*(right - left)/len(x), -1.0*(top - bottom)/len(y))  # scale horizontal and vertical axes
        self.colormap.setTransform(tr)
        
        self.set_range_x(left, right)
        self.set_range_y(bottom, top)

        self.colormap.setPos(left,bottom)

    def plot_data_point(self, x_pos: int, y_pos: int, value: float):
        """ Update a single point in the matrix at x/y
        
        Parameters
        ----------
        x,y: int
            Coordinate in the matrix of the point. 
            (0,0) is at bottom, left
            (max_x, max_y) is at top/right of the colormap
        value: float
            The value of the data point at (x,y)
        """
        self.data_matrix[y_pos][x_pos] = value
        self.colormap.setImage(self.data_matrix)

    def plot_data_line(self, data_line: np.ndarray, y_pos: int):
        """ Update a single row in the matrix at (y)
        
        Parameters
        ----------
        y_pos: int
            Y-Coordinate in the matrix of the point. 
            (0) is at bottom, (max_y) is at top of the colormap
        data_line: ndarray
            Array of values to The value of the data point at (x,y)
        """
        self.data_matrix[y_pos] = data_line
        self.colormap.setImage(self.data_matrix)

    def plot_channel(self, channel: sci_channel.SciChannel, y_pos: int):
        if y_pos >= 0 :
            self.data_matrix[y_pos] = channel.value
            self.colormap.setImage(self.data_matrix)
            self.set_unit(NSFColormap.Axis.left, channel.unit)         

    def plot_matrix(self, xy: np.ndarray):
        self.data_matrix = xy
        self.colormap.setImage(self.data_matrix)

    # Implementation ------------------------------------

    def _show_title(self, title: str):
        self.plot.setTitle(title = title, size = f"{self.title_size}px")

    def _show_label(self, axis:Axis):
        if axis != NSFColormap.Axis.z:
            self.plot.setLabel(axis.value, text=f'<span style="font-size:{self.label_size}pt">{self.axis_text[axis.value].name}</span>', units=self.axis_text[axis.value].unit)

    def _add_cross_hair_cursor(self):
        self.cursor_vLine = pg.InfiniteLine(angle=90, movable=False)
        self.cursor_hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plot.addItem(self.cursor_vLine, ignoreBounds=True)
        self.plot.addItem(self.cursor_hLine, ignoreBounds=True)
        self.cursor_vLine.setPos(-1000)
        self.cursor_hLine.setPos(-1000)
            
    def _move_cross_hairs(self, event):
        if event.isExit():
            self._show_title(self.plot_title)
            self.cursor_vLine.setPos(-1000)
            self.cursor_hLine.setPos(-1000)
            return

        pos = event.pos()
        i, j = pos.y(), pos.x()
        i = int(np.clip(i, 0, self.colormap.image.shape[0] - 1)) # xpixel
        j = int(np.clip(j, 0, self.colormap.image.shape[1] - 1)) # ypixel
        val = self.colormap.image[j, i]
        ppos = self.colormap.mapToParent(pos)
        x, y = ppos.x(), ppos.y()
        self.cursor_vLine.setPos(x)
        self.cursor_hLine.setPos(y)

        x_unit = self.plot.getAxis(NSFColormap.Axis.bottom.value).labelUnits
        y_unit = self.plot.getAxis(NSFColormap.Axis.left.value).labelUnits
        z_unit = self.axis_text[NSFColormap.Axis.z.value].unit
        self.set_title( 
            f"x={fn.siFormat(x,suffix=x_unit, precision=3)}, y={fn.siFormat(y,suffix=y_unit, precision=3)}, z={fn.siFormat(val,suffix=z_unit,precision=3)}",\
        )


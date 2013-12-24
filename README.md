QPlotWidget
===========

A simple widget for plotting. Example usage can be found in the main function of QPlotWidget.py.

The widget is created used the empty constructor QPlotWidget(). Each QPlotWidget contains a single axis. The view area of the axis is set by specifying the lower left and upper right corners: setAxisView(x_coord_lower_left, y_coord_lower_left, x_coord_upper_right, y_coord_upper_right). The view area can be changed at any time. The only other option for the axis currently implement is turning the numbering labels or off. To turn the numbering labels off, use:
    qPlotWidgetInstance.axis.axisTextEnabled = False
    qPlotWidgetInstance.axis.update()

An arbitrary number of plots can be added to a given QPlotWidget. A plot is created by calling the Plot constructor with the instance of QPlotWidget:
    sinPlot = Plot(qPlotWidgetInstance)

There are also several options that can be changed for the plot:
	# Set the size of the marker in pixels
    sinPlot.setMarkerSize(markerSizeInPixels)

    # Set the color of the line and the marker
    sinPlot.setColor(QtGui.QColor(255,0,0))

    # Set the marker type to either circles or nothing (more options to be added later)
    sinPlot.setMarkerType('none')
    sinPlot.setMarkerType('circ')

    # WARNING: The following options will only be applied to points added after the change is made. The previous options work for all points in the plot

    # Set to no fill in the marker
    sinPlot.setFilled(False)

    # Change the line weight in pixels (3 pixels here)
    sinPlot.setLineWeight(3)

    # The line is not a continuous line, but is definied between each pair of consecutive points. Thus, the dash pattern restarts after each pair.
    # Set the dash pattern of the line to dotted
    sinPlot.setDashPattern(QtGui.Qt.DotLine)

To add points, use plotInstance.addPoint([x,y]). A line will be drawn between each pair of consecutive points:

	# Draws a sin between -5 and 5
    for x in range(200):
		xPos = (x - 500/5)/(100.0/5)
		sinPlot.addPoint([xPos, math.sin(xPos)])

The performance is not great, so it is best to limit plots to around 1000 point if there is going to be a lot of resizing or the widget.
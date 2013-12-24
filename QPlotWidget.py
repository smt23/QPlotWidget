import sys
from PySide import QtGui, QtCore
from PySide.QtCore import QRectF as Rect
import math

# Represents a set of x,y coordinates to be plotted
class Plot():

	def updateBrush(self):
		if self.filled:
			self.mBrush = QtGui.QBrush(self.color)
		else:
			self.mBrush = QtGui.QBrush()

		self.mPen = QtGui.QPen(QtGui.QBrush(self.color), 1)
		self.mPen.setCosmetic(True)

		self.lPen = QtGui.QPen(QtGui.QBrush(self.color), self.lineWeight)
		self.lPen.setCosmetic(True)		

	def __init__(self,plotWidget):

		self.scene = plotWidget.scene()
		self.gView = plotWidget
		self.axis = plotWidget.axis
		self.gWindow = plotWidget

		self.pointObjects = []
		self.lineObjects = []
		self.markerSize = 8 # Size in pixels
		self.markerType = 'circ'
		self.color = QtGui.QColor(0,0,0)
		self.filled = True
		self.lineWeight = 1
		self.mPen = None
		self.mBrush = None
		self.lPen = None
		self.dashPattern = QtCore.Qt.SolidLine # Also DashLine, DotLine, DashDotLine, DashDotDotLine

		# Initial brush
		self.updateBrush()

		# Add self to the list of plots in the graphView
		self.gWindow.addPlot(self)

	# Adds a marker for point p
	def addMarker(self,p):

		if self.markerType == 'circ':
			xsize = (self.axis.rect.width()/self.gView.size().width())/(1.0/self.markerSize)
			ysize = (self.axis.rect.height()/self.gView.size().height())/(1.0/self.markerSize)
			self.pointObjects.append([p,self.scene.addEllipse(p[0] - xsize/2, p[1] - ysize/2, xsize, ysize,self.mPen,self.mBrush)])
		else:
			self.pointObjects.append([p,None])

	def addPoint(self,p):
		self.addMarker(p)

		if len(self.pointObjects) > 1:
			prevp = self.pointObjects[-2][0]
			self.lineObjects.append(self.scene.addLine(prevp[0],prevp[1],p[0],p[1],self.lPen))

	# This needs to be called any time there is a resize or a change to the axes
	# Make faster by only updating attributes?
	def redraw(self):

		self.updateBrush()

		if self.markerType == 'circ':
			xsize = (self.axis.rect.width()/self.gView.size().width())/(1.0/self.markerSize)
			ysize = (self.axis.rect.height()/self.gView.size().height())/(1.0/self.markerSize)

			for po in self.pointObjects:
				p = po[0]
				m = po[1]
				m.setRect(p[0] - xsize/2, p[1] - ysize/2, xsize, ysize)

	def setMarkerSize(self,mSize):
		self.markerSize = mSize
		self.redraw()

	def setColor(self,color):
		self.color = color
		self.redraw()

	# This is slow because it needs to rebuild the pointObjects list
	def setMarkerType(self,mType):
		self.markerType = mType

		# Precalculate xsize, ysize in case they are needed
		xsize = (self.axis.rect.width()/self.gView.size().width())/(1.0/self.markerSize)
		ysize = (self.axis.rect.height()/self.gView.size().height())/(1.0/self.markerSize)

		for po in self.pointObjects:
			if len(po) > 1:
				self.scene.removeItem(po[1])

			if self.markerType == 'circ':
				po[1] = self.scene.addEllipse(p[0] - xsize/2, p[1] - ysize/2, xsize, ysize,self.mPen,self.mBrush)
			else:
				po[1] = None


		self.redraw()

	def setFilled(self,filled):
		self.filled = filled
		self.redraw()

	# Line weight is in pixels
	def setLineWeight(self,lWeight):
		self.lineWeight = lWeight
		self.redraw()

	def setLineDashPattern(self,dashp):
		self.dashPattern = dashp
		self.redraw()


class Axis():

	# Rect holds the bounding box for the view of the graph
	rect = None

	# A list of the objects that axes has in the scene
	sceneObjects = None

	# Determines whether the axis text is drawn
	axisTextEnabled = True

	# Tick marks
	numXAxisMajor = 5
	numYAxisMajor = 5

	# Creates and draws the axes objects for the current view
	# Initially zoomed on a 2x2 view centered at 0,0
	def __init__(self,graphicsView):
		self.scene = graphicsView.scene()
		self.gView = graphicsView
		self.rect = Rect(-1,1,2,2)
		self.update()

	# Updates the transform so the axes draw the given rect
	def setAxisView(self, rect):
		self.rect = rect
		self.update()

	# Should be called any time the view is scaled or updated
	def update(self):

		# Update the scaling based on the viewport size
		self.xScale = self.gView.size().width()/self.rect.width()
		self.yScale = self.gView.size().height()/self.rect.height()

		if self.sceneObjects is not None:
			for o in self.sceneObjects:
				self.scene.removeItem(o)

		self.sceneObjects = []
		
		r = self.rect

		# Add the lines
		# Is x = 0 in the current view?
		if r.left() < 0 and r.right() > 0:
			self.sceneObjects.append(self.scene.addLine(0,r.bottom(),0,r.top()))
			yaLoc = 0
		# Otherwise, add the line in the middle of the view
		else:
			self.sceneObjects.append(self.scene.addLine(r.center().x(),r.bottom(),r.center().x(),r.top()))
			yaLoc = r.center().x()

		# Is y = 0 in the current view? Note that top and bottom are reversed, due to -1 transform
		if r.top() < 0 and r.bottom() > 0:
			self.sceneObjects.append(self.scene.addLine(r.left(),0,r.right(),0))
			xaLoc = 0
		# Otherwise, add the line in the middle of the view
		else:
			self.sceneObjects.append(self.scene.addLine(r.left(),r.center().y(),r.right(),r.center().y()))
			xaLoc = r.center().y()

		# Draw the tick marks
		xaMajSpacing = 0
		mult = 1.0
		while xaMajSpacing == 0:
			xaMajSpacing = math.floor(mult*r.width()*1.0/(self.numXAxisMajor+1))/mult
			mult *= 10.0

		yaMajSpacing = 0
		mult = 1.0
		while yaMajSpacing == 0:
			yaMajSpacing = math.floor(mult*r.height()*1.0/(self.numYAxisMajor+1))/mult
			mult *= 10.0

		x = -xaMajSpacing + yaLoc
		while x > r.left():
			self.sceneObjects.append(self.scene.addLine(x, xaLoc - 5/self.yScale, x, xaLoc + 5/self.yScale))
			if self.axisTextEnabled:
				self.addText(str(x), x, xaLoc - 6/self.yScale, alignTop = True)
			x -= xaMajSpacing

		x = xaMajSpacing + yaLoc
		while x < r.right():
			self.sceneObjects.append(self.scene.addLine(x, xaLoc - 5/self.yScale, x, xaLoc + 5/self.yScale))
			if self.axisTextEnabled:
				self.addText(str(x), x, xaLoc - 6/self.yScale, alignTop = True)
			x += xaMajSpacing				

		y = -yaMajSpacing + xaLoc
		while y > r.top():
			self.sceneObjects.append(self.scene.addLine(-5/self.xScale + yaLoc, y, 5/self.xScale + yaLoc, y))
			if self.axisTextEnabled:
				self.addText(str(y), yaLoc + 7.5/self.xScale, y, alignLeft = True)
			y -= yaMajSpacing

		y = yaMajSpacing + xaLoc
		while y < r.bottom():
			self.sceneObjects.append(self.scene.addLine(-5/self.xScale + yaLoc, y, 5/self.xScale + yaLoc, y))
			if self.axisTextEnabled:
				self.addText(str(y), yaLoc + 7.5/self.xScale, y, alignLeft = True)
			y += yaMajSpacing				

	# Adds text centered at x and y
	def addText(self, text, x, y, alignLeft = False, alignTop = False):
		t = self.scene.addText(text)

		# Undo transform
		t.setTransform(t.transform().scale(1/self.xScale,-1/self.yScale))

		tR = t.sceneBoundingRect()
		if not alignLeft:
			xLoc = x - tR.width()/2
		else:
			xLoc = x

		if not alignTop:
			yLoc = y + tR.height()/2
		else:
			yLoc = y


		r = self.rect
		if xLoc < r.left():
			xLoc = r.left()
		elif xLoc + tR.width() > r.right():
			xLoc = r.right() - tR.width()

		if yLoc < r.top():
			yLoc = r.top()
		elif yLoc - tR.height() > r.bottom():
			yLoc = r.bottom() - tR.height()

		t.setPos(xLoc, yLoc)

		self.sceneObjects.append(t)

	# Get the actual pixel coordinates of the given position
	def getPixelCoords(self, pos):
		p = [(pos[0] - self.rect.left()) * self.xScale, (pos[1] - self.rect.top()) * self.yScale]
		return p

	# Returns the correct transform to use in the GraphWindow QGraphicsView
	def getTransform(self):

		self.update()

		t = QtGui.QTransform(1,0,0,-1,0,0)
		t.scale(self.xScale,self.yScale)
		return t

	# Returns the center of the view (call on the QGraphicsView centerOn)
	def getCenter(self):
		return self.rect.center()

class QPlotWidget(QtGui.QGraphicsView):

	axis = None
	gView = None
	plots = []

	# For now, just a test of the graphicsscene, graphicsview
	def initUI(self):

		# Create a scene, this must be done before creating the axis
		self.gScene = QtGui.QGraphicsScene()
		self.gScene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
		self.setScene(self.gScene)

		# Add the axis
		self.axis = Axis(self)
		self.axis.setAxisView(Rect(-1,-1,2,2))

		# Create the QGraphicsView
		self.setVisible(True)

		# Disable the scroll bars
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

	# lower left x, lower left y, upper right x, upper right y
	def setAxisView(self, ll_x, ll_y, ur_x, ur_y):
		r =	Rect(ll_x, ll_y, ur_x - ll_x, ur_y - ll_y)
		self.axis.setAxisView(r)
		self.setTransform(self.axis.getTransform())
		self.centerOn(self.axis.getCenter())

		for pl in self.plots:
			pl.redraw()

	# Should not be called directly
	def addPlot(self, plot):
		if plot in self.plots:
			return

		self.plots.append(plot)

	# resizeEvent handler
	def resizeEvent(self, event):

		# Update the axes
		self.setTransform(self.axis.getTransform())
		self.centerOn(self.axis.getCenter())

		for pl in self.plots:
			pl.redraw()

		super(QPlotWidget, self).resizeEvent(event)

	def __init__(self):
		super(QPlotWidget,self).__init__()
		self.initUI()

def main():
	app = QtGui.QApplication(sys.argv)

	mainWindow = QtGui.QWidget()
	mainWindow.setGeometry(25,100,800,600)
	mainWindow.setWindowTitle('QPlotWidget Demo')
	grid = QtGui.QGridLayout()
	mainWindow.setLayout(grid)

	# Create the QPlotWidget
	graph = QPlotWidget()
	#graph.axis.axisTextEnabled = False

	grid.addWidget(graph,0,0,1,1)
	mainWindow.show()


	# Plot sin(x), cos(x), -sin(x), -cos(x)
	sPlot = Plot(graph)
	cPlot = Plot(graph)
	nsPlot = Plot(graph)
	ncPlot = Plot(graph)
	cPlot.setColor(QtGui.QColor(255,0,0))
	nsPlot.setColor(QtGui.QColor(0,0,255))
	ncPlot.setColor(QtGui.QColor(0,255,0))
	sPlot.setLineWeight(2)
	ncPlot.setLineWeight(3)
	nsPlot.setLineWeight(4)
	for x in range(200):
		xPos = (x - 500/5)/(100.0/5)
		sPlot.addPoint([xPos, math.sin(xPos)])
		cPlot.addPoint([xPos, math.cos(xPos)])
		ncPlot.addPoint([xPos, -math.cos(xPos)])
		nsPlot.addPoint([xPos, -math.sin(xPos)])


	graph.setAxisView(-5,-1.5,5,1.5)

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
multiKinect = True

import viz
import vizshape
import vizact

if multiKinect:
	import MultiKinectInterface

viz.go()
world = vizshape.addGrid()
world.setPosition([0, -.8, 0])

HEAD_INDEX = 3
RIGHT_HAND_INDEX = 11

sensor = MultiKinectInterface.MultiKinectSensor()

viz.MainView.setPosition(0, -.5, -5)

skeleton = []
numPoints = 20
col = viz.BLUE
for i in range(0, numPoints):
	sphere = vizshape.addSphere(radius = 0.1, color = col)
	skeleton.append(sphere)

def checkGesture():
	sensor.refreshData()
	skeletonData = sensor.getTrackedSkeleton(0,0)
	if skeletonData != None:
		for i in range(0, numPoints):
			skeleton[i].visible(viz.ON)
			point = skeletonData[i]
			skeleton[i].setPosition(point)
		if skeletonData[RIGHT_HAND_INDEX][1] > skeletonData[HEAD_INDEX][1]:
			world.playsound("kick5.wav")
	else:
		for i in range(0, numPoints):
			skeleton[i].visible(viz.OFF)

def setKinectAngle(angle):
    viz.director(sensor.setKinectElevation, 0, angle)
    print sensor.getKinectElevation(0)

vizact.onkeydown(viz.KEY_ESCAPE, sensor.shutdownKinect)
vizact.onkeydown('w', setKinectAngle, 5)
vizact.onkeydown('s', setKinectAngle, 0)
vizact.onkeydown('x', setKinectAngle, -5)
vizact.onupdate(0, checkGesture)
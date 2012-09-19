import viz
import vizshape
import vizact
import MultiKinectInterface

viz.go()
world = vizshape.addGrid()
#world = viz.addChild("Z:\Environments HD\environments\Cavern gallery.IVE")
world.setPosition([0, -.8, 0])

sensor = MultiKinectInterface.MultiKinectSensor()

viz.MainView.setPosition(0, -.5, -5)

pointNames = ["Hip center",
    "Spine",
    "Shoulder center",
    "Head",
    "Left shoulder",
    "Left elbow",
    "Left wrist",
    "Left hand",
    "Right shoulder",
    "Right elbow",
    "Right wrist",
    "Right hand",
    "Left hip",
    "Left knee",
    "Left ankle",
    "Left foot",
    "Right hip",
    "Right knee",
    "Right ankle",
    "Right foot"]

trackingStrings = ["Lost track of ", "Inferring ", "Tracking "]

currentTracking = []
for i in range(20):
    currentTracking.append(0)
    


#TOD: Did not have a chance to test my changes because the lab was being used for a demo.

skeletons = []
for j in range (0, 2):
    skeletons.append([])
    numPoints = 20
    if j >= 2: numPoints = 1
    for i in range(0, numPoints):
        if j == 0: 
            col = viz.BLUE
        elif j == 1:
            col = viz.RED
        elif j == 2:
            col = viz.GREEN
        elif j == 3:
            col = viz.YELLOW
        elif j == 4:
            col = viz.PURPLE
        else:
            col = viz.ORANGE
        sphere = vizshape.addSphere(radius = 0.1, color = col)
        skeletons[j].append(sphere)

def renderMan():
    sensor.refreshData()
    kinectTimeStamp = sensor.getKinectTimeStamp(0)
    #print (kinectTimeStamp / 1000.0)
    for j in range (0,2):
        skeletonData = sensor.getTrackedSkeleton(0, j)
        numPoints = 20
        if j >= 2: numPoints = 1
        if skeletonData != None:
            #print skeletonData
            
            temp = sensor.getTrackedSkeletonNums(0)
            skelNum = temp[0]
                
            for i in range(0, numPoints):
                skeletons[j][i].visible(viz.ON)
                point = skeletonData[i]
                skeletons[j][i].setPosition(point)
                
                if currentTracking[i] != sensor.getPointTrackingValue(0, skelNum, i):
                    currentTracking[i] = sensor.getPointTrackingValue(0, skelNum, i)
                    if i == MultiKinectInterface.KINECT_HAND_LEFT:
                        print trackingStrings[currentTracking[i]] + pointNames[i]
                
        else:
            for i in range(0, numPoints):
                skeletons[j][i].visible(viz.OFF)

def setKinectAngle(angle):
    viz.director(sensor.setKinectElevation, 0, angle)
    print sensor.getKinectElevation(0)


vizact.onkeydown(' ', sensor.shutdownKinect)
vizact.onkeydown('w', setKinectAngle, 5)
vizact.onkeydown('s', setKinectAngle, 0)
vizact.onkeydown('x', setKinectAngle, -5)
vizact.ontimer(0, renderMan)


#renderMan()
#sensor.shutdownKinect()

#now add all trackers and link a shape to it
'''for i in range(0, 20):
    t = vrpn.addTracker( 'Tracker0@localhost',i )
    s = vizshape.addSphere(radius=.1)
    l = viz.link(t,s)
    trackers.append(t)
    links.append(l)
    shapes.append(s)'''

""" 
NOTE TO JIMMY:
	
The Kinect demo seems not to run. It gave the following error message:
	
Traceback (most recent call last):
  File "<string>", line 11, in ?
  File "MultiKinectModuleTest.py", line 4, in ?
    import MultiKinectInterface
  File "MultiKinectInterface.py", line 1, in ?
    ï»¿import MultiKinect
ImportError: DLL load failed: A dynamic link library (DLL) initialization routine failed.

- Evan
"""
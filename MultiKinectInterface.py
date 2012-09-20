import MultiKinect

# These constants reflect constants exported by the Kinect SDK include file "MSR_NuiSkeleton.h".
# There are 2 fields of data beyond the index of the last skeleton point, but these record tracking
# state information and positional data respectively.
#
# USAGE:
# To get the x-y-z coordinates of a skeleton node, the following notation is used:
# 	skeleton = KinectInterface.getTrackedSkeleton(0)
# 	hip = skeleton[KinectInterface.KINECT_HIP_CENTER]
KINECT_HIP_CENTER = 0
KINECT_SPINE = 1
KINECT_SHOULDER_CENTER = 2
KINECT_HEAD = 3
KINECT_SHOULDER_LEFT = 4
KINECT_ELBOW_LEFT = 5
KINECT_WRIST_LEFT = 6
KINECT_HAND_LEFT = 7
KINECT_SHOULDER_RIGHT = 8
KINECT_ELBOW_RIGHT = 9
KINECT_WRIST_RIGHT = 10
KINECT_HAND_RIGHT = 11
KINECT_HIP_LEFT = 12
KINECT_KNEE_LEFT = 13
KINECT_ANKLE_LEFT = 14
KINECT_FOOT_LEFT = 15
KINECT_HIP_RIGHT = 16
KINECT_KNEE_RIGHT = 17
KINECT_ANKLE_RIGHT = 18
KINECT_FOOT_RIGHT = 19

KINECT_SKELETON_POSITION = 20
KINECT_TRACKING_STATE = 21

KINECT_TRACKING_STATE_TRACKED = 0

# These exported constants are based on the NUI_SKELETON_POSITION_TRACKING_STATE enum type defined in MSR_NuiSkeleton.h
KINECT_POINT_NOT_TRACKED = 0
KINECT_POINT_INFERRED = 1
KINECT_POINT_TRACKED = 2

# This value is set to 6 because the beta Kinect SDK allows for 6 active skeletons (only 2 tracked)
KINECT_NUM_SKELETONS = 6

class MultiKinectSensor:
	def __init__(self):
		initData = MultiKinect.initKinects()
		self.availableKinects = initData[0]

		self.skeletonData = []
		self.skeletonPointData = []
		self.kinectTimeStamp = []
		for i in range(self.availableKinects):
			self.skeletonData.append([])
			self.skeletonPointData.append([])
			self.kinectTimeStamp.append([])

		print "Initializing " + str(self.availableKinects) + " Kinects..."
		if initData[1]:
			print "UNABLE TO CREATE ALL KINECT INSTANCES."
		else:
			print "Kinect instances created."
		if initData[2]:
			print "INITIALIZATIONS FAILED."
		else:
			print "Initialization success."
		if initData[3]:
			print "SKELETON ENABLING FAILED."
		else:
			print "Skeletons enabled."
		if initData[4]:
			print "UNABLE TO OPEN DEPTH STREAM."
		else:
			print "Depth streams open."

	def refreshData(self):
		for i in range(self.availableKinects):
			totalData = MultiKinect.getNextSkeletonFrameFromKinectAtIndex(i)
			if totalData != None:
				self.skeletonData[i] = totalData[0]
				self.skeletonPointData[i] = totalData[1]
				self.kinectTimeStamp[i] = totalData[2]

	def skeletonIsActive(self, kinectNum, skelNum):
		if kinectNum >= self.availableKinects:
			return False
		if skelNum >= KINECT_NUM_SKELETONS:
			return False
		if self.skeletonData[kinectNum][skelNum] != None:
			return True
		else:
			return False

	def skeletonIsTracked(self, kinectNum, skelNum):
		if kinectNum >= self.availableKinects:
			return False
		if skelNum >= KINECT_NUM_SKELETONS:
			return False
		# NOTE: The next if statement is a hacked fix
		if self.skeletonData[kinectNum] == []:
			return False
		if self.skeletonData[kinectNum][skelNum] != None:
			if self.skeletonData[kinectNum][skelNum][KINECT_TRACKING_STATE][KINECT_TRACKING_STATE_TRACKED] != 0:
				return True
		else:
			return False

	def getSkeletonPos(self, kinectNum, skelNum):
		if kinectNum >= self.availableKinects:
			return None
		if not self.skeletonIsActive(skelNum):
			return None
		else:
			return self.skeletonData[kinectNum][skelNum][KINECT_SKELETON_POSITION]

	def getActiveSkeletonNums(self, kinectNum):
		if kinectNum >= self.availableKinects:
			return None
		activeNums = []
		for i in range(KINECT_NUM_SKELETONS):
			if self.skeletonIsActive(kinectNum, i):
				activeNums.append(i)
		return activeNums

	def getTrackedSkeletonNums(self, kinectNum):
		if kinectNum >= self.availableKinects:
			return None
		trackedNums = []
		for i in range(KINECT_NUM_SKELETONS):
			if self.skeletonIsTracked(kinectNum, i):
				trackedNums.append(i)
		return trackedNums

	def getTrackedSkeleton(self, kinectNum, trackedSkelIndex):
		validNums = self.getTrackedSkeletonNums(kinectNum)
		if (validNums == None) or (len(validNums) <= trackedSkelIndex):
			return None
		else:
			return self.skeletonData[kinectNum][validNums[trackedSkelIndex]]

	def shutdownKinect(self):
		MultiKinect.shutDownKinects()
		#for testing
		print "Shuting down Kinects..."

	def setKinectElevation(self, kinectNum, elevation):
		if kinectNum >= self.availableKinects:
			return False
		else:
			MultiKinect.setKinectElevationAngle(kinectNum, elevation)
			return True

	def getKinectElevation(self, kinectNum):
		if kinectNum >= self.availableKinects:
			return None
		else:
			return MultiKinect.getKinectElevationAngle(kinectNum)

	def getPointTrackingValue(self, kinectNum, skeletonIndex, pointIndex):
		if kinectNum >= self.availableKinects:
			return None
		elif pointIndex > KINECT_FOOT_RIGHT or pointIndex < 0:
			return None
		elif not self.skeletonIsTracked(kinectNum, skeletonIndex):
			return None
		else:
			return self.skeletonPointData[kinectNum][skeletonIndex][pointIndex]

	def getKinectTimeStamp(self, kinectNum):
		if kinectNum >= self.availableKinects:
			return None
		else:
			return self.kinectTimeStamp[kinectNum]

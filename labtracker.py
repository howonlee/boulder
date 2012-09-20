##########################
# Tracker for new lab    #
# Oliver Castaneda 2011  #
##########################
#
#Set the DEFAULT_OFFSET, DEFAULT_EULER, and DEFAULT_SCALE to match
#your world if the origin of your world does not
#correspond to the PPT tracking system origin.
#
# Using the tracking system:
#	from labTracker import *
#   tracking = viz.get(viz.TRACKER)
#	if(tracking):
#		Tracking = labTracker()
#		Tracking.setPosition(startPosition)
#
##################################################

import nvis
import viz

DEFAULT_OFFSET = [0,0,0]
#DEFAULT_OFFSET = [1.5,2,0]
DEFAULT_EULER = [180,0,0]#edit here
#DEFAULT_SCALE = [1.5,1,1]
PPT_HOSTNAME = '171.64.33.43'

class labTracker(object):
	def __init__(self):
		viz.mouse.setVisible(viz.OFF)
		#Activate NVIS HMD
		#nvis.nvisorSX111()
		nvis.nvisorSX60()
		viz.cursor(viz.OFF)
		#isense = viz.add('intersense.dls')
		self.posLink = headPos
		self.headMarker = headMarker

	#get position in world (absolute) coordinates of 0 marker (head marker)
	def getPosition(self):
		return [0, 0, 0]
	#get position of any marker 1,2,3...
	def getMarkerPosition(self, markerID):
		trk = self.markers[markerID-1].getPosition()
		off = self.posLink.getOffset()
		return [trk[0]+off[0], trk[1]+off[1], trk[2]+off[2]]

	#set absolute location
	def setPosition(self, pos):
		trk = self.headMarker.getPosition()
		self.posLink.setOffset([pos[0]-trk[0], pos[1]-trk[1], pos[2]-trk[2]])
	#set the ground height to absolute y
	def setGround(self, y):
		off = self.posLink.getOffset()
		off[1] = y
		self.posLink.setOffset(off)
	def getGround(self):
		off = self.posLink.getOffset()
		return off[1]
	def reset(self):
		self.posLink.setOffset(DEFAULT_OFFSET)



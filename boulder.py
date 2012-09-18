import viz
import vizact
import vizproximity
import viztask
import vizinput
import vizinfo
#import vizsonic
#from labtracker import *

class BoulderScene:
	def __init__(self):
		'''initialize. note that TAKEDATA is the option to take orientation, position data'''
		viz.go(viz.PROMPT)
		#options
		self.TAKEDATA = True
		#init objects
		self.sky = viz.add("sky_night.osgb")
		self.start_time = viz.tick()
		self.count = 0
		self.data = ""
		self.boulder_data = open('boulder_data.txt', 'a')
		self.groundSetup()
		self.boulderSetup()
		#hmd init
		self.tracking = viz.get(viz.TRACKER)
		#init timers
		vizact.ontimer(0, self.draw)
		if (self.tracking):
			self.Tracking = labTracker()
			self.Tracking.setPosition(1,1,1)

	def groundSetup(self):
		self.ground = viz.add("ground_stone.osgb")
		self.ground.setScale(5, 5, 5)
		move = vizact.moveTo([0, 0, -100], time=20)
		self.ground.addAction(move)

	def boulderSetup(self):
		self.boulder = viz.add("boulder.dae")
		self.boulder.specular(0,0,0)
		self.boulder.color(0.3, 0.3, 0.3)
		self.boulder.setPosition(0, 4, 5)
		spin = vizact.spin(1, 0, 0, 300)
		#move = vizact.moveTo([0, 0, 100], time=20)
		#spinmove = vizact.parallel(spin, move)
		self.boulder.addAction(spin)

	def draw(self):
		self.count += 1
		if (self.count == 6 and self.TAKEDATA):
			self.getdata()
			self.count = 0

	def getdata(self):
		orientation = viz.MainView.getEuler()
		position = viz.MainView.getPosition()
		self.data = self.data + "euler: " + str(orientation) + '\tposition: ' + str(position) + "\ttime: " + str(viz.tick() - self.start_time) + '\n'
		self.boulder_data.write(self.data)
		self.boulder_data.flush()

if __name__ == "__main__":
	scene = BoulderScene()

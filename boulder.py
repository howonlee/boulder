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
		'''initialize. note that TAKEDATA is the option to take orientation, position data. Data file gets really big, really quickly.'''
		viz.go(viz.PROMPT)
		#options
		self.TAKEDATA = False
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

	def scrollGround(self):
		'''this starts the infinite loop of ground scrolling'''
		move = vizact.moveTo([0, 0, -100], time=20)
		self.ground.setPosition(0,0,0)
		scroll = vizact.call(self.scrollGround)
		self.ground.addAction(move)
		self.ground.addAction(scroll)

	def groundSetup(self):
		'''sets up a ground beneath main view and sets it to scroll'''
		self.ground = viz.add("ground_gray.osgb")
		self.ground.setScale(5, 5, 5)
		scroll = vizact.call(self.scrollGround)
		self.ground.addAction(scroll)

	def boulderSetup(self):
		'''sets up a boulder to roll eternally'''
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
		'''formats data and writes it in the file'''
		orientation = viz.MainView.getEuler()
		position = viz.MainView.getPosition()
		self.data = self.data + "euler: " + str(orientation) + '\tposition: ' + str(position) + "\ttime: " + str(viz.tick() - self.start_time) + '\n'
		self.boulder_data.write(self.data)
		self.boulder_data.flush()

if __name__ == "__main__":
	scene = BoulderScene()

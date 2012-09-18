import viz
import vizact
import vizproximity
import viztask
import vizinfo
#import vizsonic
#from labtracker import *

class BoulderScene:
	def __init__(self):
		viz.go(viz.PROMPT)
		#init objects
		self.ground = viz.add("ground.osgb")
		self.ground.setScale(5, 5, 5)
		self.ground.addAction(vizact.moveTo([0, 0, -100], time=20))
		self.boulderSetup()
		#hmd init
		self.tracking = viz.get(viz.TRACKER)
		#init timers
		vizact.ontimer(0, self.draw)
		if (self.tracking):
			self.Tracking = labTracker()
			self.Tracking.setPosition(1,1,1)
			
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
		pass
		
if __name__ == "__main__":
	scene = BoulderScene()
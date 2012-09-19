import viz
import vizact
import vizproximity
import viztask
import vizinput
import vizinfo
#import vizsonic #enable for proper ambisonic sound
#from labtracker import * #enable for lab tracker

class BoulderScene:
	def __init__(self):
		'''initialize. note that TAKEDATA is the option to take orientation, position data. Data file gets really big, really quickly.'''
		viz.go(viz.PROMPT)
		#options
		self.TAKEDATA = False
		#init constant things
		self.sky = viz.add("sky_night.osgb")
		self.start_time = viz.tick()
		#init for data
		self.count = 0 #used for taking data
		self.data = ""
		self.boulder_data = open('boulder_data.txt', 'a')
		#manager init
		self.manager = vizproximity.Manager()
		self.target = vizproximity.Target(viz.MainView)
		self.manager.addTarget(self.target)
		#setup objects
		self.groundSetup()
		self.treasureSetup()
		self.instruction1Setup()
		#setup behavior
		#self.screenText = viz.addText('blah', viz.SCREEN) #debug screentext
		#hmd init
		self.tracking = viz.get(viz.TRACKER)
		#init timers, callbacks
		vizact.onkeydown('d', self.manager.setDebug, viz.TOGGLE)
		vizact.onupdate(0, self.draw)
		if (self.tracking):
			self.Tracking = labTracker()
			self.Tracking.setPosition(0,0,0)
			
	def treasureTrigger(self, e):
		'''called when we approach the treasure. triggers all the other setups'''
		self.boulderSetup()
		self.avatarSetup()
		self.treasureCleanup()
		self.scrollGround()
		self.instruction2Setup()

	def scrollGround(self):
		'''this starts the infinite loop of ground scrolling'''
		move = vizact.moveTo([0, 0, -100], time=20)
		self.ground.setPosition(0,0,0)
		scroll = vizact.call(self.scrollGround)
		self.ground.addAction(move)
		self.ground.addAction(scroll)

	def groundSetup(self):
		'''sets up a ground beneath main view'''
		self.ground = viz.add("ground_gray.osgb")
		self.ground.setScale(10, 10, 10)
		
	def groundRoll(self):
		'''tells the ground to scroll like conveyor belt'''
		scroll = vizact.call(self.scrollGround)
		self.ground.addAction(scroll)

	def treasureSetup(self):
		'''make the treasure appear and setup the proximity stuff'''
		self.treasure = viz.add("./chalice12_lowpoly_3ds/kelch12_lowpolyn2.3ds")
		self.treasure.setPosition([0, 0, -15])
		self.treasure.setScale(10, 10, 10)
		self.treasuresensor = vizproximity.Sensor(vizproximity.Box([1, 5, 1], center=[0, 0, 0]), source=self.treasure)
		self.manager.addSensor(self.treasuresensor)
		self.manager.onEnter(self.treasuresensor, self.treasureTrigger)
		
	def treasureCleanup(self):
		self.treasure.visible(show = viz.OFF)

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

	def instruction1Setup(self):
		'''instructions for the first part of the game, taking the treasure'''
		self.info1 = vizinfo.add("There's probably treasure...")
		vizact.ontimer2(6, 0, self.info1.shrink)

	def instruction2Setup(self):
		'''instructions for the second part of the game, the running'''
		#just in case it takes less than 6 seconds
		self.info1.shrink()
		self.info2 = vizinfo.add("Run from the boulder!\nBut not literally!")
		vizact.ontimer2(10, 0, self.info2.shrink)
		
	def avatarSetup(self):
		'''sets up the avatar to be running eternally'''
		self.avatar1 = viz.addAvatar("vcc_male.cfg", pos=(0, 0, -5), euler=(180, 0, 0))
		self.avatar1.state(11)
		
	def draw(self):
		self.count += 1
		if (self.count == 6 and self.TAKEDATA):
			self.getdata()
			self.count = 0

	def getdata(self):
		'''formats data and writes it in the file. we must offload to another thread eventually.'''
		orientation = viz.MainView.getEuler()
		position = viz.MainView.getPosition()
		self.data = self.data + "euler: " + str(orientation) + '\tposition: ' + str(position) + "\ttime: " + str(viz.tick() - self.start_time) + '\n'
		self.boulder_data.write(self.data)
		self.boulder_data.flush()

if __name__ == "__main__":
	scene = BoulderScene()

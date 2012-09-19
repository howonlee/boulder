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
		self.preLoad()
		self.groundSetup()
		self.treasureSetup()
		self.instruction1Setup()
		#self.screenText = viz.addText('blah', viz.SCREEN) #debug screentext
		#hmd init
		self.tracking = viz.get(viz.TRACKER)
		#init timers, callbacks
		vizact.onkeydown('d', self.manager.setDebug, viz.TOGGLE)
		vizact.onkeydown('e', self.moveBoulder)
		vizact.onupdate(0, self.draw)
		if (self.tracking):
			self.Tracking = labTracker()
			self.Tracking.setPosition(0,0,0)
		
	def preLoad(self):
		'''preloads everything so we don't get little bit of lag'''
		self.ground = viz.add("ground_gray.osgb")
		self.treasure = viz.add("./chalice12_lowpoly_3ds/kelch12_lowpolyn2.3ds")
		self.boulder = viz.add("boulder.dae")
		self.avatar1 = viz.addAvatar("vcc_male.cfg", pos=(0, 0, -5), euler=(180, 0, 0))
		#no need to hide ground or treasure
		self.boulder.visible(show = viz.OFF)
		self.avatar1.visible(show = viz.OFF)
		
	def treasureTrigger(self, e):
		'''called when we approach the treasure. triggers all the other setups'''
		self.boulderSetup()
		self.avatarSetup()
		self.treasureCleanup()
		self.scrollGround()
		self.instruction2Setup()
		
	def boulderTrigger(self, e):
		print "you got hit"

	def scrollGround(self):
		'''this starts the infinite loop of ground scrolling. don't call this, call'''
		move = vizact.moveTo([0, 0, -100], time=20)
		self.ground.setPosition(0,0,0)
		scroll = vizact.call(self.scrollGround)
		self.ground.addAction(move)
		self.ground.addAction(scroll)

	def groundSetup(self):
		'''sets up a ground beneath main view'''
		self.ground.setScale(10, 10, 10)

	def treasureSetup(self):
		'''make the treasure appear and setup the proximity stuff'''
		self.treasure.setPosition([0, 0, -15])
		#these are for anims
		x, y, z = (0, 0, -15)
		self.treasure.setScale(10, 10, 10)
		#setup anim
		treasureUpDown = vizact.sequence([vizact.moveTo(pos=[x, y+1, z], time=2), vizact.moveTo(pos=[x, y+0.5, z], time=2)], viz.FOREVER)
		treasureSpin = vizact.spin(0, 1, 0, 45)
		treasureAnim = vizact.parallel(treasureUpDown, treasureSpin)
		self.treasure.addAction(treasureAnim)
		self.treasure.emissive(1,1,1)
		#setup sensor
		self.treasuresensor = vizproximity.Sensor(vizproximity.Box([1, 5, 1], center=[0, 0, 0]), source=self.treasure)
		self.manager.addSensor(self.treasuresensor)
		self.manager.onEnter(self.treasuresensor, self.treasureTrigger)
		
	def treasureCleanup(self):
		self.treasure.visible(show = viz.OFF)

	def boulderSetup(self):
		'''sets up a boulder to roll eternally'''
		self.boulder.visible(show = viz.ON)
		self.boulder.specular(0,0,0)
		self.boulder.color(0.3, 0.3, 0.3)
		self.boulder.setPosition(0, 4, 5)
		spin = vizact.spin(1, 0, 0, 300)
		#move = vizact.moveTo([0, 0, 100], time=20)
		#spinmove = vizact.parallel(spin, move)
		self.boulder.addAction(spin)
		#setup sensor
		self.bouldersensor = vizproximity.Sensor(vizproximity.Box([6, 6, 6], center=[0, 0, 0]), source=self.boulder)
		self.manager.addSensor(self.bouldersensor)
		self.manager.onEnter(self.bouldersensor, self.boulderTrigger)
		
	def avatarDeath(self):
		'''custom blended avatar animations for maximum deathiness'''
		self.avatar1.blend(8, .9)
		self.avatar1.blend(11, .1)
		neck = self.avatar1.getBone("Bip01 Neck")
		head = self.avatar1.getBone("Bip01 Head")
		torso = self.avatar1.getBone("Bip01 Spine1")
		neck.lock()
		head.lock()
		torso.lock()
		neck.lookAt([3, 3, 3], mode=viz.AVATAR_WORLD)
		head.lookAt([-30, 30, -30], mode=viz.AVATAR_WORLD)
		torso.lookAt([-100, 0, 20], mode=viz.AVATAR_WORLD)
		
	def moveBoulder(self):
		'''sets up boulder to run over avatar'''
		spin = vizact.spin(1, 0, 0, 300)
		move = vizact.moveTo([0, 0, -100], time=5)
		spinmove = vizact.parallel(spin, move)
		self.boulder.clearActions()
		self.boulder.addAction(spinmove)
		vizact.ontimer2(0.5, 0, self.avatarDeath)#the 0.5 secs is a guesstimate

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
		self.avatar1.visible(show=viz.ON)
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

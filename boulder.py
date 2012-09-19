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
		'''initialize. note that takeData is the option to take orientation, position data. Data file gets really big, really quickly.'''
		viz.go(viz.PROMPT)
		#options
		self.takeData = False
		self.MULTIKINECT = False
		self.isGameOver = False
		if self.MULTIKINECT:
			import MultiKinectInterface
		#constants
		self.LEFT_FOOT_INDEX = 14#actually ankle
		self.RIGHT_FOOT_INDEX = 18#actually ankle
		self.NUMPOINTS = 20
		self.WIN_SCORE = 5000
		self.GAME_LENGTH = 100
		#init for data
		self.score = 0
		self.count = 0 #used for taking data
		self.data = ""
		self.start_time = viz.tick()
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
		#init timers, callbacks
		vizact.onkeydown('d', self.manager.setDebug, viz.TOGGLE)
		vizact.onkeydown('e', self.moveBoulder)
		vizact.onkeydown('f', self.runAway)
		vizact.onupdate(0, self.draw)
		vizact.ontimer2(self.GAME_LENGTH, 0, self.checkWin) #timing doesn't seem to be that awfully accurate
		#kinect init
		if self.MULTIKINECT:
			self.sensor = MultiKinectInterface.MultiKinectSensor()
			self.skeleton = []
			vizact.onkeydown(viz.KEY_ESCAPE, sensor.shutdownKinect)
			for i in range(self.NUMPOINTS):
				sphere = vizshape.addSphere(radius = 0.1, color = col)
				self.skeleton.append(sphere)
		#hmd init
		self.tracking = viz.get(viz.TRACKER)
		if (self.tracking):
			self.Tracking = labTracker()
			self.Tracking.setPosition(0,0,0)

	def preLoad(self):
		'''preloads everything so we don't get little bit of lag. all files should be in resources folder of vizard'''
		#sounds
		self.footstep = viz.addAudio("footsteps.wav")
		self.crash = viz.addAudio("crash.wav")
		#objects
		self.sky = viz.add("sky_night.osgb")
		self.ground = viz.add("ground_gray.osgb")
		self.treasure = viz.add("./chalice12_lowpoly_3ds/kelch12_lowpolyn2.3ds")
		self.boulder = viz.add("boulder.dae")
		#misc
		self.avatar1 = viz.addAvatar("vcc_male.cfg", pos=(0, 0, -5), euler=(180, 0, 0))
		self.avatarface = viz.addFace("rocky.vzf")
		self.screenText = viz.addText('0', viz.SCREEN) #debug screentext
		self.blood = viz.addTexture("blood.png")
		self.bloodquad = viz.addTexQuad(viz.SCREEN)
		self.bloodquad.texture(self.blood)
		#no need to hide ground or treasure or screen stuff, which appear immediately
		self.boulder.visible(show = viz.OFF)
		self.avatar1.visible(show = viz.OFF)
		self.bloodquad.visible(show = viz.OFF)
		
	def checkWin(self):
		if (self.score > self.WIN_SCORE):
			self.runAway()
		else:
			self.moveBoulder() #and then squish

	def treasureTrigger(self, e):
		'''called when we approach the treasure. triggers all the other setups'''
		self.boulderSetup()
		self.avatarSetup()
		self.treasureCleanup()
		self.scrollGround()
		self.instruction2Setup()

	def boulderTrigger(self, e):
		self.bloodSetup()
		vizact.ontimer2(3, 0, self.gameOver, msg="Squishy Squish!")

	def groundSetup(self):
		'''sets up a ground beneath main view'''
		self.ground.setScale(10, 10, 10)

	def scrollGround(self):
		'''this starts the infinite loop of ground scrolling. don't call this, call'''
		move = vizact.moveTo([0, 0, 100], time=20)
		self.ground.setPosition(0,0,0)
		scroll = vizact.call(self.scrollGround)
		self.ground.addAction(move)
		self.ground.addAction(scroll)

	def treasureSetup(self):
		'''make the treasure appear and setup the proximity stuff'''
		#setup treasure
		self.treasure.setPosition([0, 0, -15])
		self.treasure.setScale(10, 10, 10)
		self.treasure.emissive(1,1,1)
		#setup anim
		x, y, z = (0, 0, -15)
		treasureUpDown = vizact.sequence([vizact.moveTo(pos=[x, y+1, z], time=2), vizact.moveTo(pos=[x, y+0.5, z], time=2)], viz.FOREVER)
		treasureSpin = vizact.spin(0, 1, 0, 45)
		treasureAnim = vizact.parallel(treasureUpDown, treasureSpin)
		self.treasure.addAction(treasureAnim)
		#setup sensor
		self.treasuresensor = vizproximity.Sensor(vizproximity.Box([1, 5, 1], center=[0, 0, 0]), source=self.treasure)
		self.manager.addSensor(self.treasuresensor)
		self.manager.onEnter(self.treasuresensor, self.treasureTrigger)

	def treasureCleanup(self):
		self.treasure.visible(show = viz.OFF)
		self.manager.removeSensor(self.treasuresensor) #this to prevent re-bouldering, which is a tragedy

	def boulderSetup(self):
		'''sets up a boulder to roll eternally'''
		self.boulder.visible(show = viz.ON)
		self.boulder.specular(0,0,0)
		self.boulder.color(0.3, 0.3, 0.3)
		self.boulder.setPosition(0, 4, 5)
		spin = vizact.spin(1, 0, 0, 300)
		self.boulder.addAction(spin)
		#setup sensor
		self.bouldersensor = vizproximity.Sensor(vizproximity.Box([6, 6, 6], center=[0, 0, 0]), source=self.boulder)
		self.manager.addSensor(self.bouldersensor)
		self.manager.onEnter(self.bouldersensor, self.boulderTrigger)

	def moveBoulder(self):
		'''sets up boulder to run over avatar'''
		spin = vizact.spin(1, 0, 0, 300)
		move = vizact.moveTo([0, 4, -100], time=5)
		spinmove = vizact.parallel(spin, move)
		self.boulder.clearActions()
		self.boulder.addAction(spinmove)
		vizact.ontimer2(0.5, 0, self.avatarDeath)#the 0.5 secs is a guesstimate
		
	def runAway(self):
		'''sets up player to run away successfully. avatar still gets squished.'''
		move1 = vizact.moveTo([0, 1.7, -15], time=2)
		move2 = vizact.moveTo([0, 1.7, -100], time=15)
		spin = vizact.spin(1, 0, 0, 300)
		moveBoulder = vizact.moveTo([0, 4, -10], time = 5)
		spinmove = vizact.parallel(spin, moveBoulder)
		self.boulder.clearActions()
		self.boulder.addAction(spinmove)
		viz.MainView.addAction(move1)
		viz.MainView.addAction(move2)
		vizact.ontimer2(1, 0, self.avatarDeath)
		vizact.ontimer2(1.5, 0, self.gameOver, msg="You won!")

	def instruction1Setup(self):
		'''instructions for the first part of the game, taking the treasure'''
		self.info1 = vizinfo.add("There's probably treasure...\nBut you have limited time.")
		vizact.ontimer2(6, 0, self.info1.shrink)

	def instruction2Setup(self):
		'''instructions for the second part of the game, the running'''
		#just in case it takes less than 6 seconds
		self.info1.shrink()
		self.info2 = vizinfo.add("Run from the boulder!\nBut not literally!")
		vizact.ontimer2(10, 0, self.info2.shrink)

	def avatarSetup(self):
		'''sets up the avatar to be running eternally'''
		self.avatar1.setFace(self.avatarface)
		self.avatar1.visible(show=viz.ON)
		self.avatar1.state(11)

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

	def bloodSetup(self):
		'''sets up the bloody splat to be displayed'''
		self.bloodquad.visible(show = viz.ON)
		self.bloodquad.setScale(10,10,10)
		self.bloodquad.setPosition([0.5,0.5, 0])
		#start fading immediately
		fade = vizact.fadeTo(0, time=1.5)
		self.bloodquad.addAction(fade)

	def gameOver(self, msg):
		'''shows game over message. other parts of game over are done in other functions. also stops the data.'''
		self.takeData = False
		self.isGameOver = True
		self.screenText.alignment(viz.ALIGN_CENTER)
		self.screenText.setPosition(0.5, 0.5, 0)
		self.screenText.visible(show=viz.ON)
		self.screenText.alpha(0)
		self.screenText.message("Game Over! " + msg)
		fadeIn = vizact.fadeTo(1, time=5)
		self.screenText.addAction(fadeIn)

	def checkGesture():
		self.sensor.refreshData()
		skeletonData = self.sensor.getTrackedSkeleton(0,0)
		if skeletonData != None:
			for i in range(self.NUMPOINTS):
				self.skeleton[i].visible(viz.ON)
				point = skeletonData[i]
				skeleton[i].setPosition(self.NUMPOINTS)
			if ((skeletonData[RIGHT_FOOT_INDEX][1] > 0.2) or (skeletonData[LEFT_FOOT_INDEX][1] > 0.2)):
				ground.playsound("kick5.wav")
				self.score += 1
				print self.score #debugging
		else:
			for i in range(numPoints):
				self.skeleton[i].visible(viz.OFF)

	def draw(self):
		'''called every frame'''
		if (self.isGameOver == False):
			self.screenText.message(str(max(self.GAME_LENGTH - (viz.tick() - self.start_time), 0))) #show current time remaining
		self.count += 1 #in other words, every 6 frames.
		if (self.count == 6 and self.takeData):
			self.getdata()
			self.count = 0
		if self.MULTIKINECT:
			self.checkGesture()

	def getdata(self):
		'''formats data and writes it in the file. we must offload to another thread eventually. Data file gets big really quickly.'''
		orientation = viz.MainView.getEuler()
		position = viz.MainView.getPosition()
		self.data = self.data + "euler: " + str(orientation) + '\tposition: ' + str(position) + "\ttime: " + str(viz.tick() - self.start_time) + '\n'
		self.boulder_data.write(self.data)
		self.boulder_data.flush()

if __name__ == "__main__":
	scene = BoulderScene()

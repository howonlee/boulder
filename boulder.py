'''
boulder.py, by howon and david
a game which consists of running from a boulder
'''

'''
TODOs:
optimize
'''

'''
NOTE: how ambisonic stuff works:
	-vizsonic can only handle up to 24 sound objects. Therefore, reuse sound objects.
	-volume and directionality are the only settings added by vizsonic
	-set the ambient sound (music) with vizsonic.setAmbient()
'''

# I put the variables up here because I was trying out "from vizsonic import *",
# which you can't use within a module. After I was done testing that,
# they looked better up here because then all the imports are in one place.
AMBISONIC = True
MULTIKINECT = True

import viz
import vizact
import vizproximity
import viztask
import vizinput
import vizinfo
import vizshape
import cProfile
from labtracker import *
if AMBISONIC:
	import vizsonic
if MULTIKINECT:
	import MultiKinectInterface

class BoulderScene:
	def __init__(self):
		'''initialize. note that takeData is the option to take orientation, position data. Data file gets really big, really quickly.'''
		viz.go(viz.PROMPT)
		#options
		self.takeData = False
		self.REARVIEW = True
		self.isGameOver = False
		#constants
		self.LEFT_FOOT_INDEX = 14#actually ankle
		self.RIGHT_FOOT_INDEX = 18#actually ankle
		self.NUMPOINTS = 20
		self.WIN_SCORE = 50
		self.GAME_LENGTH = 100
		#init for data
		self.start_time = viz.tick()
		self.score = 0
		self.count = 0 #used for taking data
		if (self.takeData):
			self.data = ""
			self.boulder_data = open('boulder_data.txt', 'a')
		#manager init
		self.manager = vizproximity.Manager()
		self.target = vizproximity.Target(viz.MainView)
		self.manager.addTarget(self.target)
		#experimental rear-view stuff
		if self.REARVIEW:
			self.RearViewWindow = viz.addWindow()
			self.RearView = viz.addView()
			self.RearViewWindow.setView(self.RearView)
			self.RearViewWindow.setPosition([0, 1])
			self.viewLink = viz.link(viz.MainView, self.RearView)
			self.viewLink.preEuler([180, 0, 0])
		#setup objects
		self.preLoad()
		self.groundSetup()
		self.treasureSetup()
		self.avatarSetup()
		self.faceSetup()
		self.instruction1Setup()
		viz.MainView.setEuler(180, 0, 0)
		#init timers, callbacks
		vizact.onkeydown('d', self.manager.setDebug, viz.TOGGLE)
		vizact.onkeydown('e', self.moveBoulder)
		vizact.onkeydown('h', self.treasureTrigger, None)
		vizact.onkeydown('f', self.runAway)
		vizact.onupdate(0, self.draw)
		vizact.ontimer2(self.GAME_LENGTH, 0, self.checkWin) #timing doesn't seem to be that awfully accurate
		#kinect init
		if MULTIKINECT:
			self.sensor = MultiKinectInterface.MultiKinectSensor()
			vizact.onkeydown(viz.KEY_ESCAPE, self.sensor.shutdownKinect)
			self.rightFootUp = False
			self.leftFootUp = False
		#hmd init
		self.tracking = viz.get(viz.TRACKER)
		if (self.tracking):
			self.Tracking = labTracker()
			self.Tracking.setPosition([0,0,0])

	def preLoad(self):
		'''preloads everything so we don't get little bit of lag. all files should be in resources folder of vizard.
		note that when this function fucks up, your world will get emptier and quieter.
		so if your world gets empty and quiet, assume this function fucked up
		'''
		#objects
		self.sky = viz.add("sky_night.osgb")
		self.ground = viz.add("ground_gray.osgb")
		self.wall1 = viz.add("ground_gray.osgb")
		self.wall2 = viz.add("ground_gray.osgb")
		self.ceiling = viz.add("ground_gray.osgb")
		self.treasure = viz.add("./chalice12_lowpoly_3ds/kelch12_lowpolyn2.3ds")
		self.boulder = viz.add("boulder.dae")
		self.creepyface = viz.add("rocky.obj")
		#misc
		self.avatar1 = viz.addAvatar("CC2_m009_hipoly_A3_v2.cfg")
		self.avatarface = viz.addFace("rocky.vzf")
		self.screenText = viz.addText('0', viz.SCREEN)
		self.screenText2 = viz.addText('1', viz.SCREEN)
		self.screenText2.setPosition(0.90, 0, 0)
		#sounds
		self.treasure_sound = self.getSound("treasure.wav", self.treasure, True)
		self.crunch = self.getSound("bonesnap.wav", self.avatar1)
		self.scream = self.getSound("scream_male.wav", self.avatar1)
		self.gong = self.getSound("gong.wav", self.treasure)
		self.whoosh = self.getSound("whoosh.wav", self.avatarface)
		self.groundroll = self.getSound("groundroll_loop.wav", self.ground, loop=True)
		self.theme = self.getSound("theme.wav", self.treasure, loop=True)
		#creepy face eyes
		self.eyes = []#eyes for creepy face
		self.eye1 = viz.add('fire.osg', pos=(1, 6.6, -31))
		self.eye1.hasparticles()
		self.eyes.append(self.eye1)
		self.eye2 = viz.add('fire.osg', pos=(-1, 6.6, -31))
		self.eye2.hasparticles()
		self.eyes.append(self.eye2)
		self.blood = viz.addTexture("blood.png")
		self.bloodquad = viz.addTexQuad(viz.SCREEN)
		self.bloodquad.texture(self.blood)
		#no need to hide ground or treasure or avatar or screen stuff, which appear immediately
		self.boulder.visible(show = viz.OFF)
		self.bloodquad.visible(show = viz.OFF)
		self.eye1.visible(show = viz.OFF)
		self.eye2.visible(show = viz.OFF)

	def getSound(self, soundfile, object, loop=False):
		'''a wrapper to setup the soundobject to play a sound.
		the returned object should be sent back to playSound.
		this function returns a sound object.'''
		if AMBISONIC:
			sound = object.playsound(soundfile)
		else:
			sound = viz.addAudio(soundfile)
			if loop:
				sound.loop()
		sound.stop()
		return sound

	def playSound(self, soundobject, loop=False):
		'''passed a soundobject returned from getSound. plays the actual sound.'''
		if AMBISONIC and loop:
			soundobject.play(True)
		else:
			soundobject.play()

	def checkWin(self):
		if (self.score > self.WIN_SCORE):
			self.runAway()
		else:
			self.moveBoulder() #and then squish

	def treasureTrigger(self, e):
		'''called when we approach the treasure. triggers all the other setups'''
		if AMBISONIC:
			vizsonic.setShaker(.5)
		self.playSound(self.gong)
		self.boulderSetup()
		self.avatarRun()
		self.treasureCleanup()
		self.scrollGround()
		self.faceFlash()
		self.instruction2Setup()
		vizact.ontimer2(2, 0, self.playSound, self.theme)

	def boulderTrigger(self, e):
		'''called when we hit the boulder, to indicate that we have been squished'''
		self.crunch.play() #sfx: sickening crunch. note we don't use 3d
		self.bloodSetup()
		vizact.ontimer2(3, 0, self.gameOver, msg="Squishy Squish!")

	def groundSetup(self):
		'''sets up a ground beneath main view and walls and ceiling'''
		self.ground.setScale(10, 10, 10)
		self.wall1.setPosition(-5, 0, 0)
		self.wall1.setEuler(90, 90, 0)
		self.wall1.setScale(10, 10, 10)
		self.wall2.setPosition(5, 0, 0)
		self.wall2.setEuler(270, 90, 0)
		self.wall2.setScale(10, 10, 10)
		self.ceiling.setPosition(0, 30, 0)
		self.ceiling.setEuler(0, 180, 0)
		self.ceiling.setScale(10, 10, 10)

	def scrollGround(self):
		'''this starts the infinite loop of ground scrolling. doesn't stop once started. only the ground scrolls, not walls or ceiling'''
		self.groundroll.play() #sfx: mechanical-ish rumbling
		move = vizact.moveTo([0, 0, 100], time=20)
		self.ground.setPosition(0,0,0)
		scroll = vizact.call(self.scrollGround)
		self.ground.addAction(move)
		self.ground.addAction(scroll)

	def treasureSetup(self):
		'''make the treasure appear and setup the proximity stuff'''
		#setup treasure
		self.treasure.setPosition([0, 0, -3])
		self.treasure.setScale(10, 10, 10)
		self.treasure.emissive(1,1,1)
		#setup anim
		x, y, z = (0, 0, -15)
		treasureUpDown = vizact.sequence([vizact.moveTo(pos=[x, y+1, z], time=2), vizact.moveTo(pos=[x, y+0.5, z], time=2)], viz.FOREVER)
		treasureSpin = vizact.spin(0, 1, 0, 45)
		treasureAnim = vizact.parallel(treasureUpDown, treasureSpin)
		self.treasure.addAction(treasureAnim)
		#setup sensor
		self.treasuresensor = vizproximity.Sensor(vizproximity.Box([0.4, 5, 0.4], center=[0, 0, 0]), source=self.treasure)
		self.manager.addSensor(self.treasuresensor)
		self.playSound(self.treasure_sound, True)
		self.playSound(self.theme) # testing
		self.manager.onEnter(self.treasuresensor, self.treasureTrigger)

	def treasureCleanup(self):
		self.treasure_sound.stop()
		self.treasure_sound.stop()
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
		self.bouldersensor = vizproximity.Sensor(vizproximity.Box([7, 7, 7], center=[0, 0, 0]), source=self.boulder)
		self.manager.addSensor(self.bouldersensor)
		self.manager.onEnter(self.bouldersensor, self.boulderTrigger)

	def faceSetup(self):
		'''sets up creepy face which looks like statue'''
		self.creepyface.setPosition(0, 7, -35)
		self.creepyface.setEuler(180, 340, 0)
		self.creepyface.setScale(0.02, 0.02, 0.02)
		for eye in self.eyes:
			eye.setScale(7, 3, 7)

	def faceFlash(self):
		'''gets the creepy face to flash with firey eyes'''
		vizact.ontimer2(0.5, 0, self.whoosh.play) #sfx: whoosh
		fadeIn = vizact.fadeTo(1, time=2)
		for eye in self.eyes:
			eye.visible(show = viz.ON)
			eye.alpha(0)
			eye.addAction(fadeIn)

	def moveBoulder(self):
		'''sets up boulder to run over avatar'''
		spin = vizact.spin(1, 0, 0, 300)
		move = vizact.moveTo([0, 4, -100], time=5)
		spinmove = vizact.parallel(spin, move)
		self.boulder.clearActions()
		self.boulder.addAction(spinmove)
		vizact.ontimer2(0.2, 0, self.avatarDeath)#the 0.2 secs is a guesstimate
		self.theme.stop()

	def runAway(self):
		'''sets up player to run away successfully. avatar still gets squished.'''
		self.footstep2.play() #speedy footsteps
		move1 = vizact.moveTo([0, 1.7, -15], time=2)
		move2 = vizact.moveTo([0, 1.7, -100], time=15)
		spin = vizact.spin(1, 0, 0, 300)
		moveBoulder = vizact.moveTo([0, 4, -10], time = 5)
		spinmove = vizact.parallel(spin, moveBoulder)
		self.boulder.clearActions()
		self.boulder.addAction(spinmove)
		viz.MainView.addAction(move1)
		viz.MainView.addAction(move2)
		vizact.ontimer2(1.3, 0, self.avatarDeath)
		vizact.ontimer2(1.5, 0, self.gameOver, msg="You won!\nPoor guy.")

	def instruction1Setup(self):
		'''instructions for the first part of the game, taking the treasure'''
		self.info1 = vizinfo.add("'No! Don't do it!'\nBut that twinkling sure is twinkly...")
		vizact.ontimer2(6, 0, self.info1.shrink)

	def instruction2Setup(self):
		'''instructions for the second part of the game, the running'''
		#just in case the previous notification takes less than 6 seconds
		self.info1.shrink()
		self.info2 = vizinfo.add("'We gotta run! There's a boulder rolling at us! Gotta run "
								 + str(self.WIN_SCORE) +
								 " steps!'\nTo run away, lift your ankles and put them back down, in place.")
		vizact.ontimer2(10, 0, self.info2.shrink)

	def avatarSetup(self):
		'''sets up the avatar to refuse at you'''
		self.avatar1.setFace(self.avatarface)
		self.avatar1.setPosition(-2, 0, -6)
		self.avatar1.setEuler(60, 0, 0)
		self.avatar1.state(193) #shaking head

	def avatarRun(self):
		'''sets up the avatar to be running eternally'''
		self.avatar1.setPosition(0, 0, 0)
		self.avatar1.setEuler(180, 0, 0)
		self.avatar1.state(143) #running like mofo

	def avatarDeath(self):
		'''custom blended avatar animations for maximum deathiness'''
		self.scream.play()#sfx: scream
		self.crunch.play()#sfx: crunch
		self.avatar1.blend(1, .9) #lying down
		self.avatar1.blend(143, .1) #running
		neck = self.avatar1.getBone("Bip01 Neck")
		head = self.avatar1.getBone("Bip01 Head")
		torso = self.avatar1.getBone("Bip01 Spine1")
		neck.lock()
		head.lock()
		torso.lock()
		neck.lookAt([3, 3, 3], mode=viz.AVATAR_WORLD)
		head.lookAt([-30, 30, -30], mode=viz.AVATAR_WORLD)
		torso.lookAt([-100, 0, 20], mode=viz.AVATAR_WORLD)
		self.avatar1.setEuler(0, 270, 0)#gotta rotate, because there's no lying action
		self.avatar1.setPosition(0, 0.3, 0)

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
		if AMBISONIC:
			vizsonic.setShaker(0)
		self.takeData = False
		self.isGameOver = True
		self.screenText.alignment(viz.ALIGN_CENTER)
		self.screenText.setPosition(0.5, 0.5, 0)
		self.screenText.visible(show=viz.ON) #to make sure
		self.screenText.alpha(0)
		self.screenText.message("Game Over! " + msg)
		self.screenText2.message("") #empty it out
		fadeIn = vizact.fadeTo(1, time=5)
		self.screenText.addAction(fadeIn)

	def checkGesture(self):
		'''check Kinect gesture to make sure you're running'''
		self.sensor.refreshData()
		skeletonData = self.sensor.getTrackedSkeleton(0,0)
		if skeletonData != None:
			#print ((skeletonData[self.RIGHT_FOOT_INDEX][1]))
			if ((skeletonData[self.RIGHT_FOOT_INDEX][1] > -0.6) and (not self.rightFootUp)):
				self.rightFootUp = True
			elif ((skeletonData[self.RIGHT_FOOT_INDEX][1] < -0.6) and (self.rightFootUp)):
				self.rightFootUp = False
				self.score += 1
			if ((skeletonData[self.LEFT_FOOT_INDEX][1] > -0.6) and (not self.leftFootUp)):
				self.leftFootUp = True
			elif ((skeletonData[self.LEFT_FOOT_INDEX][1] < -0.6) and (self.leftFootUp)):
				#self.ground.playsound("kick5.wav") # play a footstep instead, so we get feedback
				self.score += 1
				self.leftFootUp = False

	def draw(self):
		'''called every frame'''
		if (self.isGameOver == False):
			currTime = self.GAME_LENGTH - (viz.tick() - self.start_time)
			self.screenText.message(str(round(max(currTime, 0), 1))) #show current time remaining
			self.screenText2.message(str(self.score))
		self.count += 1 #in other words, every 6 frames.
		if (self.count == 6 and self.takeData):
			self.getData()
			self.count = 0
		if (MULTIKINECT): #kinect is 30fps
			self.checkGesture()


	def getData(self):
		'''formats data and writes it in the file. we must offload to another thread eventually. Data file gets big really quickly.'''
		orientation = viz.MainView.getEuler()
		position = viz.MainView.getPosition()
		self.data = self.data + "euler: " + str(orientation) + '\tposition: ' + str(position) + "\ttime: " + str(viz.tick() - self.start_time) + '\n'
		self.boulder_data.write(self.data)
		self.boulder_data.flush()

if __name__ == "__main__":
	scene = BoulderScene()

#main file of the straight track (easy mode), all functions controlling user/computer players


from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
import sys
import math
import random

def displayBigText(txt, position, color, shad = (0,0,0,1)):
    size = 0.25
    display = OnscreenText(text = txt, fg = color, scale = size, 
                    shadow = shad, parent=base.a2dTopLeft, 
                    pos=position, align=TextNode.ALeft)
    return display

def displaySmallText(txt, position, color):
    size = 0.1
    display = OnscreenText(text = txt, fg = color, scale = size, 
                        parent=base.a2dTopLeft, pos=position, 
                        align=TextNode.ALeft)
    return display

def roundtoThou(n):
    return math.ceil(n * 1000.0)/1000.0

class Game(ShowBase):
 
    def __init__(self, screen='start'):
        ShowBase.__init__(self)
        
        #countdown sound file from https://www.youtube.com/watch?v=KOoCEIwswYg
        self.cdMusic = loader.loadSfx("sounds/countdown.ogg")
        #race sound file from https://www.youtube.com/watch?v=eawQqkq8ROo
        self.rMusic = loader.loadSfx("sounds/race.ogg")
        
        #window and camera
        self.win.setClearColor((0, 0, 0, 1))
        self.startPos = LPoint3f(100, 50, 0)
        self.disableMouse()
        self.x = self.startPos.getX()
        self.y = self.startPos.getY()
        self.z = 15
        self.camera.setPos(-20, self.y/3, self.z)
        self.camera.setH(90)
        self.camMaxDist = 30
        self.camMinDist = 25
        
        #mario character (user player)
        #3d mario model file from past tp, with permission:
        #https://github.com/Kabartchlett/15-112-Term-Project
        self.mario = Actor("models/MarioKart")
        self.scale = 2.5
        self.mario.setScale(self.scale)
        self.mario.setH(self.mario, 90)
        self.mario.reparentTo(render)
        self.marioX = 3
        self.marioY = self.startPos.getY() /3
        self.marioZ = 11
        self.mario.setPos(self.marioX, self.marioY, self.marioZ)
        self.mario.y_speed = -50
        self.mario.h_speed = 0
        self.marioRaceTime = 0
        self.marioFinishTime = 0
        self.drifted = False
        self.marioNumFellOff = 0
        self.mario.falling = False
        self.marioStartFallTime = None
        self.marioStartFallPos = None
        self.mario.mush = False
        self.mario.megamush = False
        self.mario.bananaSpin = False
        self.mario.preSpinAngle = self.mario.getH()
        self.mario.doubleMush = False
        
        #floater method from roaming ralph:
        #https://github.com/panda3d/panda3d/tree/master/samples/roaming-ralph
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.mario)
        self.floater.setZ(2)
        
        #computer player
        #3d yoshi model file from past tp, with permission:
        #https://github.com/Kabartchlett/15-112-Term-Project
        self.yoshi = Actor("models/YoshiKart")
        self.yoshi.setScale(self.scale)
        self.yoshi.setH(self.yoshi, 90)
        self.yoshi.reparentTo(render)
        self.yoshiX = 3
        self.yoshiY = self.startPos.getY() *(2/3)
        self.yoshiZ = 10
        self.yoshi.setPos(self.yoshiX, self.yoshiY, self.yoshiZ)
        self.yoshi.y_speed = -45
        self.yoshi.h_speed = 0
        self.yoshiRaceTime = 0
        self.yoshiFinishTime = 0
        self.yoshi.mush = False
        self.yoshi.megamush = False
        self.yoshi.bananaSpin = False
        self.yoshi.preSpinAngle = self.yoshi.getH()
        self.yoshi.doubleMush = False
        self.yoshi.falling = False
        
        #statuses
        self.gameover = False
        self.victory = False
        self.loss = False
        self.menuCount = 0
        self.paused = False
        self.addMove = 1
        self.timeDelay = 0
        self.start = True
        self.escapeStart = False
        self.menuStart = False
        self.gameMode = None
        self.startMode = True
        self.escapeMode = False
        self.charFin = True
        self.counting = True
        self.playing = True
        self.playRaceMusic = False
        
        #data init
        self.vDataRows = 50
        self.finalX = self.x
        self.lines = []
        self.isPaused = []
        self.wait = 11
        self.countdowns = []
        self.startText = []
        self.modeText = []
        self.OSimageText = []
        self.timeCharFin = None
        self.lives = []
        
        #collision with items init
        self.cTrav = CollisionTraverser()
        from itemStr import Item
        self.itemClass = Item(self)
        
        self.yoshiHandler = CollisionHandlerEvent()
        self.yoshiHandler.addInPattern('into-self.yoshi')
        
        self.collisions = self.collideInit()
        
        self.cTrav.addCollider(self.collisions, self.yoshiHandler)
        self.accept('into-self.yoshi', self.collideYoshi)
        
        
        #collision with road init
        self.ray = CollisionRay(0,0,self.mario.getZ(), 0,0,-1)
        self.roadCol = self.mario.attachNewNode(CollisionNode('colNode'))
        self.roadCol.node().addSolid(self.ray)
        self.roadCol.node().setCollideMask(BitMask32.allOn())
        self.mario.setCollideMask(BitMask32.allOff())
        self.lifter = CollisionHandlerFloor()
        self.cTrav.addCollider(self.roadCol, self.lifter)
        self.lifter.addCollider(self.roadCol, self.mario)
        
        #key events
        self.accept('escape', sys.exit)
        self.accept('q', self.menuToggle, ['display'])
        self.accept('e', self.menuToggle, ['remove'])
        self.accept('p', self.pause)
        
        #tasks
        if self.start and screen != 'mode':
            taskMgr.add(self.startScreen, 'start')
    
    def addTasks(self,task):
        self.straightRoad()
        self.displayLives()
        taskMgr.add(self.move, "move")
        taskMgr.add(self.moveSim, 'moveSim')
        taskMgr.add(self.countdown, 'countdown')
        taskMgr.add(self.mapPrev, 'map')
        taskMgr.add(self.takeLives, 'lives')
        taskMgr.add(self.moveCam, 'cam')
    
    def collideInit(self):
        mNode = CollisionNode('mario')
        mNode.addSolid(CollisionSphere(0,0,0,self.scale-2))
        marioCol = self.mario.attachNewNode(mNode)
        
        yNode = CollisionNode('yoshi')
        yNode.addSolid(CollisionSphere(0,0,0,self.scale-2))
        yoshiCol = self.yoshi.attachNewNode(yNode)
        
        return marioCol
    
    def straightRoad(self):
        
        #geom format and data
        z = 10
        
        format = GeomVertexFormat.getV3n3c4t2()
        vData = GeomVertexData('road', format, Geom.UHStatic)
        vData.setNumRows(self.vDataRows)
        
        vertex = GeomVertexWriter(vData, 'vertex')
        normal = GeomVertexWriter(vData, 'normal')
        color = GeomVertexWriter(vData, 'color')
        texcoord = GeomVertexWriter(vData, 'texcoord')
        
        for i in range(self.vDataRows):
            x = i * self.x
            vertex.addData3f(x, 0, z)
            vertex.addData3f(x, self.y, z)
            
            for n in range(2):
                normal.addData3f(x,self.y/2,z)
            
            if i > self.vDataRows-6: #finish line
                for n in range(4):
                    color.addData4f(255,0,0,1)
            elif i%2 == 0: #rainbow road
                color.addData4f(0,255,255,1)
                color.addData4f(0,255,0,1)
                color.addData4f(255,255,0,1)
                color.addData4f(255,0,255,1)
            
            texcoord.addData2f(x,0)
            texcoord.addData2f(x,self.y)
        
        self.finalX = x
        
        #geom primitives
        road = GeomTristrips(Geom.UHStatic)
        road.add_consecutive_vertices(0,2*self.vDataRows)
        road.close_primitive()
        
        #connect data and primitives
        geom = Geom(vData)
        geom.addPrimitive(road)
        
        node = GeomNode('geomNode')
        node.addGeom(geom)
        
        nodePath = render.attachNewNode(node)
        
        nodePath.set_two_sided(True)
    
    def collideYoshi(self, collEntry):
        #altered use of conservation of momentum
        
        if self.mario.getH() != 90:
            mario_sign = (90 - self.mario.getH()) // abs(90 - self.mario.getH())
        else: mario_sign = 0
        if self.yoshi.getH() != 90:
            yoshi_sign = (90 - self.yoshi.getH()) // abs(90 - self.yoshi.getH())
        else: yoshi_sign = 0
        mario_xSpeed = self.mario.y_speed * math.cos(self.mario.getH())
        mario_ySpeed = self.mario.y_speed * math.sin(self.mario.getH())
        yoshi_xSpeed = self.yoshi.y_speed * math.cos(self.yoshi.getH())
        yoshi_ySpeed = self.yoshi.y_speed * math.sin(self.yoshi.getH())
        
        x_speedAvg = ( mario_xSpeed + yoshi_xSpeed ) / 2
        y_speedAvg = ( mario_ySpeed + yoshi_ySpeed ) / 2
        
        marioAngle = math.degrees(math.acos( y_speedAvg/self.mario.y_speed ))
        yoshiAngle = math.degrees(math.acos( y_speedAvg/abs(self.yoshi.y_speed) ))
        
        self.mario.setH(self.mario.getH() + mario_sign*0.2*marioAngle)
        self.yoshi.setH(self.yoshi.getH() - mario_sign*0.2*yoshiAngle)
    
    def isOffRoad(self, player):
        return player.getY() < 0 or player.getY() > self.y or \
            player.getX() < 0 or player.getX() > self.finalX
    
    def checkItemCol(self,player):
        #checks if player ran into an item box
        for i in range(len(self.itemClass.items)):
            items = self.itemClass.items[i]
            if self.itemClass.itemsPresent[i] and abs(items.getX() - player.getX()) <= 3 and\
                    abs(items.getY() - player.getY()) <= 3 and\
                    abs(items.getZ() - player.getZ()) <= 3:
                self.itemClass.collideItem(items, i, player)
    
    def checkBananaCol(self,player):
        #makes player react to running into a banana
        
        #banana collision detection
        for i in range(len(self.itemClass.bananas)):
            banana = self.itemClass.bananas[i]
            if self.itemClass.bananaPresent[i] and abs(banana.getX() - player.getX()) <= 3 and\
                    abs(banana.getY() - player.getY()) <= 3 and\
                    abs(banana.getZ() - player.getZ()) <= 3:
                self.itemClass.bananaReact(banana, i, player)
                player.preSpinAngle = player.getH()
        
        #spin player
        if player.bananaSpin and globalClock.getFrameTime() < \
                            self.itemClass.beginSpin + self.itemClass.spinTime:
            player.h_speed = 700
            player.y_speed = 0
        
        #end spin
        if player.bananaSpin and (abs(globalClock.getFrameTime() - (self.itemClass.beginSpin + self.itemClass.spinTime)) < 1):
            player.bananaSpin = False
            player.h_speed = 0
            if player == self.yoshi: player.y_speed = -25
            elif player == self.mario: player.y_speed = -30
            player.setH(90)
        
    def checkMushEnd(self, player):
        #ends the effect of mushroom or mega mushroom
        if player.mush:
            if player.falling or abs(player.getX() - self.itemClass.beginBoostX) >= \
                                                self.itemClass.boostDistance:
                player.mush = False
                self.itemClass.mushroom(player)
        
        if player.megamush:
            if player.falling or abs(player.getX()  - self.itemClass.beginBoostX) >= \
                                                    self.itemClass.boostDistance:
                player.megamush = False
                self.itemClass.megaMushroom(player)
        
    
    def moveSim(self,task):
        dt = globalClock.getDt()
        self.timeDelay += dt
        
        h_speed = self.yoshi.h_speed
        y_speed = self.yoshi.y_speed
        z_speed = 10
        
        #chance of falling off road
        chance = 1
        maxNum = 100
        fall = random.randint(1,maxNum)
        if fall <= chance:
            h_speed = 5
        if fall >= maxNum-chance:
            h_speed = -5
        
        #checks for banana collision
        self.checkBananaCol(self.yoshi)
        
        #checks for item collision
        self.checkItemCol(self.yoshi)
       
        #change position, angle
        dh = h_speed * dt
        dy = y_speed * dt
        dz = z_speed * dt
        if self.timeDelay > self.wait:
            self.yoshiRaceTime += dt
            self.yoshi.setH(self.yoshi.getH() + dh)
            self.yoshi.setY(self.yoshi, dy)
        
        #stop at end of road
        if self.yoshi.getX() > self.finalX - 20:
            self.yoshi.y_speed = 0
        
        #fell off road
        if self.isOffRoad(self.yoshi):
            self.yoshi.y_speed = 0
            self.yoshi.setZ(self.yoshi.getZ() - dz)
        
        #crossed finish line
        if self.yoshi.getX() > (self.vDataRows-4)*self.x and self.yoshi.getZ() >= 10:
            self.yoshiFinishTime = math.ceil(self.yoshiRaceTime * 1000.0)/1000.0
            self.loss = True
            escText = displaySmallText('press esc to quit program', (0.8,-1.2), (255,255,255,0.7))
            self.OSimageText.append(escText)
            if self.gameover == False and self.victory == False:
                compwins = displayBigText('COMPUTER WINS', (0.4, -1),  (255,0,0,0.5))
                self.OSimageText.append(compwins)
        
        #checks for power ups
        self.checkMushEnd(self.yoshi)
        
        return task.cont
    
    def move(self, task):
        
        if self.playing and self.playRaceMusic:
            self.rMusic.play()
            self.playing = False
        
        dt = globalClock.getDt()
        self.timeDelay += dt
        
        #enable moving mario with direction keys
        h_speed = self.mario.h_speed
        y_speed = 0
        x_speed = 0
        z_speed = 10
        h_incr = 80
        y_incr = self.mario.y_speed
        right_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.right())
        left_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.left())
        forward_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.up())
        backward_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.down())
        
        if right_down:
            h_speed -= h_incr
        if left_down:
            h_speed += h_incr
        if forward_down:
            y_speed += y_incr
        if backward_down:
            y_speed -= y_incr
        
        #checks for banana punishment
        self.checkBananaCol(self.mario)
        
        #checks for collision with item boxes
        self.checkItemCol(self.mario)
        
        #change position, angle
        dh = h_speed * dt
        dy = y_speed * dt
        dz = z_speed * dt
        dx = x_speed * dt
        if self.timeDelay > self.wait:
            self.marioRaceTime += dt
            self.mario.setH(self.mario.getH() + dh)
            self.mario.setY(self.mario, dy)
            self.mario.setX(self.mario, dx)
        
        #fell off road
        if self.isOffRoad(self.mario) and not self.mario.falling:
            self.marioNumFellOff += 1
            self.marioStartFallTime = globalClock.getFrameTime()
            self.marioStartFallPos = self.mario.getPos()
            self.mario.falling = True
            if self.marioNumFellOff > 2:
                self.gameOver()
                
        if self.mario.falling:
            self.mario.setZ(self.mario.getZ() - dz)
            self.mario.y_speed = 0
            self.resetPreFallPos(self.mario, self.marioStartFallPos)
        
        #crossed finish line
        if self.mario.getX() > (self.vDataRows-4)*self.x:
            self.marioFinishTime = roundtoThou(self.marioRaceTime)
            self.victory = True
            if self.loss == False and self.gameover == False:
                vic = displayBigText('VICTORY!', (0.8, -1),  (255,255,0,1))
                self.OSimageText.append(vic)
                escText = displaySmallText('press esc to quit program', (0.8,-1.2), (255,255,255,0.7))
                self.OSimageText.append(escText)
        
        #show leaderboard if both players crossed finish line
        if ( self.gameover or self.victory or self.loss ) and self.charFin:
            self.timeCharFin = globalClock.getFrameTime()
            self.charFin = False
        
        if self.timeCharFin != None and globalClock.getFrameTime() > self.timeCharFin + self.wait/2:
            self.leaderboard()
        
        #checks for power ups
        self.checkMushEnd(self.mario)
        
        return task.cont
        
    def moveCam(self,task):
        dt = globalClock.getDt()
        
        #enable camera spinning around mario using a,s,w,x,k,l keys
        cam = 0
        camSpeed = 20
        a_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.asciiKey(b"a"))
        s_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.asciiKey(b"s"))
        
        #wxkl for debugging purposes
        
        if a_down:
            cam += camSpeed
        if s_down:
            cam -= camSpeed
        
        dCam = cam * dt
        self.camera.setX(self.camera, dCam)
        
        #keep camera close to mario, from roaming ralph:
        #https://github.com/panda3d/panda3d/tree/master/samples/roaming-ralph
        camVector = self.mario.getPos() - self.camera.getPos()
        camVector.setZ(0) #don't change camera's z distance
        camDist = camVector.length() #magnitude
        camVector.normalize() #unit vector (direction)
        
        if camDist > self.camMaxDist:
            self.camera.setPos(self.camera.getPos() + \
                                camVector * (camDist - self.camMaxDist))
            camDist = self.camMaxDist
        if camDist < self.camMinDist:
            self.camera.setPos(self.camera.getPos() - \
                                camVector * (self.camMinDist - camDist))
            camDist = self.camMinDist
        
        if self.camera.getZ() != self.mario.getZ() + 6.0:
            self.camera.setZ(self.mario.getZ() + 6.0)
        
        self.cTrav.traverse(render)
        
        self.camera.lookAt(self.floater)
        
        return task.cont
    
    def getPlayerProg(self, player):
        totalX = self.finalX
        x = player.getX()
        progress = x/totalX
        return progress
    
    def mapPrev(self,task):
        #show map in corner with all player's positions
        
        radius = 0.085
        length = 2*radius
        #image made in Preview
        mapP = OnscreenImage(image = 'images/straightMap.png', pos = (1,0,0.8), scale = 0.1)
        self.OSimageText.append(mapP)
        
        marioProg = self.getPlayerProg(self.mario)
        marioY = (0.8-radius) + length*marioProg
        
        yoshiProg = self.getPlayerProg(self.yoshi)
        yoshiY = (0.8-radius) + length*yoshiProg
        
        finishY = 0.8 + radius
        
        #images made in Preview
        marioSym = OnscreenImage(image = 'images/mariosym.png', 
                                pos = (1,0,marioY), scale = 0.01)
        yoshiSym = OnscreenImage(image = 'images/yoshisym.png', 
                                pos = (1,0,yoshiY), scale = 0.01)
        finishSym = OnscreenImage(image = 'images/finishsym.png', 
                                pos = (1,0,finishY), scale = 0.01)
        
        self.OSimageText.append(marioSym)
        self.OSimageText.append(yoshiSym)
        self.OSimageText.append(finishSym)
        
        return task.cont
    
    def resetPreFallPos(self, player, pos):
        #only mario is replaced on the track
        if self.marioStartFallTime != None and not self.gameover and globalClock.getFrameTime() > self.marioStartFallTime + self.wait/4:
            self.mario.falling = False
            
            x = player.getX()
            y = self.y/2
            z = player.getY()
            
            player.setPos(x,y,z)
            self.mario.y_speed = -30
       
    def displayLives(self):
        #display the number of lives user player has left
        
        livesText = displaySmallText('lives:', (0.1,-0.15), (255,255,255,1))
        self.OSimageText.append(livesText)
        #images made in Preview
        self.life1 = OnscreenImage(image = 'images/life.png', pos = (-0.9,0,0.87), scale = 0.03)
        self.life2 = OnscreenImage(image = 'images/life.png', pos = (-0.8,0,0.87), scale = 0.03)
        self.life3 = OnscreenImage(image = 'images/life.png', pos = (-0.7,0,0.87), scale = 0.03)
        self.OSimageText.append(self.life1)
        self.OSimageText.append(self.life2)
        self.OSimageText.append(self.life3)
    
    def takeLives(self,task):
        if self.marioNumFellOff == 1: self.life3.destroy()
        if self.marioNumFellOff == 2: self.life2.destroy()
        if self.marioNumFellOff == 3: self.life1.destroy()
        
        return task.cont
    
    def startScreen(self, task):
        if self.escapeStart: return
        
        if self.start:
            #image from supermariorun.com
            logo = OnscreenImage(image = 'images/mario.png', pos = (0.01,0,-0.5), scale = 0.3)
            
            welcome = OnscreenText('Welcome to Mario Kart!', fg = (255,0,0,1), scale = 0.2,
                                    shadow = (255,255,255,1), parent = base.a2dTopLeft, 
                                    pos = (0.2, -0.5), align = TextNode.ALeft)
            
            show_menu = OnscreenText('press Q to see key instructions', fg = (255,255,255,1), 
                                    scale = 0.1, shadow = (0,255,0,1), 
                                    parent = base.a2dTopLeft, pos = (0.6, -0.8), 
                                    align = TextNode.ALeft)
            
            start_game = OnscreenText('press space to start game!', fg = (255,255,255,1), 
                                    scale = 0.1, shadow = (0,0,255,1), 
                                    parent = base.a2dTopLeft, pos = (0.7, -1), 
                                    align = TextNode.ALeft)
            
            self.startText.append(logo)
            self.startText.append(welcome)
            self.startText.append(show_menu)
            self.startText.append(start_game)
        
        q_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.asciiKey(b"q"))
        space_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.space())
        
        self.menuStart = True
        if q_down or space_down:
            self.start = False
            self.escapeStart = True
            for text in self.startText: text.destroy()
        if space_down: 
            self.menuStart = False
            self.addTasks(task)
            
        return task.cont
        
    
    def countdown(self, task):
        #display countdown before game starts
        taskMgr.remove('start')
        
        dt = globalClock.getDt()
        self.timeDelay += dt
        interval = self.wait/3
        
        #sound effect
        if self.counting:
            self.cdMusic.play()
            self.counting = False
        
        if self.timeDelay < interval*1:
            display = displayBigText('3', (1.3,-1), (255,255,255,1), (255,0,0,1))
            self.countdowns.append(display)
        elif self.timeDelay < interval*2:
            for display in self.countdowns: display.destroy()
            display = displayBigText('2', (1.3,-1), (255,255,255,1), (255,255,0,1))
            self.countdowns.append(display)
        elif self.timeDelay < interval*3:
            for display in self.countdowns: display.destroy()
            display = displayBigText('1', (1.3,-1), (255,255,255,1), (0,255,0,1))
            self.countdowns.append(display)
        elif self.timeDelay < interval*4:
            for display in self.countdowns: display.destroy()
            display = displayBigText('GO!', (1.1,-1), (255,255,255,1))
            self.countdowns.append(display)
        elif self.timeDelay > interval*4:
            for display in self.countdowns: display.destroy()
            self.playRaceMusic = True
        
        return task.cont
        
    def pause(self, fromFunction = None):
        self.paused = not self.paused
            
        if self.paused == True:
            if fromFunction == None: #not from menu
                displayPause = displayBigText('PAUSED', (0.85, -1),  (255,255,255,1))
                self.isPaused.append(displayPause)
                self.OSimageText.append(displayPause)
            
            self.addMove -= 1
            taskMgr.remove("move")
            taskMgr.remove("moveSim")
            taskMgr.remove("countdown")
            
        else: #unpause
            if fromFunction == None: 
                for item in self.isPaused: item.destroy()
            
            if self.addMove > 0: return
            self.addMove += 1
            
            taskMgr.add(self.move, "move")
            taskMgr.add(self.moveSim, "moveSim")
            taskMgr.add(self.countdown, 'countdown')
            
    def menuToggle(self, keyInput):
        #display menu of key instructions
        
        taskMgr.remove('start')
        for text in self.startText: text.destroy()
        
        yIncr = -0.1
        directions = [ 'esc: quit program', 'Q: view menu', 'E: escape menu', 
                        'P: pause/unpause', 'Up/Down: move Mario forward/backward',
                        "Right/Left: change Mario's direction", 'A/S: rotate camera' ]
        
        if keyInput == 'display':
            self.menuCount += 1
            if self.menuCount > 1: return
            
            self.paused = False
            self.pause('menu')
           
            title = displaySmallText('Mario Kart Key Legend', (0.75,-0.1), 
                                    (255,255,255,1))
            self.lines = [ title ]
            self.OSimageText.append(title)
            
            for i in range(2,len(directions)+2):
                y = yIncr*i
                
                line = displaySmallText(directions[i-2], (0.1,y), (255,255,255,0.75))
                self.lines.append(line)
                self.OSimageText.append(line)
            
            #access menu from start screen
            if self.menuStart:
                line = displaySmallText('press E to start game!', (0.8,-1.5), 
                                        (255,255,0,1)) 
                self.lines.append(line) 
                self.OSimageText.append(line) 
                self.menuStart = False
                  
        if keyInput == 'remove':
            #escape menu
            self.menuCount = 0
            self.paused = True
            self.pause('menu')
            for line in self.lines:
                line.destroy()
            
            self.straightRoad()
            self.displayLives()
            # taskMgr.add(self.moveSim, 'moveSim')
            # taskMgr.add(self.countdown, 'countdown')
            # taskMgr.add(self.move, "move")
            taskMgr.add(self.mapPrev, 'map')
            taskMgr.add(self.takeLives, 'lives')
            taskMgr.add(self.moveCam, 'cam')
        
    def gameOver(self):
        self.gameover = True
        if self.victory == False and self.loss == False:
            gameText = displayBigText('GAME OVER', (0.65, -1),  (255,255,255,1))
            self.OSimageText.append(gameText)
            escText = displaySmallText('press esc to quit program', (0.8,-1.2), (255,255,255,0.7))
            self.OSimageText.append(escText)
    
    def leaderboard(self):
        #remove everything else on the screen
        taskMgr.remove('moveSim')
        taskMgr.remove("move")
        taskMgr.remove('map')
        for child in render.getChildren():
            child.removeNode()
        for item in self.OSimageText:
            item.destroy()
        
        #characters that didn't finish
        if self.marioFinishTime == 0: 
            self.marioFinishTime = roundtoThou(self.marioRaceTime)
        if self.yoshiFinishTime == 0: 
            self.yoshiFinishTime = roundtoThou(self.yoshiRaceTime)
        
        leaderB = displayBigText('LEADERBOARD', (0.45, -0.3), (255,255,0,1))
        firstPlace = displaySmallText('1st:', (0.5, -0.5), (255,255,0,1))
        secondPlace = displaySmallText('2nd:', (0.5, -0.6), (255,255,0,1))
        
        if self.marioFinishTime <= self.yoshiFinishTime:
            marioY = -0.5
            yoshiY = -0.6
        else:
            marioY = -0.6
            yoshiY = -0.5
        
        marioRight = displaySmallText('Mario (User)', (0.8, marioY), (255,255,0,1))
        marioLeft = displaySmallText(str(self.marioFinishTime), (1.8, marioY), (255,255,0,1))
        yoshiRight = displaySmallText('Yoshi (Computer)', (0.8, yoshiY), (255,255,0,1))
        marioLeft = displaySmallText(str(self.yoshiFinishTime), (1.8, yoshiY), (255,255,0,1))
        escText = displaySmallText('press esc to quit program', (0.7,-1.8), (255,255,255,0.7))
        
        #image from https://mariokart.fandom.com/wiki/Mario
        image = OnscreenImage(image = 'images/leaderboardmario.png', pos = (0.01,0,-0.2), scale = 0.4)

game = Game()
game.run()

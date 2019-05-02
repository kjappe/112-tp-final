#main file of the circular track (hard mode), all functions controlling user/computer players

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

def displaySmallText(txt, position, color, shad = None):
    size = 0.1
    display = OnscreenText(text = txt, fg = color, scale = size, shadow = shad, 
                        parent=base.a2dTopLeft, pos=position, align=TextNode.ALeft)
    return display


def distance(x1,y1,x2,y2):
    return ( (x1-x2)**2 + (y1-y2)**2 )**0.5

def roundtoThou(n):
    return math.ceil(n * 1000.0)/1000.0

class Game(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)
        
        #countdown sound file from https://www.youtube.com/watch?v=KOoCEIwswYg
        self.cdMusic = loader.loadSfx("sounds/countdown.ogg")
        #race sound file from https://www.youtube.com/watch?v=eawQqkq8ROo
        self.rMusic = loader.loadSfx("sounds/race.ogg")
        
        self.r_1 = 700
        self.r_2 = 900
        self.rad_avg = (self.r_1 + self.r_2) / 2
        self.rad_incr = (self.r_2 - self.r_1) / 3
        
        #window and camera
        self.win.setClearColor((0, 0, 0, 1))
        self.startPos = LPoint3f(100, 50, 0)
        self.disableMouse()
        self.x = self.startPos.getX()
        self.y = self.startPos.getY()
        self.z = 15
        self.camera.setPos(self.r_1 + self.rad_incr, 10, 300)
        self.camera.setH(0)
        self.camMaxDist = 180
        self.camMinDist = 150
        
        #mario character (user player)
        #3d mario model file from past tp, with permission:
        #https://github.com/Kabartchlett/15-112-Term-Project
        self.mario = Actor("models/MarioKart")
        self.scale = 7
        self.mario.setScale(self.scale)
        self.mario.setH(self.mario, 0)
        self.mario.reparentTo(render)
        self.marioX = 3
        self.marioY = self.startPos.getY() /3
        self.marioZ = 11
        self.mario.setPos(self.r_1 + self.rad_incr,-40,15)
        self.mario.y_speed = -30
        self.mario.h_speed = 0
        self.mario.raceTime = 0
        self.mario.finishTime = 0
        self.drifted = False
        self.mario.numFellOff = 0
        self.mario.falling = False
        self.mario.startFallTime = None
        self.mario.startFallPos = None
        self.mario.gameover = False
        self.mario_lapText = None
        self.mario.crossed = False
        self.mario.mush = False
        self.mario.megamush = False
        self.mario.bananaSpin = False
        self.mario.preSpinAngle = self.mario.getH()
        self.mario.lap = 1
        self.mario.doubleMush = False
        
        #floater method from roaming ralph:
        #https://github.com/panda3d/panda3d/tree/master/samples/roaming-ralph
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.mario)
        self.floater.setZ(2)
        
        self.center = NodePath(PandaNode("center"))
        self.center.setZ(0)
        self.center.setZ(0)
        self.center.setZ(15)
        
        #computer player
        #3d yoshi model file from past tp, with permission:
        #https://github.com/Kabartchlett/15-112-Term-Project
        self.yoshi = Actor("models/YoshiKart")
        self.yoshi.setScale(self.scale)
        self.yoshi.setH(self.yoshi, 20)
        self.yoshi.reparentTo(render)
        self.yoshiX = 3
        self.yoshiY = self.startPos.getY() *(2/3)
        self.yoshiZ = 10
        self.yoshi.setPos(self.r_1 + 2*self.rad_incr,-40,15)
        self.yoshi.y_speed = -25
        self.yoshi.h_speed = 0
        self.AIadjust = 60
        self.yoshi.raceTime = 0
        self.yoshi.finishTime = 0
        self.yoshi.numFellOff = 0
        self.yoshi.falling = False
        self.yoshi.startFallTime = None
        self.yoshi.startFallPos = None
        self.yoshiStartH = None
        self.yoshi.gameover = False
        self.yoshi_lapText = None
        self.yoshi.crossed = False
        self.yoshi.mush = False
        self.yoshi.megamush = False
        self.yoshi.bananaSpin = False
        self.yoshi.preSpinAngle = self.yoshi.getH()
        self.yoshi.lap = 1
        self.yoshi.doubleMush = False
        
        #statuses
        self.victory = False
        self.loss = False
        self.menuCount = 0
        self.paused = False
        self.addMove = 1
        self.timeDelay = 0
        self.start = True
        self.escapeStart = False
        self.menuStart = True
        self.charFin = True
        self.counting = True
        self.playing = True
        self.playRaceMusic = False
        
        #data init
        self.vDataRows = 100
        self.finalX = self.x
        self.lines = []
        self.isPaused = []
        self.wait = 10
        self.countdowns = []
        self.startText = []
        self.cirNodePath = None
        self.OSimageText = []
        self.timeCharFin = None
        self.lives = []
        
        
        #collision with items init
        from itemCir import Item
        self.itemClass = Item(self)
        
        #key events
        self.accept('escape', sys.exit)
        self.accept('q', self.menuToggle, ['display'])
        self.accept('e', self.menuToggle, ['remove'])
        self.accept('p', self.pause)
        
        #tasks
        if self.start:
            taskMgr.add(self.startScreen, 'start')
    
    def addTasks(self,task):
        self.circularRoad()
        self.displayLives()
        self.displayLaps()
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
    
    def circularRoad(self):
        #geom format and data
        z = 15
        points = self.vDataRows // 2 #one circle
        #x = rcos(t)
        #y = rsin(t)
        t_incr = (2*math.pi) / points
        
        format = GeomVertexFormat.getV3n3c4t2()
        vData = GeomVertexData('cRoad', format, Geom.UHStatic)
        vData.setNumRows(2*self.vDataRows)
        
        vertex = GeomVertexWriter(vData, 'vertex')
        normal = GeomVertexWriter(vData, 'normal')
        color = GeomVertexWriter(vData, 'color')
        texcoord = GeomVertexWriter(vData, 'texcoord')
        
        for i in range(self.vDataRows):
            angle = t_incr * i
            x_1 = self.r_1 * math.cos(angle)
            y_1 = self.r_1 * math.sin(angle)
            
            x_2 = self.r_2 * math.cos(angle)
            y_2 = self.r_2 * math.sin(angle)
            
            vertex.addData3f(x_1, y_1, z)
            vertex.addData3f(x_2, y_2, z)
            
            for n in range(2):
                normal.addData3f(0,0,z)
            
            if i > self.vDataRows/2 - 2: #finish line
                for n in range(2):
                    color.addData4f(255,0,0,1)
            elif i%2 == 0: #rainbow road
                color.addData4f(0,255,255,1)
                color.addData4f(0,255,0,1)
                color.addData4f(255,255,0,1)
                color.addData4f(255,0,255,1)
            
            texcoord.addData2f(x_1,y_1)
            texcoord.addData2f(x_2,y_2)
        
        #geom primitives
        cRoad = GeomTristrips(Geom.UHStatic)
        cRoad.add_consecutive_vertices(0,2*self.vDataRows)
        cRoad.close_primitive()
        
        #connect data and primitives
        cirGeom = Geom(vData)
        cirGeom.addPrimitive(cRoad)
        
        cirNode = GeomNode('geomNode')
        cirNode.addGeom(cirGeom)
        
        self.cirNodePath = render.attachNewNode(cirNode)
        
        self.cirNodePath.set_two_sided(True)
        
    def checkCharCol(self):
        if abs(self.yoshi.getX() - self.mario.getX()) < 10 and \
            abs(self.yoshi.getY() - self.mario.getY()) < 10 and \
            abs(self.yoshi.getZ() - self.mario.getZ()) < 10:
                self.collideYoshi()
    
    def collideYoshi(self):
        #altered use of conservation of momentum
        if self.mario.getH() != 0: mario_sign = self.mario.getH() / abs(self.mario.getH())
        else: mario_sign = 0
        if self.yoshi.getH() != 0: yoshi_sign = self.yoshi.getH() / abs(self.yoshi.getH())
        else: yoshi_sign = 0
        
        self.mario.setH(self.mario.getH() + mario_sign*15)
        self.yoshi.setH(self.yoshi.getH() - mario_sign*15)
        
    def isOffRoad(self, player):
        distFromCen = distance(0,0,player.getX(), player.getY())
        
        return distFromCen < self.r_1 or distFromCen > self.r_2
    
    def almostOffRoad(self, player):
        #for computer player, detect when almost off the road
        distFromCen = distance(0,0,player.getX(), player.getY())
        
        inner = ( distFromCen > self.r_1 and distFromCen < self.r_1 + 30 )
        outer = ( distFromCen < self.r_2 and distFromCen > self.r_2 - 30 )
        
        return inner or outer
    
    def checkItemCol(self,player):
        #checks if player ran into an item box
        for i in range(len(self.itemClass.items)):
            items = self.itemClass.items[i]
            if self.itemClass.itemsPresent[i] and abs(items.getX() - player.getX()) <= 10 and\
                    abs(items.getY() - player.getY()) <= 10 and\
                    abs(items.getZ() - player.getZ()) <= 5:
                self.itemClass.collideItem(items, i, player)
    
    def checkBananaCol(self,player):
        #makes player react to running into a banana
        
        #banana collision detection
        for i in range(len(self.itemClass.bananas)):
            banana = self.itemClass.bananas[i]
            if self.itemClass.bananaPresent[i] and abs(banana.getX() - player.getX()) <= 10 and\
                    abs(banana.getY() - player.getY()) <= 10 and\
                    abs(banana.getZ() - player.getZ()) <= 10:
                self.itemClass.bananaReact(banana, i, player)
                player.preSpinAngle = player.getH()
        
        #spin player
        if player.bananaSpin and globalClock.getFrameTime() < \
                            self.itemClass.beginSpin + self.itemClass.spinTime:
            player.h_speed = 600
            player.y_speed = 0

        #end spin
        if player.bananaSpin and (abs(globalClock.getFrameTime() - (self.itemClass.beginSpin + self.itemClass.spinTime)) < 1):
            player.bananaSpin = False
            player.h_speed = 0
            if player == self.yoshi: player.y_speed = -25
            elif player == self.mario: player.y_speed = -30
            player.setH(player.preSpinAngle)
                
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
    
    def checkFellOff(self, player):
        #checks if the player fell off the road
        if self.isOffRoad(player) and not player.falling:
            player.numFellOff += 1
            player.startFallTime = globalClock.getFrameTime()
            player.startFallPos = player.getPos()
            if player == self.yoshi: self.yoshiStartH = self.yoshi.getH()
            player.falling = True
            if player.numFellOff > 2:
                if player == self.yoshi: player.gameover = True
                if player == self.mario: self.gameOver()
    
    def checkFinishLine(self,player):
        #checks if the player crossed the finish line
        if player.getX() > self.r_1 and player.getX() < self.r_2 and \
            abs(player.getY()) < 30 and player.getZ() >= 15 and not player.crossed:
            player.lap += 1
            player.crossed = True
            
            if player.lap > 3: #final lap completed
                player.finishTime = roundtoThou(player.raceTime)
                
                if player == self.mario:
                    self.victory = True
                    if self.loss == False and self.mario.gameover == False:
                        vic = displayBigText('VICTORY!', (0.8, -1),  (255,255,0,1))
                        self.OSimageText.append(vic)
                        escText = displaySmallText('press esc to quit program', (0.8,-1.2),
                                                    (255,255,255,0.7))
                        self.OSimageText.append(escText)
                elif player == self.yoshi:
                    self.loss = True
                    escText = displaySmallText('press esc to quit program', (0.8,-1.2), (255,255,255,0.7))
                    self.OSimageText.append(escText)
                    if self.mario.gameover == False and self.victory == False:
                        compwins = displayBigText('COMPUTER WINS', (0.4, -1),  (255,0,0,0.5))
                        self.OSimageText.append(compwins)
    
    def moveSim(self,task):
        
        dt = globalClock.getDt()
        self.timeDelay += dt
        
        h_speed = self.yoshi.h_speed
        y_speed = self.yoshi.y_speed
        z_speed = 10
        
        #checks for banana collision
        self.checkBananaCol(self.yoshi)
        
        #checks for item collision
        self.checkItemCol(self.yoshi)
        
        #adjust angle if almost run off road (AI)
        if self.almostOffRoad(self.yoshi):
            distFromCen = distance(0,0,self.yoshi.getX(), self.yoshi.getY())
            if distFromCen > self.r_1 and distFromCen < self.r_1 + 30:
                h_speed += self.AIadjust
            elif distFromCen < self.r_2 and distFromCen > self.r_2 - 30:
                h_speed -= self.AIadjust
        
        #change position, angle
        dh = h_speed * dt
        dy = y_speed * dt
        dz = z_speed * dt
        if self.timeDelay > self.wait:
            self.yoshi.raceTime += dt
            self.yoshi.setH(self.yoshi.getH() + dh)
            self.yoshi.setY(self.yoshi, dy)
        
        #fell off road
        self.checkFellOff(self.yoshi)
                
        if self.yoshi.falling:
            self.yoshi.setZ(self.yoshi.getZ() - dz)
            self.yoshi.y_speed = 0
            self.resetPreFallPos(self.yoshi, self.yoshi.startFallPos)
        
        #crossed finish line
        self.checkFinishLine(self.yoshi)
        
        if self.yoshi.crossed: self.displayLaps(self.yoshi)
        
        #checks for power ups
        self.checkMushEnd(self.yoshi)
        
        
        return task.cont
    
    def move(self, task):
        # print(self.cdMusic.status())
        if self.playing and self.playRaceMusic:
            self.rMusic.play()
            self.playing = False
        
        dt = globalClock.getDt()
        self.timeDelay += dt
        
        #enable moving mario with direction keys
        h_speed = self.mario.h_speed
        y_speed = 0
        z_speed = 50
        x_speed = 0
        h_incr = 80
        y_incr = self.mario.y_speed
        right_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.right())
        left_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.left())
        forward_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.up())
        backward_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.down())
        d_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.asciiKey(b"d"))
        f_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.asciiKey(b"f"))
        
        if right_down:
            h_speed -= h_incr
        if left_down:
            h_speed += h_incr
        if forward_down:
            if d_down or f_down: y_speed += y_incr/3
            else: y_speed += y_incr
        if backward_down:
            if d_down or f_down: y_speed -= y_incr/3
            else: y_speed -= y_incr
        if d_down and self.timeDelay > self.wait:
            self.drifted = True
            self.mario.lookAt(self.center)
            self.mario.setH(self.mario.getH() + 180)
            x_speed -= y_incr * (4/3)
        if f_down and self.timeDelay > self.wait:
            self.drifted = True
            self.mario.lookAt(self.center)
            self.mario.setH(self.mario.getH() + 180)
            x_speed += y_incr * (4/3)
        if not d_down and not f_down and self.drifted and self.timeDelay > self.wait:
            self.drifted = False
            self.mario.setH(self.mario.getH() + 90)
        
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
            self.mario.raceTime += dt
            self.mario.setH(self.mario.getH() + dh)
            self.mario.setY(self.mario, dy)
            self.mario.setX(self.mario, dx)
        
        #mario and yoshi collision
        self.checkCharCol()
        
        #fell off road
        self.checkFellOff(self.mario)
                
        if self.mario.falling:
            self.mario.setZ(self.mario.getZ() - dz)
            self.mario.y_speed = 0
            self.resetPreFallPos(self.mario, self.mario.startFallPos)
        
        #crossed finish line
        self.checkFinishLine(self.mario)
        
        if self.mario.crossed: self.displayLaps(self.mario)
        
        #show leaderboard if someone completed 3 laps or gameover
        if ( self.mario.gameover or self.victory or self.loss ) and self.charFin:
            self.timeCharFin = globalClock.getFrameTime()
            self.charFin = False
        
        if self.timeCharFin != None and globalClock.getFrameTime() > self.timeCharFin + self.wait/2:
            self.leaderboard()
        
        #checks for power ups
        self.checkMushEnd(self.mario)
        
        return task.cont
        
            
    def moveCam(self, task):
        dt = globalClock.getDt()
        
        #enable camera spinning around mario using a,s,w,x,k,l keys
        cam = 0
        camSpeed = 700
        vert = 0
        hor = 0
        a_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.asciiKey(b"a"))
        s_down = base.mouseWatcherNode.isButtonDown(KeyboardButton.asciiKey(b"s"))
        
        
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
        
        self.camera.setH(self.mario.getH())
        self.camera.setZ(self.mario.getZ()+25)
        
        self.camera.lookAt(self.floater)
        
        return task.cont
    
    def resetPreFallPos(self, player, pos):
        #place player back on the road
        
        if player.startFallTime != None and not player.gameover and globalClock.getFrameTime() > player.startFallTime + self.wait/4:
            player.falling = False
            
            if distance(0,0,player.getX(), player.getY()) >= self.r_2: sign = -1 #outer
            else: sign = 1 #inner
            
            if player.getX() < 0: adjustX = -70 *sign
            else: adjustX = 70 *sign
            if player.getY() < 0: adjustY = -70 *sign
            else: adjustY = 70 *sign
            
            player.setPos(pos + (adjustX, adjustY, 0))
            if player == self.mario: self.mario.y_speed = -30
            elif player == self.yoshi:
                self.yoshi.y_speed = -25
                self.yoshi.setH(self.mario.getH())
        
    
    def displayLaps(self, player=None):
        #display the lap number each player is on
        
        #past finish line
        if player != None and player.getX() > self.r_1 and player.getX() < self.r_2 and \
            abs(player.getY()) > 30 and player.getZ() >= 15:
            player.crossed = False
        
        #destroy previous lap count
        if self.mario_lapText != None: self.mario_lapText.destroy()
        if self.yoshi_lapText != None: self.yoshi_lapText.destroy()
        
        #new lap count
        self.mario_lapText = OnscreenText(text = 'Lap: ' + str(self.mario.lap), fg = (255,0,0,1), 
                                        scale =  0.05, parent=base.a2dTopLeft, pos=(2.5,-0.15), 
                                        align=TextNode.ALeft)
        self.yoshi_lapText = OnscreenText(text = 'Lap: ' + str(self.yoshi.lap), fg = (0,255,0,1), 
                                        scale =  0.05, parent=base.a2dTopLeft, pos=(2.5,-0.25), 
                                        align=TextNode.ALeft)
        self.OSimageText.append(self.mario_lapText)
        self.OSimageText.append(self.yoshi_lapText)
    
    def displayLives(self):
        #display the number of lives user player has left
        
        livesText = displaySmallText('lives:', (0.1,-0.15), (255,255,255,1))
        self.OSimageText.append(livesText)
        #images made in preview
        self.life1 = OnscreenImage(image = 'images/life.png', pos = (-0.9,0,0.87), scale = 0.03)
        self.life2 = OnscreenImage(image = 'images/life.png', pos = (-0.8,0,0.87), scale = 0.03)
        self.life3 = OnscreenImage(image = 'images/life.png', pos = (-0.7,0,0.87), scale = 0.03)
        self.OSimageText.append(self.life1)
        self.OSimageText.append(self.life2)
        self.OSimageText.append(self.life3)
    
    def takeLives(self, task):
        if self.mario.numFellOff == 1: self.life3.destroy()
        if self.mario.numFellOff == 2: self.life2.destroy()
        if self.mario.numFellOff == 3: self.life1.destroy()
        
        return task.cont
    
    def getPlayerAngle(self, player):
        #get player's current angle wrt the circular track
        x = player.getX()
        y = player.getY()
        
        if x == 0:
            if y<=0: angle = 90
            else: angle = -90
        else: angle = math.degrees(math.atan(abs(y)/abs(x)))
        
        if y<=0 and x<=0: pass #Q1
        elif y<0 and x>0: angle = 180 - angle #Q2
        elif y>0 and x<0: angle = -angle #Q3
        elif y>0 and x>0: angle = -180 + angle #Q4
        
        return angle
    
    def mapPrev(self,task):
        #show map in corner with all player's positions
        
        radius = 0.085
        mapX = 1
        mapY = 0.8
        #image made in preview
        mapP = OnscreenImage(image = 'images/map.png', pos = (mapX,0,mapY), scale = 0.1)
        self.OSimageText.append(mapP)
        
        marioAngle = self.getPlayerAngle(self.mario)
        marioX = mapX + radius*math.cos(math.radians(marioAngle))
        marioY = mapY + radius*math.sin(math.radians(marioAngle))
        
        yoshiAngle = self.getPlayerAngle(self.yoshi)
        yoshiX = mapX + radius*math.cos(math.radians(yoshiAngle))
        yoshiY = mapY + radius*math.sin(math.radians(yoshiAngle))
        
        finishX = mapX + radius*math.cos(math.radians(180))
        finishY = mapY + radius*math.sin(math.radians(180))
        
        #images made in preview
        marioSym = OnscreenImage(image = 'images/mariosym.png', 
                                pos = (marioX,0,marioY), scale = 0.01)
        yoshiSym = OnscreenImage(image = 'images/yoshisym.png', 
                                pos = (yoshiX,0,yoshiY), scale = 0.01)
        finishSym = OnscreenImage(image = 'images/finishsym.png', 
                                pos = (finishX,0,finishY), scale = 0.01)
        
        self.OSimageText.append(marioSym)
        self.OSimageText.append(yoshiSym)
        self.OSimageText.append(finishSym)
        
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
        
        if q_down: self.menuStart = True
        if q_down or space_down:
            self.start = False
            self.escapeStart = True
            for text in self.startText: text.destroy()
        if space_down: 
            self.addTasks(task)
            
        return task.cont
        
    
    def countdown(self, task):
        #display countdown before game starts
        taskMgr.remove('start')
        
        dt = globalClock.getDt()
        self.timeDelay += dt
        interval = self.wait/3
        
        #countdown sound effect
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
        
        #pause countdown music if playing
        if self.cdMusic.status() == self.cdMusic.PLAYING:
            self.cdMusicTime = self.cdMusic.getTime()
            self.cdMusic.setPlayRate(0)
        
        yIncr = -0.1
        directions = [ 'esc: quit program', 'Q: view menu', 'E: escape menu', 
                        'P: pause/unpause', 'Up/Down: move Mario forward/backward',
                        "Right/Left: change Mario's direction", 'A/S: rotate camera',
                        'D/F: drift Mario forwards/backwards', 
                        "during drift, use Up/Down in place of Right/Left" ]
        
        if keyInput == 'display':
            self.menuCount += 1
            if self.menuCount > 1: return
            
            self.paused = False
            self.pause('menu')
           
            title = displaySmallText('Mario Kart Key Legend', (0.75,-0.1), 
                                    (255,255,255,1), (0,0,0,1))
            self.OSimageText.append(title)
            
            self.lines = [ title ]
            
            for i in range(2,len(directions)+2):
                y = yIncr*i
                
                line = displaySmallText(directions[i-2], (0.1,y), (255,255,255,0.75), 
                                        (0,0,0,1))
                self.lines.append(line)
                self.OSimageText.append(line)
            
            #access menu from start screen
            if self.menuStart:
                line = displaySmallText('press E to start game!', (0.8,-1.5), 
                                        (255,255,0,1), (0,0,0,1)) 
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
            
            self.circularRoad()
            self.displayLives()
            self.displayLaps()
            taskMgr.add(self.moveSim, 'moveSim')
            taskMgr.add(self.countdown, 'countdown')
            taskMgr.add(self.move, "move")
            taskMgr.add(self.mapPrev, 'map')
            taskMgr.add(self.takeLives, 'lives')
            taskMgr.add(self.moveCam, 'cam')
        
    def gameOver(self):
        self.mario.gameover = True
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
        
        leaderB = displayBigText('LEADERBOARD', (0.45, -0.3), (255,255,0,1))
        firstPlace = displaySmallText('1st:', (0.5, -0.5), (255,255,0,1))
        secondPlace = displaySmallText('2nd:', (0.5, -0.6), (255,255,0,1))
        
        #characters that didn't finish
        if self.mario.finishTime == 0:
            self.mario.finishTime = roundtoThou(self.mario.raceTime)
        if self.yoshi.finishTime == 0:
            self.yoshi.finishTime = roundtoThou(self.yoshi.raceTime)
        
        if self.mario.finishTime <= self.yoshi.finishTime:
            marioY = -0.5
            yoshiY = -0.6
        else:
            marioY = -0.6
            yoshiY = -0.5
        
        marioRight = displaySmallText('Mario (User)', (0.8, marioY), (255,255,0,1))
        marioLeft = displaySmallText(str(self.mario.finishTime), (1.8, marioY), (255,255,0,1))
        yoshiRight = displaySmallText('Yoshi (Computer)', (0.8, yoshiY), (255,255,0,1))
        marioLeft = displaySmallText(str(self.yoshi.finishTime), (1.8, yoshiY), (255,255,0,1))
        escText = displaySmallText('press esc to quit program', (0.7,-1.8), (255,255,255,0.7))
        
        #image from https://mariokart.fandom.com/wiki/Mario
        image = OnscreenImage(image = 'images/leaderboardmario.png', pos = (0.01,0,-0.2), scale = 0.4)
        
        
        
    

game = Game()
game.run()

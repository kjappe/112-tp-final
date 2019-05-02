#contains some functions and info about item boxes for circular path

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
import sys
import math
import random

def selectItem():
    items = [ 'mushroom', 'mega mushroom', 'banana' ]
    # items = [ 'banana' ]
    return random.choice(items)



class Item(object):
    def __init__(self, game):
        
        self.game = game
        
        #init
        self.startPos = LPoint3f(100, 50, 0)
        self.x = self.startPos.getX()
        self.y = self.startPos.getY()
        self.z = 15
        
        #physical items
        #3d banana model file from past tp, with permission:
        #https://github.com/Kabartchlett/15-112-Term-Project
        self.bananaModel = loader.loadModel('models/bananaModel')
        # self.bananaModel.setPos(self.game.mario.getPos() + (0,0,10))
        
        #statuses
        self.doubleMush = False
        self.doubleMega = False
        
        #data
        self.boostDistance = 1000
        self.mushrooms = []
        self.beginBoostX = Vec3(0,0,0)
        self.mega_mushrooms = []
        self.beginSpin = globalClock.getFrameTime()
        self.spinTime = 3
        self.items = []
        self.itemsPresent = [True for i in range(15)]
        self.bananas = []
        self.bananaPresent = [True for i in range(len(self.bananas))]
        
        self.setItems()
        
    def setItems(self):
        
        #3d item model file from past tp, with permission:
        #https://github.com/Kabartchlett/15-112-Term-Project
        self.item1a = loader.loadModel('models/itemBox')
        self.item2a = loader.loadModel('models/itemBox')
        self.item3a = loader.loadModel('models/itemBox')
        self.item4a = loader.loadModel('models/itemBox')
        self.item5a = loader.loadModel('models/itemBox')
        self.item1b = loader.loadModel('models/itemBox')
        self.item2b = loader.loadModel('models/itemBox')
        self.item3b = loader.loadModel('models/itemBox')
        self.item4b = loader.loadModel('models/itemBox')
        self.item5b = loader.loadModel('models/itemBox')
        self.item1c = loader.loadModel('models/itemBox')
        self.item2c = loader.loadModel('models/itemBox')
        self.item3c = loader.loadModel('models/itemBox')
        self.item4c = loader.loadModel('models/itemBox')
        self.item5c = loader.loadModel('models/itemBox')
        
        self.items.append(self.item1a)
        self.items.append(self.item1b)
        self.items.append(self.item1c)
        self.items.append(self.item2a)
        self.items.append(self.item2b)
        self.items.append(self.item2c)
        self.items.append(self.item3a)
        self.items.append(self.item3b)
        self.items.append(self.item3c)
        self.items.append(self.item4a)
        self.items.append(self.item4b)
        self.items.append(self.item4c)
        self.items.append(self.item5a)
        self.items.append(self.item5b)
        self.items.append(self.item5c)
        
        #get positions for items
        startAngle = 150
        positions = []
        itemsInARow = 3
        numItems = len(self.items) // itemsInARow
        angle_incr = 2*math.pi / numItems
        for i in range(numItems):
            angle = angle_incr * i + startAngle 
            displace = random.randint(0,50)
            radius_1 = self.game.r_1 + ((self.game.r_2 - self.game.r_1) / 4) - displace
            radius_2 = self.game.r_1 + ((self.game.r_2 - self.game.r_1) / 2) - displace
            radius_3 = self.game.r_1 + ((self.game.r_2 - self.game.r_1) * (3/4)) - displace
            
            x_1 = radius_1 * math.cos(angle)
            y_1 = radius_1 * math.sin(angle)
            
            x_2 = radius_2 * math.cos(angle)
            y_2 = radius_2 * math.sin(angle)
            
            x_3 = radius_3 * math.cos(angle)
            y_3 = radius_3 * math.sin(angle)
            
            positions.append( (x_1,y_1) )
            positions.append( (x_2,y_2) )
            positions.append( (x_3,y_3) )
        
        #place items on track
        for i in range(0,len(self.items),3):
            positionA = positions[i]
            positionB = positions[i+1]
            positionC = positions[i+2]
            itemA = self.items[i]
            itemB = self.items[i+1]
            itemC = self.items[i+2]
            
            itemA.reparentTo(render)
            itemB.reparentTo(render)
            itemC.reparentTo(render)
            itemA.setScale(7)
            itemB.setScale(7)
            itemC.setScale(7)
            itemA.setPos(positionA[0], positionA[1], 20)
            itemB.setPos(positionB[0], positionB[1], 20)
            itemC.setPos(positionC[0], positionC[1], 20)
            
    def collideItem(self, item, index, player):
        #choose power up/punishment from collision with item box
        
        itemPos = item.getPos()
        item.removeNode()
        self.itemsPresent[index] = False
        powerUp = selectItem()
        
        if powerUp == 'mushroom':
            if player.mush == True: player.doubleMush = True
            else: player.mush = True
            self.mushroom(player,itemPos)
        elif powerUp == 'mega mushroom':
            player.megamush = True
            self.megaMushroom(player,itemPos)
        elif powerUp == 'banana':
            self.bananaSpin = False
            self.banana(player, itemPos)
        
    
    def mushroom(self, player, pos= (0,0,0)):
        #increase speed
        
        self.beginBoostX = self.game.mario.getX()
        if player.mush: #begin effect
            if player == self.game.mario:
                #mushroom image from https://mariokart.fandom.com/wiki/Mushroom_(item)
                mushroom = OnscreenImage(image = 'images/mushroom.png', pos = (-1,0,0.7),
                                        scale = 0.1 )
                self.mushrooms.append(mushroom)
                self.game.OSimageText.append(mushroom)
                if not player.doubleMush: player.y_speed *= 2
                
            if player == self.game.yoshi: 
                self.game.AIadjust *= 2.5
                if not player.doubleMush: player.y_speed *= 1.5
            
            return self.beginBoostX
        
        else: #end effect
            if player == self.game.mario:
                for mushrooms in self.mushrooms: mushrooms.destroy()
                if not player.doubleMush: player.y_speed /= 2
            if player == self.game.yoshi: 
                self.game.AIadjust /= 2.5
                if not player.doubleMush: player.y_speed /= 1.5
            player.doubleMush = False
    
    def megaMushroom(self, player, pos = (0,0,0)):
        #increase size
        
        self.beginBoostX = self.game.mario.getX()
        if player.megamush: #begin effect
            player.setScale(14)
            if player == self.game.mario:
                #mega mushroom image from https://mariokart.fandom.com/wiki/Mega_Mushroom
                mega_mushroom = OnscreenImage(image = 'images/megaMushroom.png', 
                                            pos = (-1,0,0.7), scale = 0.1 )
                self.mega_mushrooms.append(mega_mushroom)
                self.game.OSimageText.append(mega_mushroom)
                
                self.game.camMaxDist = 240
                self.game.camMinDist = 200
                self.game.floater.setZ(1)
            
            if player == self.game.yoshi: 
                self.game.AIadjust *= 2
                
            return self.beginBoostX
        
        else: #end effect
            player.setScale(self.game.scale)
            if player == self.game.mario:
                for mushrooms in self.mega_mushrooms: mushrooms.destroy()
                
                self.game.camMaxDist = 180
                self.game.camMinDist = 150
                self.game.floater.setZ(2)
            
            if player == self.game.yoshi: 
                self.game.AIadjust /= 2
        
    
    def banana(self, player, pos):
        #display banana
        
        #3d banana model file from past tp, with permission:
        #https://github.com/Kabartchlett/15-112-Term-Project
        self.bananaModel = loader.loadModel('models/bananaModel')
        self.bananaModel.setPos(pos + (50,0,1))
        self.bananaModel.reparentTo(render)
        self.bananaModel.setH(-90)
        self.bananaModel.setScale(1)
        self.bananas.append(self.bananaModel)
        self.bananaPresent.append(True)
    
    def bananaReact(self, banana, index, player):
        #make banana disappear after collision
        self.beginSpin = globalClock.getFrameTime()
        banana.removeNode()
        self.bananaPresent[index] = False
        player.bananaSpin = True


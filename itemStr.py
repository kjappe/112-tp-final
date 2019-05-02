#contains some functions and info about item boxes for straight track

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
    items = [ 'mega mushroom', 'mushroom']
    # items = [ 'banana' ]
    return random.choice(items)

class Item(object):
    def __init__(self, game):
        
        self.game = game
        
        #start data
        self.startPos = LPoint3f(100, 50, 0)
        self.x = self.startPos.getX()
        self.y = self.startPos.getY()
        self.z = 15
        
        #physical items
        #3d banana model file from past tp, with permission:
        #https://github.com/Kabartchlett/15-112-Term-Project
        self.bananaModel = loader.loadModel('models/bananaModel')
        self.bananaModel.setPos(self.game.mario.getPos() + (0,0,10))
        
        #statuses
        self.mush_Mario = False
        self.megaMush_Mario = False
        self.mush_Yoshi = False
        self.megaMush_Yoshi = False
        self.bananaSpin_yoshi = False
        self.bananaSpin_mario = False
        self.bananaPresent = False
        self.itemPresent = True
        
        #data init
        self.boostDistance = 900
        self.mushrooms = []
        self.beginBoostX = 0
        self.mega_mushrooms = []
        self.beginSpin = globalClock.getFrameTime()
        self.spinTime = 2.5
        self.items = []
        self.itemsPresent = [True for i in range(10)]
        self.bananas = []
        self.bananaPresent = [True for i in range(len(self.bananas))]
        
        self.setItems()
    
    def setItems(self):
        
        #3d item model file from past tp, with permission:
        #https://github.com/Kabartchlett/15-112-Term-Project
        self.item1 = loader.loadModel('models/itemBox')
        self.item2 = loader.loadModel('models/itemBox')
        self.item3 = loader.loadModel('models/itemBox')
        self.item4 = loader.loadModel('models/itemBox')
        self.item5 = loader.loadModel('models/itemBox')
        self.item6 = loader.loadModel('models/itemBox')
        self.item7 = loader.loadModel('models/itemBox')
        self.item8 = loader.loadModel('models/itemBox')
        self.item9 = loader.loadModel('models/itemBox')
        self.item10 = loader.loadModel('models/itemBox')
        self.items.append(self.item1)
        self.items.append(self.item2)
        self.items.append(self.item3)
        self.items.append(self.item4)
        self.items.append(self.item5)
        self.items.append(self.item6)
        self.items.append(self.item7)
        self.items.append(self.item8)
        self.items.append(self.item9)
        self.items.append(self.item10)
        
        #get positions of item boxes
        positions = []
        numItems = len(self.items)
        x_incr = (self.game.vDataRows*self.x)/numItems
        for i in range(numItems):
            x = x_incr * i + 100
            y = random.randint(10,self.y-10)
            positions.append( (x,y) )
        
        #place item boxes on track
        for i in range(len(self.items)):
            position = positions[i]
            item = self.items[i]
            item.reparentTo(render)
            item.setScale(2)
            item.setPos(position[0], position[1], 11)
    
    
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
                if not player.doubleMush: player.y_speed *= 2.5
                
            
            return self.beginBoostX
        
        else: #end effect
            if player == self.game.mario:
                for mushrooms in self.mushrooms: mushrooms.destroy()
                if not player.doubleMush: player.y_speed /= 2.5
            player.doubleMush = False
    
    def megaMushroom(self, player, pos = (0,0,0)):
        #increase size
        
        self.beginBoostX = self.game.mario.getX()
        if player.megamush: #begin effect
            player.setScale(5)
            if player == self.game.mario:
                #mega mushroom image from https://mariokart.fandom.com/wiki/Mega_Mushroom
                mega_mushroom = OnscreenImage(image = 'images/megaMushroom.png', 
                                            pos = (-1,0,0.7), scale = 0.1 )
                self.mega_mushrooms.append(mega_mushroom)
                self.game.OSimageText.append(mega_mushroom)
                
                self.game.camMaxDist = 45
                self.game.camMinDist = 40
                self.game.floater.setZ(1)
            
                
            return self.beginBoostX
        
        else: #end effect
            player.setScale(self.game.scale)
            if player == self.game.mario:
                for mushrooms in self.mega_mushrooms: mushrooms.destroy()
                
                self.game.camMaxDist = 30
                self.game.camMinDist = 25
                self.game.floater.setZ(2)
            
        
    
    def banana(self, player, pos):
        #display banana
        
        #3d banana model file from past tp, with permission:
        #https://github.com/Kabartchlett/15-112-Term-Project
        self.bananaModel = loader.loadModel('models/bananaModel')
        self.bananaModel.setPos(pos + (200,0,0))
        self.bananaModel.reparentTo(render)
        self.bananaModel.setH(-90)
        self.bananaModel.setScale(0.35)
        self.bananas.append(self.bananaModel)
        self.bananaPresent.append(True)
    
    def bananaReact(self, banana, index, player):
        #make banana disappear after collision
        self.beginSpin = globalClock.getFrameTime()
        banana.removeNode()
        self.bananaPresent[index] = False
        player.bananaSpin = True

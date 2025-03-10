import pygame
from pygame.locals import *
from pacmanFSM import PacmanFSM
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites

class Pacman(Entity):
    def __init__(self, node, nodes):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.fsm = PacmanFSM(self, nodes)
        self.direction = LEFT
        self.setBetweenNodes(self.direction)
        self.nodes = nodes
        
    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(self.direction)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP
    
    def setGhosts(self, ghosts):
        self.ghosts = ghosts

    def setPellets(self, pellets):
        self.pellets = pellets
    
    def setPowerPellets(self, powerPellets):
        self.powerPellets = powerPellets
 
    def update(self, dt):
        self.fsm.update(dt, self.ghosts, self.powerPellets)
        self.sprites.update(dt)

        self.position += self.directions[self.direction] * self.speed * dt
        
        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            direction = self.fsm.get_next_direction(directions, self.ghosts, self.powerPellets, self.pellets)
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target != self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            self.setPosition()

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None    
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

from algorithms import astar, astar_avoid
from constants import *
import random

from vector import Vector2

class PacmanFSM(object):
    def __init__(self, pacman, nodes):
        self.pacman = pacman
        self.nodes = nodes
        self.state = NORMAL
        self.timer = 0
        self.eaten_power_p = set()
        self.num_ppellet_eaten = 0
        self.starttimer = 7
    
    def resetFSM(self):
        self.state = NORMAL
        self.timer = 0
    
    # Update function triggers transitions
    def update(self, dt, ghosts, powerPellets):
        if self.ghost_close(ghosts):
            self.change_state(FLEE)
        elif self.state == FLEE and not self.ghost_close(ghosts):
                self.change_state(NORMAL)
        elif self.pellet_eaten(powerPellets):
            self.change_state(EAT)
            self.timer = 7  
        elif self.state == EAT:
            self.timer -= dt
            if self.timer <= 2 or self.ghost_hunting(ghosts):
                self.change_state(NORMAL)

    # Helper function for changing state
    def change_state(self, new_state):
        if self.state == new_state:
            return
        state_names = {
            NORMAL: "Normal",
            FLEE: "Flee",
            EAT: "Eat",
        }
        print(f"Pacman changing state: {state_names[self.state]} → {state_names[new_state]}")
        self.state = new_state

    # Returns a direction based on state
    def get_next_direction(self, valid_directions, ghosts, powerPellets, pellets):    
        if self.state == NORMAL:
            return self.get_normal_pellets(pellets, valid_directions)
        elif self.state == FLEE:
            return self.get_escape_direction(powerPellets, ghosts, valid_directions)
        elif self.state == EAT:
            return self.get_chase_direction(ghosts, valid_directions)
        
    # Chasing normal pellets using basic goal direction
    def get_normal_pellets(self, pellets, directions):
        goal = self.get_nearby_pellet(pellets)
        return self.goal_direction(directions, goal)
    
    # Targets powerpellets while avoiding ghosts
    def get_escape_direction(self, powerPellets, ghosts, directions):   
        target = self.get_nearby_power_pellet2(powerPellets) if self.num_ppellet_eaten == len(powerPellets) else self.get_nearby_power_pellet(powerPellets)

        if target == None:
            print("Target None in getescape")
            return random.choice(directions)
        
        path = astar_avoid(self.pacman.node, target, ghosts)
        
        if not path or len(path) < 2:
            print("Returning random in escape")
            return random.choice(directions)
           
        next_node = path[1]
        goal = next_node.position - self.pacman.position  
        return self.get_direction(goal)
    
    # Targets closest ghost and hunts it using astar
    def get_chase_direction(self, ghosts, directions):
        target = self.get_nearby_ghost(ghosts)  
        if target is None:
            print("No valid ghost target found!")
            return random.choice(directions)  
        
        path = astar(self.pacman.node, target.target)
        
        if not path or len(path) < 2:
            print("Returning pac-dir in chase")
            return random.choice(directions)

        next_node = path[1]        
        goal = next_node.position - self.pacman.position  
        return self.get_direction(goal)
    
    # Targets closest powerpellet
    def get_pellet_direction(self, powerpellets, directions):
        target = self.get_nearby_power_pellet2(powerpellets) if self.num_ppellet_eaten == len(powerpellets) else self.get_nearby_power_pellet(powerpellets)

        if target is None:
            print("No valid powerpellets found!")
            return random.choice(directions)  
        
        path = astar(self.pacman.node, target)
        
        if not path or len(path) < 2:
            print("Returning pac-dir in chase")
            return random.choice(directions)

        next_node = path[1]        
        goal = next_node.position - self.pacman.position  
        return self.get_direction(goal)

    # Choose the direction that moves toward the goal faster.  
    # Prioritize horizontal movement if the X distance is greater, otherwise, move vertically.
    def get_direction(self, goal):
        if goal.x == 0 and goal.y == 0:
            return self.pacman.direction  

        if abs(goal.x) > abs(goal.y):
            return RIGHT if goal.x > 0 else LEFT
        else:
            return DOWN if goal.y > 0 else UP 

    # Basic goal direction    
    def goal_direction(self, directions, goal):
        distances = []
        for direction in directions:
            distances.append(
                (goal - (self.pacman.position + self.pacman.directions[direction] * TILEWIDTH)).magnitudeSquared()
                )
        index = distances.index(min(distances))
        return directions[index]
    
    # Returns closest normal pellet vector        
    def get_nearby_pellet(self, pellets):
        distances = []
        for p in pellets:
            if p.visible:
                dist = self.pacman.position.distance_to(p.position)
                distances.append((dist, p))
        
        if not distances:
            return self.pacman.target.position
        
        distances.sort(key=lambda x: x[0])

        _, target = distances[0]
        return target.position

    # Returns closest powerpellet node
    # This node is used as target in astar        
    def get_nearby_power_pellet(self, pellets):
        distances = []
        for p in pellets:
            if p in self.eaten_power_p:
                continue  
            dist = self.pacman.position.distance_to(p.position)
            distances.append((dist, p.node))  
        
        if not distances:
            return None

        distances.sort(key=lambda x: x[0])

        _, target = distances[0]
        return target
    
    # Same as above but without checking if p in self.eaten_power_p
    def get_nearby_power_pellet2(self, pellets):
        distances = []
        for p in pellets:
            dist = self.pacman.position.distance_to(p.position)
            distances.append((dist, p.node))  
        
        if not distances:
            return None

        distances.sort(key=lambda x: x[0])

        _, target = distances[0]
        return target
    
    # Returns nearby ghosts node
    def get_nearby_ghost_node(self, ghosts):
        distances = []
        for g in ghosts:
            if self.is_in_home(g):
                continue
            dist = (g.position - self.pacman.position).magnitudeSquared()
            distances.append((dist, g.node))  
         
        distances.sort(key=lambda x: x[0])

        _, target = distances[0]
        return target
    
    # Returns nearby ghosts 
    def get_nearby_ghost(self, ghosts):
        distances = []
        for g in ghosts:
            if self.is_in_home(g):
                continue
            dist = self.pacman.position.distance_to(g.position)
            distances.append((dist, g))  
        
        if not distances:
            return None
        
        distances.sort(key=lambda x: x[0])
        _, target = distances[0]
        return target
     
    # Helper function to check if a ghost is inside home area 
    def is_in_home(self, ghost): # Very hacky, but works
        if ghost.node == ghost.homeNode or ghost.node == ghost.spawnNode:
            return True
        for n in ghost.node.getNeighbors():
            if n == ghost.homeNode or n == ghost.spawnNode:
                return True
        return False


    # Function for when pacman eats a pellet    
    def pellet_eaten(self, powerPellets):
        for pellet in powerPellets[:]:
            if pellet in self.eaten_power_p:
                continue  
            if self.pacman.collideCheck(pellet):
                print("Pellet eaten")
                self.eaten_power_p.add(pellet)
                self.num_ppellet_eaten += 1
                print(self.eaten_power_p)
                return True
        return False 
    
    # Helper function checking if a ghost is within a number of tiles
    def ghost_close(self, ghosts):
        for ghost in ghosts:
            if ghost.mode.current == CHASE:
                if self.pacman.position.is_nearby(ghost.position, 8):
                    return True
        return False
        
    # Helper function checking if a powerpellet is within a number of tiles
    def powerpellet_close(self, powerpellets):
        for ppellet in powerpellets:
            if self.pacman.position.is_nearby(ppellet.position, 10):
                return True
        return False
        
    # Helper function checking if a ghost is hunting
    def ghost_hunting(self, ghosts):
        for g in ghosts:
            if g.mode.current == CHASE:
                return True
        return False
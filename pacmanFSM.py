from algorithms import astar, dijkstra_avoid
from constants import *
from heapq import heappop, heappush

class PacmanFSM(object):
    def __init__(self, pacman, nodes):
        self.pacman = pacman
        self.nodes = nodes
        self.state = NORMAL
        self.timer = 0
        self.reversed = False 

    def update(self, dt, ghosts, pellets):
        if self.state == NORMAL:
            # Transition to EAT state when a pellet is eaten
            if self.pellet_eaten(pellets) and self.state != EAT:
                self.change_state(EAT)
                self.timer = 7
            
            # Transition to FLEE state if ghosts are nearby
            elif self.ghost_nearby(ghosts): 
                self.change_state(FLEE)

        elif self.state == FLEE:
            # Transition back to NORMAL state when no ghosts are nearby
            if not self.ghost_nearby(ghosts):
                self.change_state(NORMAL)
            # Transition to EAT state if a pellet is eaten while fleeing
            elif self.pellet_eaten(pellets) and self.state != EAT:
                self.change_state(EAT)
                self.timer = 7

        elif self.state == EAT:
            if self.ghost_nearby(ghosts):
                self.change_state(FLEE)
            else:
                # Timer countdown while in EAT state
                self.timer -= dt
                if self.timer <= 1: 
                    #Probably near ghosts so flee a bit before they chase you again
                    self.change_state(FLEE)

    def change_state(self, new_state):
        state_names = {
            NORMAL: "Normal",
            FLEE: "Flee",
            EAT: "Eat"
        }
        print(f"Pacman changing state: {state_names[self.state]} → {state_names[new_state]}")
        self.state = new_state

    def get_next_direction(self, valid_directions, ghosts, pellets):
        if self.state == NORMAL:
            return self.get_target_direction(pellets, valid_directions)  # Move towards goal
        elif self.state == FLEE:
            return self.get_escape_direction(valid_directions, ghosts)  # Move away from ghosts
        elif self.state == EAT:
            return self.get_chase_direction(ghosts, valid_directions)  # Chase something
        return self.pacman.direction  # Default to current direction

    def get_target_direction(self, pellets, directions):
        target = self.getNearbyPellet(pellets)
        path = astar(self.pacman.node, target)

        if not path or len(path) < 2:
            return self.pacman.goalDirection(directions)
           
        next_node = path[1]  
    
        goal = next_node.position - self.pacman.node.position
        self.pacman.goal = next_node.position
        
        return self.getDirection(goal)

    def get_escape_direction(self, directions, ghosts):   
        # Negative vector of nearest ghost
        nearest_ghost = self.getNearbyGhost(ghosts)
        distances = []
        for direction in directions:
            vec = (
                nearest_ghost.position - self.pacman.position + self.pacman.directions[direction] * TILEWIDTH
            )
            distances.append(- vec.magnitudeSquared())
        index = distances.index(max(distances))
        return directions[index]
       
    def get_escape_direction2(self, directions, pellets, ghosts):
        target = self.getNearbyPellet(pellets)
        path = dijkstra_avoid(self.pacman.node, target, ghosts)

        if not path or len(path) < 2:
            return self.pacman.goalDirection(directions)
           
        next_node = path[1]  
    
        goal = next_node.position - self.pacman.node.position
        self.pacman.goal = next_node.position
        
        return self.getDirection(goal)

    def get_chase_direction(self, ghosts, directions):
        target = self.getNearbyGhost(ghosts)      
        path = astar(self.pacman.node, target)
        
        if not path or len(path) < 2:
            return self.pacman.goalDirection(directions)
           
        next_node = path[1]  
    
        goal = next_node.position - self.pacman.node.position
        self.pacman.goal = next_node.position
        
        return self.getDirection(goal)
    
    def getDirection(self, goal):
        if abs(goal.x) > abs(goal.y):
            if goal.x > 0:
                return RIGHT  
            else:
                return LEFT  
        else:
            if goal.y > 0:
                return DOWN  
            else:
                return UP 
        

    def getNearbyPellet(self, pellets):
        distances = []
        for p in pellets:
            if p.visible:
                dist = (p.position - self.pacman.position).magnitudeSquared()
                heappush(distances, (dist, p.node))
        if not distances:
            return self.pacman.target
            
        _, target = heappop(distances)
        return target
    
    def getNearbyGhost(self, ghosts):
        distances = []
        for g in ghosts:
            # Only chase ghosts in state FREIGHT
            if g.mode.current == FREIGHT: 
                dist = (g.position - self.pacman.position).magnitudeSquared()
                heappush(distances, (dist, g.node))
        
        if not distances:
            return self.pacman.target
        
        _, target = heappop(distances)
        return target

    def ghost_nearby(self, ghosts):
        for ghost in ghosts:
            if ghost.mode.current == CHASE:
                if self.within_radius(self.pacman.position, ghost.position):
                    return True
        return False

    def pellet_eaten(self, pellets):
        for pellet in pellets:
            if self.pacman.collideCheck(pellet) and pellet.visible:
                print("pellet eaten")
                return True
        return False 

    def within_radius(self, vec1, vec2, radius=120):
        return (vec1 - vec2).magnitudeSquared() <= radius**2
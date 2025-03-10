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
        self.powerP = set()
    
    def update(self, dt, ghosts, powerPellets):
        if self.state == NORMAL:
            # Transition to EAT state when a pellet is eaten
            if self.pellet_eaten(powerPellets):
                self.change_state(EAT)
                self.timer = 7
            
            # Transition to FLEE state if ghosts are nearby
            elif self.ghost_close(ghosts): 
                self.change_state(FLEE)

        elif self.state == FLEE:
            # Transition back to NORMAL state when no ghosts are nearby
            if not self.ghost_close(ghosts):
                self.change_state(NORMAL)
            # Transition to EAT state if a pellet is eaten while fleeing
            elif self.pellet_eaten(powerPellets):
                self.change_state(EAT)
                self.timer = 7

        elif self.state == EAT:
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

    def get_next_direction(self, valid_directions, ghosts, powerPellets, pellets):
        if self.state == NORMAL:
            if self.powerP == set(powerPellets):
                print("Going after normal pellets")
                return self.get_normal_pellets(pellets, valid_directions)
            return self.get_target_direction(powerPellets, valid_directions)  # Move towards goal
        elif self.state == FLEE:
            return self.get_escape_direction(valid_directions, ghosts)  # Move away from ghosts
        elif self.state == EAT:
            return self.get_chase_direction(ghosts, valid_directions)  # Chase something
        return self.pacman.direction  # Default to current direction

    def get_normal_pellets(self, pellets, directions):
        goal = self.getNearbyPellet(pellets)
        distances = []
        for direction in directions:
            vec = (
                goal - self.pacman.position + self.pacman.directions[direction] * TILEWIDTH
            )
            distances.append(vec.magnitudeSquared())
        index = distances.index(max(distances))
        return directions[index]

    def get_target_direction(self, powerPellets, directions):
        target = self.getNearbyPowerPellet(powerPellets)
        path = astar(self.pacman.node, target)

        if not path or len(path) < 2:
            return self.pacman.goalDirection(directions)
           
        next_node = path[1]  

        goal = next_node.position - self.pacman.position
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
       
    def get_chase_direction(self, ghosts, directions):
        target = self.getNearbyGhost(ghosts)      
        path = astar(self.pacman.node, target)
        
        if not path or len(path) < 2:
            return self.pacman.goalDirection(directions)
           
        next_node = path[1]  
    
        goal = next_node.position - self.pacman.position
        
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
                distances.append((dist, p))
        
        if not distances:
            return self.pacman.target.position
        
        distances.sort(key=lambda x: x[0])

        _, target = distances[0]
        print(f"Target pellet: {target.position}")
        return target.position


    def getNearbyPowerPellet(self, powerPellets):
        distances = []
        for p in powerPellets:
            if p not in self.powerP:
                dist = (p.position - self.pacman.position).magnitudeSquared()
                distances.append((dist, p.node))  
        
        if not distances:
            return self.pacman.target

        distances.sort(key=lambda x: x[0])

        _, target = distances[0]
        print(f"Target power pellet: {target.position}")
        return target
    
    def getNearbyGhost(self, ghosts):
        distances = []
        for g in ghosts:
            if g.mode.current == FREIGHT: 
                dist = (g.position - self.pacman.position).magnitudeSquared()
                distances.append((dist, g.node))  
        if not distances:
            return self.pacman.target
        
        distances.sort(key=lambda x: x[0])

        _, target = distances[0]
        return target

    def is_in_home(self, pos):
        for home_pos in self.nodes.homenodes:
            return pos == home_pos 
        
    def pellet_eaten(self, powerPellets):
        for pellet in powerPellets[:]:
            if pellet in self.powerP:
                continue  
            if self.pacman.collideCheck(pellet):
                print("Pellet eaten")
                self.powerP.add(pellet)
                print(self.powerP)
                return True
        return False 

    def heuristic(self, node1, node2):
        return abs(node1.position.x - node2.position.x) + abs(node1.position.y - node2.position.y)
    
    def ghost_close(self, ghosts):
        for ghost in ghosts:
            if ghost.mode.current == CHASE:
                dist = self.heuristic(self.pacman, ghost)
                if dist <= 200:
                    return True
        return False
        
    def within_radius(self, vec1, vec2, radius=400):
        return (vec1 - vec2).magnitudeSquared() <= radius**2
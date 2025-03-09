from algorithms import astar
from constants import *
import random

class PacmanFSM(object):
    def __init__(self, pacman, nodes):
        self.pacman = pacman
        self.nodes = nodes
        self.state = NORMAL
        self.timer = 0 

    def update(self, dt, ghosts, pellets):
        if self.state == NORMAL:
            if self.ghost_nearby(ghosts):
                self.change_state(FLEE)

            elif self.pellet_eaten(pellets):
                self.change_state(EAT)
                self.timer = 5  

        elif self.state == FLEE:
            if not self.ghost_nearby(ghosts):
                self.change_state(NORMAL)

        elif self.state == EAT:
            self.timer -= dt
            if self.timer <= 0:
                self.change_state(NORMAL)

    def change_state(self, new_state):
        state_names = {
            NORMAL: "Normal",
            FLEE: "Flee",
            EAT: "Eat"
        }
        print(f"Pacman changing state: {state_names[self.state]} → {state_names[new_state]}")
        self.state = new_state

    def ghost_nearby(self, ghosts):
        for ghost in ghosts:
            if (self.pacman.position - ghost.position).magnitude() < 100:
                return True
        return False

    def pellet_eaten(self, pellets):
        for pellet in pellets:
            if self.pacman.collideCheck(pellet):
                print("pellet eaten")
                return True
        return False  
    
    def get_next_direction(self, valid_directions):
        if self.state == NORMAL:
            return self.get_target_direction(valid_directions)  # Move towards goal
        elif self.state == FLEE:
            return self.get_escape_direction(valid_directions)  # Move away from ghosts
        elif self.state == EAT:
            return self.get_chase_direction(valid_directions)  # Chase something
        return self.pacman.direction  # Default to current direction

    def get_target_direction(self, valid_directions):
        return random.choice(valid_directions) if valid_directions else self.pacman.direction

    def get_escape_direction(self, valid_directions):
        # For now, just pick a random escape route
        return random.choice(valid_directions) if valid_directions else self.pacman.direction

    def get_chase_direction(self, valid_directions):
        return random.choice(valid_directions) if valid_directions else self.pacman.direction
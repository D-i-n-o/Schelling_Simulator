import random
import pygame
import pygame_gui
import sys
from fractions import Fraction
from agent import JumpAgent, SwapAgent
from utilities import *
from abc import ABC, abstractmethod

from collections import namedtuple

class Game(ABC):
    def __init__(self, width, height, utility_function = SinglePeakedUtility(peak = Fraction(1,2))):
        self.NE = False
        self.w_width, self.w_height = 100,100
        self.height = height
        self.width = width
        self.agent_ratio = 1.0
        self.blue_agent_ratio = 0.5
        self.self_inclusive = True
        self.agent_count = int(self.height*self.width*self.agent_ratio/2)
        self.diagonal_neighbors = True
        self.utility_function = utility_function
        self.size = 60 # default tile size
        self.simulation_state = 0
        self.agent_mapping = {0:self.grid_cell("triangle.png"), 1:self.grid_cell("square.png")}
        self.grid = [[None for _ in range(self.height)] for _ in range(self.width)]
        self.agents = []
        
    # LS(G) = 1 / |V| * sum_{v in V}  (f_G(v) / deg(v))
    def local_segregation(self, agents):
        if len(agents) == 0: return 0
        sum_same_type = 0
        deg = 8
        for agent in agents:
            same_type_agents, other_type_agents = agent.neighborhood_types()
            sum_same_type += same_type_agents
        return sum_same_type / (deg * len(self.agents))

    def grid_cell(self, texture = None):
        square = pygame.Surface((self.size, self.size))
        square.fill((0, 0, 0))
        pygame.draw.rect(square, (20,20,20), (0, 0, self.size, self.size), 1)
        if texture:    
            tex = pygame.image.load(texture).convert_alpha()
            tex = pygame.transform.scale(tex, (self.size, self.size))
            square.blit(tex, (0,0))
        return square
    
    def adjacent(self, i,j):
        return (self.diagonal_neighbors or (i == 0 or j == 0)) and (self.self_inclusive or (i != 0 or j != 0))
    
    def wrap_position(self, pos):
        return (pos[0] % self.width, pos[1] % self.height)

    def agent_at(self, pos):
        return self.grid[pos[0]][pos[1]]
    
    def agent_type_at(self, pos):
        agent = self.agent_at(pos)
        if agent:
            return agent.type
        return None
    
    def neighbors(self, pos):
        return [self.wrap_position((pos[0]+i, pos[1]+j)) for i in range(-1,2) for j in range(-1,2) if self.adjacent(i,j)]
 
    def positions(self):
        return ((x,y) for x in range(self.width) for y in range(self.height))
    
    def adapt_to_windowsize(self, w, h):
        self.w_width = w
        self.w_height = h
        self.size = int(min(0.9*w/self.width, 0.9*h/self.height))
        if self.size < 5:
            self.size = 5
        self.agent_mapping = {None: self.grid_cell(), 0:self.grid_cell("triangle.png"), 1:self.grid_cell("square.png")}
    
    def set_grid_size(self, width, height):
        if width == self.width and height == self.height:
            return
        self.NE = False
        self.height = height
        self.width = width
        self.agent_count = int(height*width*self.agent_ratio/2)
        self.adapt_to_windowsize(self.w_width, self.w_height)
        self.generate_grid()

    def set_utility_function(self, f):
        self.NE = False
        self.utility_function = f
    
    def set_self_inclusive(self, self_inclusive):
        if self_inclusive != self.self_inclusive:
            self.NE = False
        self.self_inclusive = self_inclusive

    def set_torus_type(self, torus_type):
        if torus_type == "8-Torus":
            if self.diagonal_neighbors == False:
                self.NE = False
            self.diagonal_neighbors = True
        else:
            if self.diagonal_neighbors == True:
                self.NE = False
            self.diagonal_neighbors = False

    def set_blue_agents(self, blue_agents):
        if self.blue_agent_ratio == blue_agents:
            return
        self.NE = False
        self.blue_agent_ratio = blue_agents
        self.generate_grid()

    def set_agents(self, agents):
        if self.agent_ratio == agents:
            return
        self.NE = False
        self.agent_ratio = agents
        self.agent_count = int(self.height*self.width*self.agent_ratio)
        self.generate_grid()

    @abstractmethod
    def draw_on(self, screen, font):
        pass

    @abstractmethod
    def update_simulation(self):
        pass


    @abstractmethod
    def generate_grid(self):
        pass
    
        
class JumpGame(Game):
    def place_agents(self, r, b):
        assert r+b < self.width*self.height
        # assert r >= b
        self.NE = False
        nodes = list(self.positions())   
        random.shuffle(nodes)
        self.r = r
        self.b = b
        agent_counts = [r,b] # 0 is red, 1 is blue
        for agent_type, agent_count in enumerate(agent_counts): 
            for i in range(agent_count):
                node = nodes.pop()
                self.grid[node[0]][node[1]] = JumpAgent(self, agent_type, node)

    def generate_grid(self):
        self.NE = False
        self.grid = [[None for _ in range(self.height)] for _ in range(self.width)]
        self.place_agents(int(self.agent_count* (1-self.blue_agent_ratio)), int(self.agent_count * self.blue_agent_ratio))
        self.agents = [self.agent_at(pos) for pos in self.positions() if self.agent_at(pos) is not None]
        self.empty_nodes = set((pos for pos in self.positions() if self.agent_at(pos) is None))
        self.jump_target = None
        self.jumping_agent = None
        self.simulation_state = 0
        self.ls = self.local_segregation(self.agents)
        print("Local Segregation: ", self.ls)

    def __init__(self, width, height, utility_function = SinglePeakedUtility(peak = Fraction(1,2))):
        super().__init__(width, height, utility_function)
        self.r = 1
        self.b = 1
        self.agent_ratio = 0.8
        self.agent_count = int(self.height*self.width*self.agent_ratio/2)
        
        self.generate_grid()
        
        self.jump_target = None
        self.jumping_agent = None
        self.jump_new_utility = None
        
    
    def draw_on(self, screen, font):   
        def blit_centered(screen, surface, center):
            pos = (center[0] - surface.get_size()[0]/2, center[1] - surface.get_size()[1]/2)
            screen.blit(surface, pos)
        def grid_pos_to_coords(pos):
            return ((pos[0])*self.size, (pos[1])*self.size)
        def grid_pos_to_center(pos):
            return ((pos[0]+0.5)*self.size, (pos[1]+0.5)*self.size)
        def highlight_cell(pos, color, width):
            pos = grid_pos_to_coords(pos)
            pygame.draw.rect(screen, color, (pos[0], pos[1], self.size, self.size), width)
        screen.fill((0, 0, 0))
        for x in range(self.width):
            for y in range(self.height):
                agent_type = self.agent_type_at((x,y))
                agent_surface = self.agent_mapping[agent_type]
                screen.blit(agent_surface, grid_pos_to_coords((x,y)))
        if self.jumping_agent is not None and self.jump_target is not None:
            for pos in self.neighbors(self.jumping_agent.pos):
                highlight_cell(pos, (200, 150, 150, 75), 2)
            highlight_cell(self.jumping_agent.pos, (200, 200, 200), 4)
            for pos in self.neighbors(self.jump_target):
                highlight_cell(pos, (150, 200, 150, 75), 4)
            highlight_cell(self.jump_target, (200, 200, 200), 2)
            current_utility = self.jumping_agent.utility()
            text_current_utility = font.render(str(float(int(current_utility*100)/100)), True, (0, 0, 0))
            text_new_utility = font.render(str(float(int(self.jump_new_utility*100)/100)), True, (255, 255, 255))
            blit_centered(screen, text_current_utility, grid_pos_to_center(self.jumping_agent.pos))
            blit_centered(screen, text_new_utility, grid_pos_to_center(self.jump_target))
    
    def update_simulation(self):
        if self.simulation_state == 0:
            self.jumping_agent, self.jump_target, self.jump_new_utility = self.find_jump()
            
        if self.simulation_state == 1:
            self.execute_jump()
        self.simulation_state = (self.simulation_state + 1 ) % 2
    
    def execute_jump(self):
        if self.jumping_agent and self.jump_target:
            # updating local segregation metric
            affected_neighbors = set()
            affected_neighbors.add(self.jumping_agent)
            for pos in self.neighbors(self.jumping_agent.pos):
                if (neighbor := self.agent_at(pos)) is None: continue
                affected_neighbors.add(neighbor)
            for pos in self.neighbors(self.jump_target):
                if (neighbor := self.agent_at(pos)) is None: continue
                affected_neighbors.add(neighbor)

            ls_pre_jump = self.local_segregation(affected_neighbors)
            self.jumping_agent.jump_to(self.jump_target)
            ls_post_jump = self.local_segregation(affected_neighbors)
            self.ls += (ls_post_jump - ls_pre_jump)
    
        self.jumping_agent = None
        self.jump_target = None
            
    def find_jump(self):
        if self.NE:
            return None, None, None
        limit = int(len(self.agents)*0.1)
        empty_nodes = list(self.empty_nodes)
        random.shuffle(empty_nodes)
        for _ in range(limit):
            agent = random.choice(self.agents)
            improving_position, new_utility = agent.find_improving_jump(empty_nodes)
            if improving_position:
                return agent, improving_position, new_utility
        random.shuffle(self.agents)
        for agent in self.agents:
            improving_position, new_utility = agent.find_improving_jump(empty_nodes)
            if improving_position:
                return agent, improving_position, new_utility
        self.NE = True
        return None, None, None

class SwapGame(Game):
    
    
    def __init__(self, width, height, utility_function = SinglePeakedUtility(peak = Fraction(1,2))):
        super().__init__(width, height, utility_function)
    
        self.b = int(self.width * self.height * self.blue_agent_ratio)
        self.r = self.width * self.height - self.b # no empty cells
        self.generate_grid()
        self.swap_agent1 = None
        self.swap_agent2 = None


    def draw_on(self, screen, font):
        def blit_centered(screen, surface, center):
            pos = (center[0] - surface.get_size()[0]/2, center[1] - surface.get_size()[1]/2)
            screen.blit(surface, pos)
        def grid_pos_to_coords(pos):
            return ((pos[0])*self.size, (pos[1])*self.size)
        def grid_pos_to_center(pos):
            return ((pos[0]+0.5)*self.size, (pos[1]+0.5)*self.size)
        def highlight_cell(pos, color, width):
            pos = grid_pos_to_coords(pos)
            pygame.draw.rect(screen, color, (pos[0], pos[1], self.size, self.size), width)
        screen.fill((0, 0, 0))
        for x in range(self.width):
            for y in range(self.height):
                agent_type = self.agent_type_at((x,y))
                agent_surface = self.agent_mapping[agent_type]
                screen.blit(agent_surface, grid_pos_to_coords((x,y)))
        if self.swap_agent1 is not None and self.swap_agent2 is not None:
            for pos in self.neighbors(self.swap_agent1.pos):
                highlight_cell(pos, (200, 150, 150, 75), 2)
            highlight_cell(self.swap_agent1.pos, (200, 200, 200), 4)
            for pos in self.neighbors(self.swap_agent2.pos):
                highlight_cell(pos, (150, 200, 150, 75), 4)
            highlight_cell(self.swap_agent2.pos, (200, 200, 200), 2)
            # new_utility_a = self.jumping_agent.utility()
            # text_current_utility = font.render(str(float(int(current_utility*100)/100)), True, (0, 0, 0))
            # text_new_utility = font.render(str(float(int(self.jump_new_utility*100)/100)), True, (255, 255, 255))
            # blit_centered(screen, text_current_utility, grid_pos_to_center(self.swap_agent1.pos))
            # blit_centered(screen, text_new_utility, grid_pos_to_center(self.swap_agent2.pos))


    def place_agents(self, r, b):
        assert r+b == self.width*self.height
        nodes = list(self.positions())
        random.shuffle(nodes)
        assert len(nodes) == self.width*self.height
        self.r = r
        self.b = b
        self.NE = False
        agent_counts = [r,b] # 0 is red, 1 is blue
        for agent_type, agent_count in enumerate(agent_counts):
            for i in range(agent_count):
                node = nodes.pop()
                self.grid[node[0]][node[1]] = SwapAgent(self, agent_type, node)

    def generate_grid(self):
        self.NE = False
        self.grid = [[None for _ in range(self.height)] for _ in range(self.width)]
        num_blue = int(self.width * self.height * self.blue_agent_ratio)
        self.place_agents(self.width*self.height - num_blue, num_blue)
        self.blue_agents = [self.agent_at(pos) for pos in self.positions() if self.agent_type_at(pos) == 1]
        self.red_agents = [self.agent_at(pos) for pos in self.positions() if self.agent_type_at(pos) == 0]
        self.agents = self.red_agents + self.blue_agents
        self.simulation_state = 0
        self.ls = self.local_segregation(self.agents)
        print("Local Segregation: ", self.ls)

    def agent_count(self):
        return int(self.height*self.width)
    
    def wrap_position(self, pos):
        return (pos[0] % self.width, pos[1] % self.height)
    
    def neighbors(self, pos):
        return [self.wrap_position((pos[0]+i, pos[1]+j)) for i in range(-1,2) for j in range(-1,2) if self.adjacent(i,j)]

    def find_swap(self):
        if self.NE:
            return None, None
        # limit = int(len(self.agents)*0.1)
        # random.shuffle(self.agents)
        for agent in self.blue_agents:
            improving_swap_partner = agent.find_improving_swap(self.red_agents)
            if improving_swap_partner:
                return agent, improving_swap_partner
        self.NE = True
        return None, None

    def update_simulation(self):
        if self.simulation_state == 0:
            self.swap_agent1, self.swap_agent2 = self.find_swap()

        if self.simulation_state == 1:
            if self.swap_agent1 and self.swap_agent2:
                affected_neighbors = set()
                for pos in self.neighbors(self.swap_agent1.pos):
                    affected_neighbors.add(self.agent_at(pos))
                for pos in self.neighbors(self.swap_agent2.pos):
                    affected_neighbors.add(self.agent_at(pos))
                ls_pre_swap = self.local_segregation(affected_neighbors)
                SwapAgent.swap(self, self.swap_agent1, self.swap_agent2)
                ls_post_swap = self.local_segregation(affected_neighbors)
                self.ls += (ls_post_swap - ls_pre_swap)
        
        self.simulation_state = (self.simulation_state + 1 ) % 2
    
        
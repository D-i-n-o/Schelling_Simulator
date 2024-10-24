import random
from fractions import Fraction

def is_greater(a, b, epsilon=1e-9):
    return (a - b) > epsilon

class Agent:
    def __init__(self, game, agent_type, pos):
        self.game = game
        self.type = agent_type
        self.pos = pos
        
    def neighborhood_types(self):
        same_type_agents = 0
        other_type_agents = 0
        for neighbor_pos in self.game.neighbors(self.pos):
            other_type = self.game.agent_type_at(neighbor_pos)
            if other_type is None:
                continue
            if other_type == self.type:
                same_type_agents += 1
            else:
                other_type_agents += 1
        return same_type_agents, other_type_agents

    def utility(self):
        same_type_agents, other_type_agents = self.neighborhood_types()
        f_i = 0.0
        if same_type_agents + other_type_agents > 0:
            f_i = Fraction(same_type_agents, same_type_agents + other_type_agents)
        return self.game.utility_function(f_i)

class JumpAgent(Agent):

    def jump_to(self, new_pos, only_temporary = False):
        if new_pos == self.pos:
            return
        self.game.grid[self.pos[0]][self.pos[1]] = None
        self.game.grid[new_pos[0]][new_pos[1]] = self
        if not only_temporary:
            self.game.empty_nodes.remove(new_pos)
            self.game.empty_nodes.add(self.pos)
        self.pos = new_pos
    
    def find_improving_jump(self, empty_nodes):
        original_position = self.pos
        u = self.utility()
        new_utility = None
        improving_position = None
        for pos in empty_nodes:
            self.jump_to(pos, only_temporary=True)
            new_utility = self.utility()
            if is_greater(new_utility, u): 
                improving_position = pos
                break
        self.jump_to(original_position, only_temporary=True)
        return improving_position, new_utility

class SwapAgent(Agent):

    @staticmethod
    def swap(game, agent1, agent2):
        game.grid[agent1.pos[0]][agent1.pos[1]] = agent2
        game.grid[agent2.pos[0]][agent2.pos[1]] = agent1
        agent1.pos, agent2.pos = agent2.pos, agent1.pos
    
    def find_improving_swap(self, other_agents):
        u = self.utility()
        if u == 1.0:
            return None
        new_utility = None
        improving_agent = None
        for other_agent in other_agents:
            other_utility = other_agent.utility()
            if other_utility == 1.0:
                continue
            SwapAgent.swap(self.game, self, other_agent)
            new_utility = self.utility()
            new_other_utility = other_agent.utility()
            SwapAgent.swap(self.game, self, other_agent)
            if is_greater(new_utility, u) and is_greater(new_other_utility, other_utility):
                improving_agent = other_agent
                break
        return improving_agent

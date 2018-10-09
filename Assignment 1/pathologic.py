# -*-coding: utf-8 -*
'''NAMES OF THE AUTHOR(S): Gaël Aglin <gael.aglin@uclouvain.be>, Francois Aubry <francois.aubry@uclouvain.be>'''
from search import *
import copy


#################
# Problem class #
#################

class Pathologic(Problem):

    def successor(self, state):
        for i in range(state.nbr):
            for j in range(state.nbc):
                if state.grid[i][j] == '$':
                    current_r = i
                    current_c = j
        # action_list = ['up', 'down', 'left', 'right']
        action_list = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        iterator = [get_direction(action, state, current_r, current_c) for action in action_list]
        # print(iterator)
        generator = (item for item in iterator if item)
        # generator = iter(iterator)
        # for item in generator:
        #     print(item)
        return generator

    def goal_test(self, state):
        for i in range(state.nbr):
            if '_' in state.grid[i]:
                return False
        return True


def get_direction(action, state, row, column):
    # if action == 'up':
    #     row_op = -1
    #     column_op = 0
    # elif action == 'down':
    #     row_op = 1
    #     column_op = 0
    # elif action == 'left':
    #     row_op = 0
    #     column_op = -1
    # else:
    #     row_op = 0
    #     column_op = 1

    row_op = action[0]
    column_op = action[1]

    
    if (row + row_op < 0) or (column + column_op < 0) or \
            (row + row_op == state.nbr) or (column + column_op == state.nbc):
        return None
    elif (state.grid[row + row_op][column + column_op] == '0') or (
            state.grid[row + row_op][column + column_op] == '_'):
        grid = copy.deepcopy(state.grid)
        grid[row][column] = 'x'
        grid[row + row_op][column + column_op] = '$'
        new_state = State(grid)
        return [action, new_state]
    else:
        return None



###############
# State class #
###############

class State:
    def __init__(self, grid):
        self.nbr = len(grid)
        self.nbc = len(grid[0])
        self.grid = grid

    def __str__(self):
        s = ""
        for i in range(0, self.nbr):
            for j in range(0, self.nbc):
                s = s + str(self.grid[i][j]) + " "
            s = s.rstrip()
            if i < self.nbr - 1:
                s = s + '\n'
        return s


######################
# Auxiliary function #
######################

def readInstanceFile(filename):
    lines = [line.replace(" ", "").rstrip('\n') for line in open(filename)]
    n = len(lines)
    m = len(lines[0])
    grid_init = [[lines[i][j] for j in range(0, m)] for i in range(0, n)]
    return grid_init


#####################
# Launch the search #
#####################

# grid_init = readInstanceFile(sys.argv[1])
grid_init = readInstanceFile('instances/i04')

init_state = State(grid_init)

problem = Pathologic(init_state)

# example of bfs graph search

node = depth_first_tree_search(problem)
# node = breadth_first_tree_search(problem)
# node = depth_first_graph_search(problem)
# node = breadth_first_graph_search(problem)

# example of print
path = node.path()
path.reverse()


print('Number of moves: ' + str(node.depth))
for n in path:
    print(n.state)  # assuming that the __str__ function of state outputs the correct format
    print()

# -*-coding: utf-8 -*
'''NAMES OF THE AUTHOR(S): Gaël Aglin <gael.aglin@uclouvain.be>, Francois Aubry <francois.aubry@uclouvain.be>'''
from search import *
import copy


#################
# Problem class #
#################

class Pathologic(Problem):

    def successor(self, state):
        # state.grid[4][2] = '1'
        # state.grid[2][2] = '$'
        for i in range(state.nbr):
            for j in range(state.nbc):
                if state.grid[i][j] == '$':
                    current_r = i
                    current_c = j
        action_list = ['up', 'down', 'left', 'right']
        iterator = [get_direction(action, state, current_r, current_c) for action in action_list \
                    if get_direction(action, state, current_r, current_c)]
        generator = (item for item in iterator)
        # for item in generator:
        #     print(item)
        return generator

    def goal_test(self, state):
        count = 0
        for i in range(state.nbr):
            for j in range(state.nbc):
                if state.grid[i][j] == '_':
                    count += 1
        # print(count)
        if count == 0:
            return True
        else:
            return False

def get_direction(action, state, row, column):
    if action == 'up':
        row_op = -1
        column_op = 0
    elif action == 'down':
        row_op = 1
        column_op = 0
    elif action == 'left':
        row_op = 0
        column_op = -1
    else:
        row_op = 0
        column_op = 1
    try:
        if (state.grid[row + row_op][column + column_op] == '0') or (
                state.grid[row + row_op][column + column_op] == '_'):
            grid = copy.deepcopy(state.grid)
            grid[row][column] = 'x'
            grid[row + row_op][column + column_op] = '$'
            new_state = State(grid)
            # print(action)
            # print(new_state)
            # print('\n')
            return [action, new_state]
    except:
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
grid_init = readInstanceFile('instances/i02')
init_state = State(grid_init)
print('init_state')
print(init_state)

problem = Pathologic(init_state)

# example of bfs graph search
node = breadth_first_graph_search(problem)

# example of print
path = node.path()
path.reverse()



print('Number of moves: ' + str(node.depth))
for n in path:
    print(n.state)  # assuming that the __str__ function of state outputs the correct format
    print()

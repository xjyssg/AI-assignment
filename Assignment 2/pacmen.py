# -*-coding: utf-8 -*
'''NAMES OF THE AUTHOR(S): Gael Aglin <gael.aglin@uclouvain.be>, Francois Aubry <francois.aubry@uclouvain.be>'''
from search import *
import copy


#################
# Problem class #
#################
class Pacmen(Problem):

    def successor(self, state):
        """Returns successors according to the current state"""
        pacmen = []
        # print(state)
        for i in range(state.nbr):
            for j in range(state.nbc):

                if state.grid[i][j] == '1':
                    pacmen.append([i, j, 1])
                elif state.grid[i][j] == '2':
                    pacmen.append([i, j, 2])
                    # pacmen.append([i, j])
                elif state.grid[i][j] == '3':
                    pacmen.append([i, j, 3])
                    # pacmen.append([i, j])
                    # pacmen.append([i, j])

                # if state.grid[i][j] == '$':
                #     pacmen.append([i, j, 1])

        action_list = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        # Performs every possible actions
        possible_action = []
        state_list = [state]

        for i in range(len(pacmen)):
            new_state = []
            new_action = []
            for j in range(len(state_list)):
                for k in range(len(action_list)):
                    result = get_direction(action_list[k], state_list[j], pacmen[i])
                    if result != None:
                        new_state.append(result[1])
                        new_action.append(result)
            possible_action = new_action
            state_list = new_state


        generator = (item for item in possible_action if item)
        return generator

    def goal_test(self, state):
        """Returns the result whether the current state is the goal"""
        for i in range(state.nbr):
            if '@' in state.grid[i]:
                return False
        return True

def get_direction(action, state, position):
    """Returns a new state given the current state and the action"""
    row = position[0]
    column = position[1]
    number = position[2]

    row_op = action[0]
    column_op = action[1]

    if (row + row_op < 0) or (column + column_op < 0) or \
            (row + row_op >= state.nbr) or (column + column_op >= state.nbc):
        return None
    elif (state.grid[row + row_op][column + column_op] == '@') or \
            (state.grid[row + row_op][column + column_op] == ' ') or \
            (state.grid[row + row_op][column + column_op] == '1') or \
            (state.grid[row + row_op][column + column_op] == '2'):

        grid = copy.deepcopy(state.grid)
        
        if number == 1:
            grid[row][column] = ' '
        elif number == 2:
            grid[row][column] = '1'
        elif number == 3:
            grid[row][column] = '2'
        
        if (state.grid[row + row_op][column + column_op] == '@') or \
                (state.grid[row + row_op][column + column_op] == ' '):

            grid[row + row_op][column + column_op] = '1'

            # grid[row + row_op][column + column_op] = '$'

        elif state.grid[row + row_op][column + column_op] == '1':
            grid[row + row_op][column + column_op] = '2'
        elif state.grid[row + row_op][column + column_op] == '2':
            grid[row + row_op][column + column_op] = '3'

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
        for a in range(nsharp):
            s = s+"#"
        s = s + '\n'
        for i in range(0, self.nbr):
            s = s + "# "
            for j in range(0, self.nbc):
                s = s + str(self.grid[i][j]) + " "
            s = s + "#"
            if i < self.nbr:
                s = s + '\n'
        for a in range(nsharp):
            s = s+"#"
        return s

    def __eq__(self, other_state):
        for i in range(self.nbr):
            for j in range(self.nbc):
                if self.grid[i][j] != other_state.grid[i][j]:
                    return False
        return True

    def __hash__(self):
        cal = 0

        a_score = 1000
        b_score = 50
        c_score = 100
        for i in range(self.nbr):
            for j in range(self.nbc):
                if self.grid[i][j] == '@':
                    cal += a_score * (i + 10 * j)

                elif self.grid[i][j] == '1':

                # elif self.grid[i][j] == '$':

                    cal += b_score * (i + 10 * j)
                elif self.grid[i][j] == '2':
                    cal += c_score * (i + 10 * j)

        return cal



######################
# Auxiliary function #
######################
def readInstanceFile(filename):
    lines = [[char for char in line.rstrip('\n')[1:][:-1]] for line in open(filename)]
    nsharp = len(lines[0]) + 2
    lines = lines[1:len(lines)-1]
    n = len(lines)
    m = len(lines[0])
    grid_init = [[lines[i][j] for j in range(1, m, 2)] for i in range(0, n)]
    return grid_init,nsharp


def cal_distance(corrdinate1, corrdinate2, node):
    result = abs(corrdinate1[0] - corrdinate2[0]) + abs(corrdinate1[1] - corrdinate2[1])

    # if (corrdinate1[0] - corrdinate2[0] == 0) or \
    #         (corrdinate1[1] - corrdinate2[1] == 0):
    #     result += 2
    # x1 = min(corrdinate2[0], corrdinate1[0])
    # x2 = max(corrdinate2[0], corrdinate1[0])
    # y1 = min(corrdinate2[1], corrdinate1[1])
    # y2 = max(corrdinate2[1], corrdinate1[1])
    # if 'x' in node.state.grid[corrdinate2[0]][y1 : y2]:
    #     # result += node.state.nbr - (y2 - y1)
    #     result += 2
    # else:
    #     for index in range(x1, x2):
    #         if 'x' in node.state.grid[index + 1][corrdinate2[1]]:
    #             # result += node.state.nbc - (x2 - x1)
    #             result += 2
    #             break
    return result


######################
# Heuristic function #
######################
def heuristic(node):
    h = 0.0
    candidates = []
    foods = []
    for i in range(node.state.nbr):
        for j in range(node.state.nbc):
            if (node.state.grid[i][j] == '1'):
                candidates.append([i, j])
            elif (node.state.grid[i][j] == '2'):
                candidates.append([i, j])
                candidates.append([i, j])
            elif (node.state.grid[i][j] == '3'):
                candidates.append([i, j])
                candidates.append([i, j])
                candidates.append([i, j])
            # elif (node.state.grid[i][j] == '$'):
            #     candidates.append([i, j])
            if node.state.grid[i][j] == '@':
                foods.append([i, j])

    # print(candidates)
    # print(foods)
    while foods != []:
        min_dis = 100
        min_f = 0
        min_c = 0
        for f_index in range(len(foods)):
            for c_index in range(len(candidates)):
                possible = cal_distance(foods[f_index], candidates[c_index], node)
                if min_dis >= possible:
                    min_dis = possible
                    min_f = f_index
                    min_c = c_index
        h += min_dis
        candidates.remove(candidates[min_c])
        candidates.append(foods[min_f])
        foods.remove(foods[min_f])
        # print(candidates)
        # print(foods)
        # print()
        
    return h



#####################
# Launch the search #
#####################
grid_init,nsharp = readInstanceFile(sys.argv[1])
# grid_init,nsharp = readInstanceFile('instances/i10')

init_state = State(grid_init)
# print(init_state)
# print(init_state.nbr)
# print(init_state.nbc)

for i in range(init_state.nbr):
    for j in range(init_state.nbc):
        if (init_state.grid[i][j] == '$'):
            init_state.grid[i][j] = '1'

# print(init_state)
problem = Pacmen(init_state)

node = astar_graph_search(problem, heuristic)

# example of print
path = node.path()
path.reverse()

print('Number of moves: ' + str(node.depth))


# for n in path:
#     for i in range(n.state.nbr):
#         for j in range(n.state.nbc):
#             if (n.state.grid[i][j] == '1') or \
#                     (n.state.grid[i][j] == '2') or \
#                     (n.state.grid[i][j] == '3'):
#                 n.state.grid[i][j] = '$'
for n in path:
    for i in range(n.state.nbr):
        for j in range(n.state.nbc):
            if (n.state.grid[i][j] == '1') or \
                    (n.state.grid[i][j] == '2') or \
                    (n.state.grid[i][j] == '3'):
                n.state.grid[i][j] = '$'
    print(n.state)  # assuming that the __str__ function of state outputs the correct format
    print()
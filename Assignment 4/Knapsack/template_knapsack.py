#! /usr/bin/env python3
'''NAMES OF THE AUTHOR(S): Gaël Aglin <gael.aglin@uclouvain.be>, Francois Aubry <francois.aubry@uclouvain.be>'''
from search import *
import re
import sys
import os
import copy
import heapq

class Knapsack(Problem):

    def __init__(self,initFile):
        try:
            file=open(initFile,'r')
            self.nItems = int(file.readline().strip().rstrip('\n'))
            self.itemWeight = []
            self.itemUtil = []
            self.conflicts = []

            for i in range(self.nItems):
                data = file.readline().strip().rstrip('\n')
                data = re.sub(' +',' ',data).split(' ')
                self.itemWeight.append(int(data[1]))
                self.itemUtil.append(int(data[2]))
                if len(data) > 3:
                    self.conflicts.append([int(w)-1 for w in data[3:]])
                else:
                    self.conflicts.append([])

            self.capacity = int(file.readline().strip().rstrip('\n'))
            file.close()

            self.initial = self.initial_state()

        except IOError as error:
            print('Error opening the instance file: '+str(error))
            exit(-1)

    def initial_state(self):
        state = {}
        state['items'] = []
        state['weight'] = 0
        state['utility'] = 0
        return state

    def successor(self,state):
        successor_list = []
        value_list = []
        # add item
        if (state['items'] == []):
            # no items in the bag
            for index in range(self.nItems):
                if (state['weight'] + self.itemWeight[index]) <= self.capacity:
                    new_state = copy.deepcopy(state)
                    new_state['items'].append(index)
                    new_state['weight'] += self.itemWeight[index]
                    new_state['utility'] += self.itemUtil[index]

                    # value_list.append(self.itemUtil[index] / self.capacity)
                    # value_list.append(new_state['utility'] / new_state['weight'])
                    value_list.append(self.itemUtil[index] / self.itemWeight[index])

                    successor_list.append((0, new_state))
        else:
            # some items in the bag
            conflict_list = []
            for item_index in range(len(state['items'])):
                item = state['items'][item_index]
                # print('current item', item)
                for j in range(len(self.conflicts[item])):
                    conflict_list.append(self.conflicts[item][j])
            # print('conflicts', conflict_list)
            # print('items', state['items'])
            for index in range(self.nItems):
                if (index not in state['items']) and \
                (index not in conflict_list) and \
                ((state['weight'] + self.itemWeight[index]) <= self.capacity):
                    new_state = copy.deepcopy(state)
                    new_state['items'].append(index)
                    new_state['weight'] += self.itemWeight[index]
                    new_state['utility'] += self.itemUtil[index]

                    # value_list.append(self.itemUtil[index] / self.capacity)
                    # value_list.append(new_state['utility'] / new_state['weight'])
                    value_list.append(self.itemUtil[index] / self.itemWeight[index])

                    successor_list.append((0, new_state))

        # remove item
        # if (len(state['items']) > 1) and (state['weight'] >=  0.9 * self.capacity):
        if len(successor_list) == 0:
            for item_index in range(len(state['items'])):
                item = state['items'][item_index]
                new_state = copy.deepcopy(state)
                new_state['items'].remove(item)
                new_state['weight'] -= self.itemWeight[item]
                new_state['utility'] -= self.itemUtil[item]
                # if (new_state['utility'] / new_state['weight']) >= ((state['utility'] / state['weight'])):

                # value_list.append(((self.itemUtil[item]) / 2) / self.capacity)
                value_list.append(1 / (new_state['utility'] / new_state['weight']))
                # value_list.append(1 / self.itemUtil[item] / self.itemWeight[item])

                successor_list.append((0, new_state))
        
        self.value_list = value_list
        if (successor_list == []):# or (length1 == length2):
            successor_list.append((0, state))
            self.value_list = [0]
        generator = (item for item in successor_list if item)
        return generator


    def value(self, state):
        return state['utility'] # / state['weight'] # + 0.2 * (self.capacity - state['weight']) / state['weight']

    def getUtility(self,state):
        """
        :param state:
        :return: utility of the state in parameter
        """
        return state['utility']

    def __str__(self):
        s=str(self.nItems)+'\n'
        for i in range(self.nItems):
            s+= '\t'+str(i)+' '+str(self.itemWeight[i])+' '+str(self.itemUtil[i])+'\n'
        s+= str(self.capacity)
        return s


#################
# Local Search #
#################

def maxvalue(problem, limit=100, callback=None):
    current = LSNode(problem, problem.initial, 0)
    best = current
    for step in range(limit):
        if callback is not None:
            callback(current)
        successor_list = list(current.expand())
        # value_list = [successor.value() for successor in successor_list]
        value_list = problem.value_list
        max_value = max(value_list)
        node_list = []
        for index in range(len(value_list)):
            if value_list[index] == max_value:
                node_list.append(successor_list[index])
        current = random.choice(node_list)
        if current.value() > best.value():
            best = current
    return best


def randomized_maxvalue(problem, limit=100, callback=None):
    current = LSNode(problem, problem.initial, 0)
    best = current
    for step in range(limit):
        if callback is not None:
            callback(current)
        successor_list = list(current.expand())
        # value_list = [successor.value() for successor in successor_list]
        value_list = problem.value_list
        # print(value_list)
        if len(value_list) < 5:
            parameter = len(value_list)
        else:
            parameter = 5
        max_list = heapq.nlargest(parameter, value_list)
        # print(max_list)
        node_list = []
        for j in range(parameter):
            value = max_list[j]
            node_index = value_list.index(value)
            node_list.append(successor_list[node_index])
        current = random.choice(node_list)
        best = current
    return best




#####################
#       Launch      #
#####################

a = 12

if a == 1:
    if(len(sys.argv) <=2 ):
        print("Usage: "+sys.argv[0]+" instance_file technique_value (0: randomWalk,1: maxValue,2: randomizedMaxvalue)")
        exit(-1)
    knap = Knapsack(sys.argv[1])
    tech = int(sys.argv[2])
else:
    folder = 'knapsack_instances'
    file = 'knapsack9.txt'
    path = os.path.join(folder, file)
    knap = Knapsack(path)
    tech = 1


# setting parameter
stepLimit = 100
if(tech == 0):
    node = random_walk(knap,stepLimit)
elif(tech == 1):
    node = maxvalue(knap,stepLimit)
elif(tech == 2):
    node = randomized_maxvalue(knap,stepLimit)


state = node.state
print("weight: " + str(state['weight']) + " utility: " + str(state['utility']))
print("Items: " + str([x + 1 for x in state['items']]))
print("Capacity: " + str(knap.capacity))
print("STEP: "+str(node.step))

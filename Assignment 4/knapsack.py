#! /usr/bin/env python3
'''NAMES OF THE AUTHOR(S): Gaël Aglin <gael.aglin@uclouvain.be>, Francois Aubry <francois.aubry@uclouvain.be>'''
from search import *
import re
import sys
import random


class Knapsack(Problem):
	def __init__(self, initFile):
		try:
			file = open(initFile, 'r')
			self.nItems = int(file.readline().strip().rstrip('\n'))
			self.itemWeight = []
			self.itemUtil = []
			self.conflicts = []

			for i in range(self.nItems):
				data = file.readline().strip().rstrip('\n')
				data = re.sub(' +', ' ', data).split(' ')
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
		self.state[0] = []
		self.state[2] = 0
		self.state[3] = 0
		return self.state[2], self.state[3], [x for x in self.state[0]]
	#pass

	def successor(self, state):
		following_states = []
		next_state = []
		if state.state[0] == []:
			liste = state.state[0].copy()
			for i in range(self.nItems):
				liste.append(i)
				next_state = self.itemWeight[i], self.itemUtil[i], liste
				following_states.append(next_state)
		else:
			for i in range(self.nItems):
				liste = state.state[0].copy()
				if i not in liste:
					if next_state not in self.conflicts[i] and (state.state[2]+self.itemWeight)<=self.capacity:
						liste.append(i)
						next_state = state.state[2] + self.itemWeight[i], state.state[3] + self.itemUtil[i], liste
						following_states.append(next_state)
		for i in range(len(following_states)):
			return following_states[i]
		#pass

	def getUtility(self, state):
		"""
		:param state:
		:return: utility of the state in parameter
		"""
		if state.state[3] == 0:
			return 0
		else:
			return state.state[3]

	def __str__(self):
		s=str(self.nItems)+'\n'
		for i in range(self.nItems):
			s+= '\t'+str(i)+' '+str(self.itemWeight[i])+' '+str(self.itemUtil[i])+'\n'
		s+= str(self.capacity)
		return s000

#################
# Local Search #
#################


def maxvalue(problem, limit=100, callback=None):

	current = LSNode(problem, problem.initial, 0)
	best = current
	# Put your code here!
	for step in range(limit):
		if callback is not None:
			callback(current)
		minValue = current.value()
		bestNode = current
		for elem in list(current.expand()):
			if elem.value() < minValue:
				minValue=elem.value()
				bestNode=elem
			current = bestNode
			if current.value() < best.value():
				best = current
	return best


def randomized_maxvalue(problem, limit=100, callback=None):
	current = LSNode(problem, problem.initial, 0)
	best = current
	l = [] #list that contains all the neighbors
	k = [] #list that contains all the neighbors sorted accordingly to their value increasingly
	h = [] #list that contains the five best neighbors
	for step in range(limit):
		if callback is not None:
			callback(current)
		#minValue = current.value()
		#nextBestNode = current
		for elem in list(current.expand()):
			l.append(elem)
		k = sorted(l, l)
		h = [k[0], k[1], k[2], k[3], k[4]]
		nextBestNode = random.choice(h)
		if nextBestNode.value() < best.value():
			best = nextBestNode
	return best





#####################
#       Launch      #
#####################

if(len(sys.argv) <=2 ):
	print("Usage: "+sys.argv[0]+" instance_file technique_value (0: randomWalk,1: maxValue,2: randomizedMaxvalue)")
	exit(-1)

knap = Knapsack(sys.argv[1])

stepLimit = 100

tech = int(sys.argv[2])

if(tech == 0):
	node = random_walk(knap,stepLimit)
elif(tech == 1):
	node = maxvalue(knap,stepLimit)
elif(tech == 2):
	node = randomized_maxvalue(knap,stepLimit)


state = node.state
print("weight: " + str(state[2]) + " utility: " + str(state[3]))
print("Items: " + str([x for x in state[0]]))
print("Capacity: " + str(knap.capacity))
print("STEP: "+str(node.step))




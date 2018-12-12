import sys
import graph
from clause import *

"""
For the graph coloring problem, the only code you have to do is in this file.

You should replace

# your code here

by a code generating a list of clauses modeling the graph coloring problem
for the input graph and give number of colors.

You should build clauses using the Clause class defined in clause.py

Read the comment on top of clause.py to see how this works.
"""
def get_clauses(G, nb_colors):
  clauses = []
  # create clause for each edge
  for index in range(G.nb_edges):
    node_1 = G.edges[index][0]
    node_2 = G.edges[index][1]
    for j in range(nb_colors):
      clause = Clause(nb_colors)
      clause.add_negative(node_1, j + 1)
      clause.add_negative(node_2, j + 1)
      clauses.append(clause)
  # create clause for each node
  for index in range(G.nb_nodes):
    # at least one color
    clause = Clause(nb_colors)
    for j in range(nb_colors):
      clause.add_positive(index + 1, j + 1)
    clauses.append(clause)
    # at most one color
    for i_color in range(nb_colors):
      for j_color in range(nb_colors):
        if i_color < j_color:
          clause = Clause(nb_colors)
          clause.add_negative(index + 1, i_color + 1)
          clause.add_negative(index + 1, j_color + 1)
          clauses.append(clause)
  return clauses

if __name__ == '__main__':
  # G = graph.Graph('cycle5.col')
  # nb_colors = 3
  # print(G.nb_nodes, G.nb_edges)
  # print(G.adjacent)
  # print(G.edges)
  # print(G.nb_edges - len(G.edges))

  G = graph.Graph(sys.argv[1])
  nb_colors = int(sys.argv[2])
  clauses = get_clauses(G, nb_colors)
  for clause in clauses:
    print(clause)

  # nb_colors = 7
  # summ = 0
  # for i_color in range(0, nb_colors):
  #     for j_color in range(0, nb_colors):
  #       if i_color < j_color:
  #         summ += 1
  #         print([i_color, j_color])
  # print(summ)

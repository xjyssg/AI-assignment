"""
Class used to represent a clause in CNF for the graph coloring problem.
Variable X_v_c is true iff node v has color c.

For example, to create a clause:

X_1_1 or ~X_1_2 or X_3_4

you can do:

clause = Clause(3)
clause.add_positive(1, 1)
clause.add_negative(1, 2)
clause.add_positive(3, 3)

"""
class Clause:

  def __init__(self, nb_colors, varname = 'X'):
    self.nb_colors = nb_colors
    self.varname = varname
    self.clause = [ ]

  def index(self, v, c):
    return (v - 1) * self.nb_colors + c

  def str_from_index(self, idx):
    tmp = abs(idx) - 1
    v = tmp // self.nb_colors + 1
    c = tmp % self.nb_colors + 1
    if idx < 0:
      return '~{0}_{1}_{2}'.format(self.varname, v, c)
    return '{0}_{1}_{2}'.format(self.varname, v, c)
    
  def add_positive(self, v, c):
    self.clause.append( self.index(v, c) )

  def add_negative(self, v, c):
    self.clause.append( -self.index(v, c) )

  def minisat_str(self):
    return ' '.join( [str(x) for x in self.clause] )

  def __str__(self):
    return ' or '.join( [self.str_from_index(x) for x in self.clause] )

if __name__ == '__main__':
  clause = Clause(3)
  clause.add_positive(1, 1)
  clause.add_negative(1, 2)
  clause.add_positive(3, 3)
  print(clause)
  print(clause.minisat_str())

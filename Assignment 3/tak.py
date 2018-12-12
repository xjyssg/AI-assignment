from state import State
from mystack import Stack
from myqueue import Queue

"""
Define the number of stones can capstones for each board size.
"""
STONES = { 
  3: (10,0),
  4: (15,0),
  5: (21,1),
  6: (30,1),
  8: (50,2)
}

"""
Define constants representing flat stones, standing stones and cap stones.
"""
FLAT_STONE = 0
STANDING_STONE = 1
CAP_STONE = 2

TYPES = ['-', '|', '*']

"""
Define the four directions.
"""
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)
DIR = [ UP, DOWN, LEFT, RIGHT ]

"""
Class representing the Tak state
"""
class TakState(State):

  def __init__(self, size, max_height):
    State.__init__(self)
    self.size = size
    self.max_height = max_height
    self.stones = [ STONES[size][0] for _ in range(2) ]
    self.capstones = [ STONES[size][1] for _ in range(2) ]
    self.board = [ [ Stack() for _ in range(size) ] for _ in range(size) ]
    self.history = set()
    self.turn = 1

  def get_data_tuple(self):
    data = [ x for x in self.stones ]
    data += [ x for x in self.capstones ]
    for r in range(self.size):
      for c in range(self.size):
        data += [ r, c ]
        for x in self.board[r][c]:
          data += [ x[0], x[1] ]
    return tuple(data)

  def __eq__(self, other):
    return self.get_data_tuple() == other.get_data_tuple()
      
  
  def __hash__(self):
    return hash(self.get_data_tuple())
    
  """
  Return a deep copy of this state.
  """
  def copy(self):
    cp = TakState(self.size, self.max_height)
    for i in range(2):
        cp.stones[i] = self.stones[i]
        cp.capstones[i] = self.capstones[i]
    for r in range(self.size):
        for c in range(self.size):
            for x in self.board[r][c]:
                cp.board[r][c].add(x)
    cp.cur_player = self.get_cur_player()
    cp.winner = self.winner
    cp.invalid_player = self.invalid_player
    cp.timeout_player = self.timeout_player
    cp.history = set()
    for x in self.history:
      cp.history.add(x)
    cp.turn = self.turn
    return cp

  """
  Return the size of the board.
  """
  def get_size(self):
    return self.size

  """
  Return true if and only if the game is over.
  """
  def game_over_check(self):
    over, winner = self.is_over()
    return over
  
  """
  Returns a pair (over, winner) where over is true iff the game is over and winner is equal to the winner 
  (0, 1 or -1 is the game is not over)
  """
  def is_over(self):
    # check whether someone ran out of stones
    for i in range(2):
      if self.stones[i] + self.capstones[i] == 0:
        r, b = self.control_count()
        if r > b: return True, 0
        elif r < b: return True, 1
        return True, self.cur_player
    # check whether the board is full
    full = True
    for r in range(self.size):
      for c in range(self.size):
        if len(self.board[r][c]) == 0:
          full = False
    if full:
      r, b = self.control_count()
      if r > b: return True, 0
      elif r < b: return True, 1
      return True, self.cur_player
    # check whether there is a path
    for i in range(2):
      if self.check_horizontal_path(i) != None:
        return True, i
      if self.check_vertical_path(i) != None:
        return True, i
    return False, -1
  
  """
  Return the number of board position contolled by each player.
  """
  def control_count(self):
    count = [ 0, 0 ]
    for r in range(self.size):
      for c in range(self.size):
        for i in range(2):
          if self.is_controlled_by(r, c, i):
            count[i] += 1
    return tuple(count)

  """
  Get the winning path if it exists. It retuns an empty path otherwise.
  """
  def get_winning_path(self):
    path = self.check_horizontal_path(self.winner)
    if path != None: return path
    path = self.check_vertical_path(self.winner)
    if path != None: return path
    return []

  """
  Check whether there is a horizontal winnning path for a given player.
  """
  def check_horizontal_path(self, player):
    # initialize left positions that belong to player
    L = [ ]
    R = [ ]
    for r in range(self.size):
      if self.is_controlled_by(r, 0, player):
        L.append( (r, 0) )
      if self.is_controlled_by(r, self.size - 1, player):
        R.append( (r, self.size - 1) )
    # perform a BFS from the left to see if we can reach the right
    return self.bfs(L, R, player)
  
  """
  Check whether there is a vertical winning path for a given player.
  """
  def check_vertical_path(self, player):
    # initialize the top positions that belong to player
    U = [ ]
    D = [ ]
    for c in range(self.size):
      if self.is_controlled_by(0, c, player):
        U.append( (0, c) )
      if self.is_controlled_by(self.size - 1, c, player):
        D.append( (self.size - 1, c) )
    # perform a BFS from the top to see if we can reach the bottom
    return self.bfs(U, D, player)
  
  """
  Check whether there is a path controlled by the given player connecting the
  cells in S to the cells in T. Used to check winning paths.
  """
  def bfs(self, S, T, player):
    # initialize BFS
    parent = [ [ None for _ in range(self.size) ] for _ in range(self.size) ]
    Q = Queue()
    for s in S:
      Q.add(s)
      parent[s[0]][s[1]] = -1
    # BFS loop
    cnt = 0
    while len(Q) > 0:
      cnt += 1
      r, c = Q.remove()
      for d in DIR:
        rr = r + d[0]
        cc = c + d[1]
        if 0 <= rr and rr < self.size and 0 <= cc and cc < self.size and parent[rr][cc] == None and self.is_controlled_by(rr, cc, player):
          Q.add( (rr, cc) )
          parent[rr][cc] = (r, c)
    # check whether the other side was reached
    for r, c in T:
      if parent[r][c] != None:
        # build the path
        path = [ ]
        cur = (r, c)
        while cur != -1:
          path.append(cur)
          cur = parent[cur[0]][cur[1]]
        return path
    return None
  
  """
  Check whether cell (r, c) is controlled by the given player.
  """
  def is_controlled_by(self, r, c, player):
    if len(self.board[r][c]) == 0:
      # no piece
      return False
    piece_type, owner = self.board[r][c].top()
    if owner != player:
      # piece not owned by player
      return False
    if piece_type == STANDING_STONE:
      # piece is standing stone
      return False
    return True

  """
  Return the index of the current player.
  """
  def get_cur_player(self):
    return self.cur_player

  """
  Get all the actions that the current player can perform.
  """
  def get_current_player_actions(self):
    actions = [ ]
    # gather all place actions
    for place_action in self.get_place_actions():
      tmp = self.copy()
      tmp.apply_action(place_action)
      if not tmp.get_data_tuple() in self.history:
        actions.append(place_action)
    # gather all move actions
    if self.turn >= 3:
      for move_action in self.get_move_actions():
        tmp = self.copy()
        tmp.apply_action(move_action)
        if not tmp.get_data_tuple() in self.history:
          actions.append(move_action)
    return actions
  
  """
  Get all possible move actions from the current player.
  """
  def get_move_actions(self):
    move_actions = [ ]
    for row in range(self.size):
      for col in range(self.size):
        if len(self.board[row][col]) > 0 and self.get_top_piece(row, col)[1] == self.cur_player:
          # can only move if the stack belongs to the player
          for d in DIR:
            r = row + d[0]
            c = col + d[1]
            # check if position is in range
            if 0 <= r and r < self.size and 0 <= c and c < self.size:
              max_pieces = min(self.size, len(self.board[row][col]))
              for k in range(1, max_pieces + 1):
                if self.can_move_top_k(row, col, r, c, k):
                  delta = (r - row, c - col)
                  move = ('move', row, col, delta, [k])
                  move_actions.append(move)
                  state_tmp = self.copy()
                  state_tmp.apply_action(move)
                  self.gen_move_actions(r, c, delta, move, move_actions, state_tmp, 0)
    return move_actions

  """
  Auxiliary function to generate move actions.
  """
  def gen_move_actions(self, row, col, delta, move, move_actions, state_tmp, depth):
    r = row + delta[0]
    c = col + delta[1]
    if 0 <= r and r < self.size and 0 <= c and c < self.size:
      max_pieces = move[4][-1]
      for k in range(1, max_pieces):
        if state_tmp.can_move_top_k(row, col, r, c, k):
          nb_pieces = [x for x in move[4]]
          nb_pieces.append(k)
          new_move = (move[0], move[1], move[2], move[3], nb_pieces)
          move_actions.append(new_move)
          state_tmp = self.copy()
          state_tmp.apply_action(new_move)
          self.gen_move_actions(r, c, delta, new_move, move_actions, state_tmp, depth + 1)
  
  """
  Get all place actions for the current player.
  """
  def get_place_actions(self):
    place_actions = [ ]
    for row in range(self.size):
      for col in range(self.size):
        if len(self.board[row][col]) == 0:
          # can only place something if the board is empty
          if self.stones[self.cur_player] > 0:
            place_actions.append( ('place', FLAT_STONE, row, col) )
            if self.turn >= 3:
              place_actions.append( ('place', STANDING_STONE, row, col) )
          if self.capstones[self.cur_player] > 0:
            if self.turn >= 3:
              place_actions.append( ('place', CAP_STONE, row, col) )
    return place_actions  
            
  """
  Applies a given action to this state. It assume that the actions is
  valid. This must be checked with is_action_valid.
  """
  def apply_action(self, action):
    self.history.add(self.get_data_tuple())
    action_id = action[0]
    if action_id == 'place':
      piece_type = action[1]
      row = action[2]
      col = action[3]
      player = self.cur_player
      if self.turn <= 2:
        player = 1 - player
      self.add_piece(row, col, piece_type, player)
      if piece_type == CAP_STONE:
        self.capstones[player] -= 1
      else:
        self.stones[player] -= 1
    elif action_id == 'move':
      row = action[1]
      col = action[2]
      delta = action[3]
      assert abs(delta[0]) + abs(delta[1]) == 1, delta
      nb_pieces = action[4]
      for i in range(len(nb_pieces)):
        r_dest = row + delta[0]
        c_dest = col + delta[1]
        self.move_top_k(row, col, r_dest, c_dest, nb_pieces[i])
        row = r_dest
        col = c_dest
    # check whehter the game is over and set the winner if so
    over, winner = self.is_over()
    if over:
      self.winner = winner
    else:
      self.cur_player = 1 - self.cur_player
      self.turn += 1

  """
  Return the scores of each players.
  """
  def get_scores(self):
    if self.winner == None:
      return (0, 0)
    elif self.winner == 0:
      return (1, 0)
    return (0, 1)
  
  """
  Get the winner of the game. Call only if the game is over.
  """
  def get_winner(self):
    return self.winner

  """
  Check whether postition (r, c) is empty.
  """
  def is_empty(self, r, c):
    return len(self.board[r][c]) == 0

  """
  Check whether the current player still has pieces (stones or capstones).
  """
  def cur_player_has_pieces(self):
    return self.stones[self.cur_player] + self.capstones[self.cur_player] > 0


  """
  Get the top piece at position (r, c). Returns None if the stack is empty.
  """
  def get_top_piece(self, r, c):
    if len(self.board[r][c]) == 0: return None
    return self.board[r][c].top()

  """
  Checks whether it is possible to move k the pieces on top of the stack at (r_orig, c_orig)
  to (r_dest, c_dest). Also checks whether the positions are adjacent.
  """
  def can_move_top_k(self, r_orig, c_orig, r_dest, c_dest, k):
    if not (0 <= r_dest and r_dest < self.size and 0 <= c_dest and c_dest < self.size): return False
    if len(self.board[r_dest][c_dest]) + k > self.max_height: return False
    if len(self.board[r_dest][c_dest]) == 0: return True
    delta_r = abs(r_orig - r_dest)
    delta_c = abs(c_orig - c_dest)
    if delta_r + delta_c != 1: return False
    piece_type, _ = self.board[r_dest][c_dest].top()
    if piece_type == CAP_STONE: return False
    if piece_type != STANDING_STONE: return True
    piece_type, _ = self.board[r_orig][c_orig].top()
    return k == 1 and piece_type == CAP_STONE

  """
  Move the top k pieces of stack (r_orig, c_orig) to (r_dest, c_dest).
  It assumes that there are enough pieces at origin and enough space at destination.
  """
  def move_top_k(self, r_orig, c_orig, r_dest, c_dest, k):
    assert 0 <= r_orig and r_orig < self.size and 0 <= c_orig and c_orig < self.size, 'move_top_k orig out of bounds r={0}, c={1}'.format(r_orig, c_orig)
    assert 0 <= r_dest and r_dest < self.size and 0 <= c_dest and c_dest < self.size, 'move_top_k dest out of bounds r={0}, c={1}'.format(r_dest, c_dest)
    assert 0 < k and k <= len(self.board[r_orig][c_orig]), 'move_top_k number of pieces out of bounds k={0} and board has {1} pieces'.format(k, len(self.board[r_orig][r_dest]))
    tmp = Stack()
    for i in range(k):
      tmp.add(self.board[r_orig][c_orig].remove())
    if len(self.board[r_dest][c_dest]) > 0:
      piece_type, owner = self.board[r_dest][c_dest].top()
      if piece_type == STANDING_STONE:
        self.set_top_piece(r_dest, c_dest, FLAT_STONE, owner)
    for i in range(k):
      self.board[r_dest][c_dest].add(tmp.remove())
  
  """
  Return a string representation of the board.
  """
  def __str__(self):
    # create the matrix representation
    R = self.max_height * self.size + self.size + 1
    C = 2 * self.size + self.size + 1
    print(R, C)
    M = [ [ ' ' for c in range(C) ] for r in range(R) ]
    for r in range(R):
      for c in range(C):
        if r % (self.max_height + 1) == 0 or c % 3 == 0:
          M[r][c] = '.'
    r0 = self.max_height
    c0 = 1
    for r in range(self.size):
      for c in range(self.size):
        rm = r0 + r * (self.max_height + 1)
        cm = c0 + c * 3
        tmp = [ x for x in self.board[r][c] ]
        for t, o in tmp:
          M[rm][cm] = TYPES[t]
          M[rm][cm + 1] = str(o)
          rm -= 1
    # convert matrix to string
    s = ''
    for r in range(R):
      for c in range(C):
         s += M[r][c]
      s += '\n'
    # add other info
    s += '{0} flat stone\n{1} standing stone\n{2} cap stone\n'.format(TYPES[0], TYPES[1], TYPES[2])
    s += 'player0 has {0} stones and {1} capstones\n'.format(self.stones[0], self.capstones[0])
    s += 'player1 has {0} stones and {1} capstones\n'.format(self.stones[1], self.capstones[1])
    s += 'current palyer: {0}\n'.format(self.cur_player)
    return s

  """
  Get a representation of this state that can be loaded in the GUI.
  """
  def get_data_str(self):
    s = ''
    s += str(self.cur_player) + '\n'
    s += '{0}\n{1}\n'.format(self.size, self.max_height)
    s += '{0}\n{1}\n'.format(self.stones[0], self.stones[1])
    s += '{0}\n{1}\n'.format(self.capstones[0], self.capstones[1])
    types = ['-', '|', '*']
    for r in range(self.size):
      for c in range(self.size):
        l = len(self.board[r][c])
        if l != 0:
          s += '{0} {1} {2}\n'.format(r, c, l)
          data = [ ]
          for x in self.board[r][c]:
            data.append(x)
          data.reverse()
          for t, o in data:
            s += '{0} {1}\n'.format(o, types[t])
    return s

  ##########################################################################
  # YOU SHOULD NOT USE THESE FUNCTION, THEY ARE ONLY USED IN THE INTERFACE #
  ##########################################################################

  """
  Add a piece of type piece_type for the given player at position (r, c).
  This should not be used by your code, it is just a function used in the interface.
  It does not change the current player nor checks whether the game is over.
  """
  def add_piece(self, r, c, piece_type, player):
    if len(self.board[r][c]) > 0:
      pt, owner = self.board[r][c].remove()
      if pt == STANDING_STONE:
        self.board[r][c].add( (FLAT_STONE, owner) )
      else:
        self.board[r][c].add( (pt, owner) )
    self.board[r][c].add( (piece_type, player) )
  
  """
  Add a piece of type piece_type for the current player at position (r, c).
  This should not be used by your code, it is just a function used in the interface.
  It does not change the current player nor checks whether the game is over.
  """
  def add_piece_cur_player(self, r, c, piece_type):
    self.add_piece(r, c, piece_type, self.cur_player)

  """
  Replace the top of the stack at position (r, c) by a piece of type piece_type for the given player.
  This should not be used by your code, it is just a function used in the interface.
  It does not change the current player nor checks whether the game is over.
  """
  def set_top_piece(self, r, c, piece_type, player):
    if len(self.board[r][c]) > 0:
      self.board[r][c].remove()
    self.board[r][c].add( (piece_type, player) )

  """
  Replace the top of the stack at position (r, c) by a piece of type piece_type for the current player.
  This should not be used by your code, it is just a function used in the interface.
  It does not change the current player nor checks whether the game is over.
  """
  def set_top_piece_cur_player(self, r, c, piece_type):
    self.set_top_piece(r, c, piece_type, self.cur_player)

  """
  Get a representation of this state that can be loaded in the GUI.
  """
  def get_inginious_str(self):
    return '\n' + str(self) + '\n'

def read_state_from_file(fn):
  f = open(fn, 'r')
  lines = [ line.strip() for line in f.readlines() ]
  tmp = [ ]
  for line in lines:
    if len(line) > 0:
      tmp.append(line)
  lines = tmp
  size = int(lines[0])
  max_height = int(lines[1])
  state = TakState(size, max_height)
  state.cur_player = int(lines[2])
  state.stones[0] = int(lines[3])
  state.stones[1] = int(lines[4])
  state.capstones[0] = int(lines[5])
  state.capstones[1] = int(lines[6])
  i = 7
  while i < len(lines):
    data = lines[i].split(' ')
    r = int(data[0])
    c = int(data[1])
    k = int(data[2])
    i += 1
    for j in range(k):
      data = lines[i].split(' ')
      owner = int(data[0])
      tp = data[1]
      if tp == '-':
        tp = FLAT_STONE
      elif tp == '|':
        tp = STANDING_STONE
      else:
        tp = CAP_STONE
      state.add_piece(r, c, tp, owner)
      i += 1
  return state

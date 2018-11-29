from agent import AlphaBetaAgent
import minimax
import time

STANDING_STONE = 1

"""
Agent skeleton. Fill in the gaps.
"""
class MyAgent(AlphaBetaAgent):

  """
  This is the skeleton of an agent to play the Tak game.
  """
  def get_action(self, state, last_action, time_left):
    self.last_action = last_action
    self.time_left = time_left
    print('good', time_left)
    if time_left > 200:
      self.depth = 3
    elif time_left > 20:
      self.depth = 2
    else:
      self.depth = 1
    return minimax.search(state, self)


  """
  The successors function must return (or yield) a list of
  pairs (a, s) in which a is the action played to reach the
  state s.
  """
  def successors(self, state):
    # action_list = state.get_current_player_actions()
    # candidates = {}
    # for action in action_list:
    #   current_state = state.copy()
    #   current_state.apply_action(action)
    #   if current_state:
    #     score = self.evaluate(current_state)
    #     try:
    #         candidates[score].append((action, current_state))
    #     except:
    #         candidates[score] = [(action, current_state)]
    # keys = candidates.keys()
    # keys = list(keys)
    # keys.sort()
    # threshold = int(0.8 * len(candidates))
    # if threshold < 1:
    #   threshold = 1
    # result = []
    # for index in range(threshold):
    #   result = result + candidates[keys[- index - 1]]
    # # print(len(result))
    # generator = (candidate for candidate in result)
    # return generator

    action_list = state.get_current_player_actions()
    candidates = []
    for action in action_list:
      current_state = state.copy()
      current_state.apply_action(action)
      if current_state:
        candidates.append((action, current_state))
    # print(len(candidates))
    generator = (candidate for candidate in candidates)
    return generator
    


  """
  The cutoff function returns true if the alpha-beta/minimax
  search has to stop and false otherwise.
  """
  def cutoff(self, state, depth):
    if state.game_over_check():
      return True
    if depth == self.depth:
      return True
    else:
      return False


  """
  The evaluate function must return an integer value
  representing the utility function of the board.
  """
  def evaluate(self, state):
    # set parameter
    W = 0.17 * 0.5
    # W = 0
    (over, winner) = state.is_over()
    if over:
      if self.id == state.get_winner():
        return 1000
      else:
        return -1000
    else:
      count1 = []
      score1 = 0
      count2 = []
      score2 = 0
      # count each player's 
      for r in range(state.size):
        for c in range(state.size):
          if not state.is_empty(r, c):
            height = len(state.board[r][c])
            piece_type, owner = state.board[r][c].top()
            if owner == self.id:
              if piece_type == STANDING_STONE:
                score1 -= 1
              else:
                count1.append([r, c])
                score1 += 1 + height * W
            else:
              if piece_type == STANDING_STONE:
                score2 -= 1
              else:
                count2.append([r, c])
                score2 += 1 + height * W
    return score1 - score2
      


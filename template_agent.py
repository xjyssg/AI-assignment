from agent import AlphaBetaAgent
import minimax

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
    return minimax.search(state, self)

  """
  The successors function must return (or yield) a list of
  pairs (a, s) in which a is the action played to reach the
  state s.
  """
  def successors(self, state):
    action_list = state.get_current_player_actions()
    candidates = []
    for action in action_list:
      current_state = state.copy()
      current_state.apply_action(action)
      if current_state:
        candidates.append((action, current_state))
    generator = (candidate for candidate in candidates)
    # raise RuntimeError(len(candidates))
    # a = [candidate for candidate in candidates]
    # raise RuntimeError(len(a))
    return generator
    


  """
  The cutoff function returns true if the alpha-beta/minimax
  search has to stop and false otherwise.
  """
  def cutoff(self, state, depth):
    if state.game_over_check():
      return True
    # raise RuntimeError(len(state.history))
    # if len(state.history) > depth:
    #   return True
    # else:
    #   return False
    # if len(state.history) > 1:
      # raise RuntimeError((state.history), depth)
    # if len(state.history) == depth - 1:
    if depth == 1:
      # raise RuntimeError(state.history)
      return True
    else:
      return False

    # if depth == 0:
    #   return False
    # elif depth == 1:
    #   return True
    # elif depth == 2:
    #   return False 
    # else:
    #   return depth + len(state.history)

  """
  The evaluate function must return an integer value
  representing the utility function of the board.
  """
  def evaluate(self, state):
    (over, winner) = state.is_over()
    if over:
      if self.id == state.get_winner():
        return 1000
      else:
        return -1000
    else:
      count = state.control_count()
      return count[self.id] - count[1 - self.id]

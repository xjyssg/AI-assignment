import sys
sys.path.append('./public/')

class MatchLogger():

  def __init__(self, log_dir):
    self.log_dir = log_dir

  def setup_match_log(self, agent1, agent2, id):
    self.writer = open(self.log_dir + '/' + agent1 + '-vs-' + agent2 + '_' + str(id), 'w')
  
  def write_initial(self, state):
    pass#self.writer.write(str(state))
  
  def write_log(self, line):
    self.writer.write(line + '\n')

  def write_action(self, player, action):
    self.writer.write('#ACTION ' + str(player) + ' ' + action_to_str(action) + '\n')

  def close_game_log(self):
    self.writer.close()

"""
Convert a valid action into a string for logging
"""
def action_to_str(action):
  try:
    s = ''
    for x in action:
      if type(x) == tuple:
        for y in x:
          s = s + str(y) + ' '
      else:
        s = s + str(x) + ' '
    return s.strip()
  except Exception:
    return None

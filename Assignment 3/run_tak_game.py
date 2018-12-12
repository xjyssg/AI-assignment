from run_game_tools import *
from tak import *
from match_logger import *

if __name__ == '__main__':
  initial_state = TakState(5, 6)
  agent0 = getattr(__import__('contest_agent'), 'MyAgent')()
  agent0.set_id(1)
  agent1 = getattr(__import__('smart_agent'), 'MyAgent')()
  agent1.set_id(0)
  logger = MatchLogger('logs')
  logger.setup_match_log(agent0.get_name(), agent1.get_name(), 0)
  res = make_match(initial_state, [agent0, agent1], 300, logger)
  print(res)

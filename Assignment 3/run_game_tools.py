import sys
sys.path.append('./public/')
import traceback
import time
import random
import signal
import math
import datetime
from match_logger import MatchLogger

def handler(signum, frame):
    raise Exception('end of time')

def play_game(initial_state, names, players, total_time, verbose, logger):
    # create the initial state
    state = initial_state
    # initialize the time left for each player
    time_left = [ total_time for i in range(len(players)) ]
    timedout = -1
    crashed = -1
    invalidaction = -1
    quit = -1
    exception = ''
    action = None
    last_action = None
    if logger != None:
        logger.write_initial(initial_state)
    # loop until the game is over
    while not state.game_over():
        #print(state)
        cur_player = state.get_cur_player()
        start = 0
        end = 0
        try:
            # get the start time
            start = time.time()
            action = get_action_timed(players[cur_player], state, last_action, time_left[cur_player])
            # get the end time
            end = time.time()
        except TimeoutError:
            # set that the current player timed out
            timedout = cur_player
            # write on the log that the current player timed out
            if logger != None:
                logger.write_log(str(cur_player) + ' timeout')
            break
        except Exception as e:
            trace = traceback.format_exc().split('\n')
            exception = trace[len(trace) - 2]
            # set that the current player crashed
            crashed = cur_player
            # write that the current player crashed
            if logger != None:
                logger.write_log(str(cur_player) + ' crashed (' + str(e) + ')')
            break
        else:
            # compute enlapsed time
            enlapsed = math.floor(end - start)
            if logger != None:
              logger.write_log(str(enlapsed) + ' ' + str(time_left[cur_player]))
            # update time
            time_left[cur_player] = time_left[cur_player] - enlapsed
            # check if the action is valid
            try:
                if action[0] == 'rage-quit':
                    # the player wants to quit
                    quit = cur_player
                    if logger != None:
                        logger.write_log(str(cur_player) + ' rage-quit')
                    break
                elif state.is_action_valid(action):
                    # the action is valid so we can apply the action to the state
                    # write the action of the current player on the log
                    if logger != None:
                        logger.write_action(cur_player, action)
                    state.apply_action(action)
                    last_action = action
                else:
                    print('invalid ' + str(action)) 
                    # set that the current player gave an invalid action
                    invalidaction = cur_player
                    if logger != None:
                        logger.write_log(str(cur_player) + ' invalid action')
                    break
            except Exception:
                # set that the current player gave an invalid action
                invalidaction = cur_player
                if logger != None:
                    logger.write_log(str(cur_player) + ' could not apply action')
                break
    if logger != None:
        # finish the log by writting the scores and the winner
        logger.write_log(str(state.get_scores()))
        logger.write_log(str(state.get_winner()))
        # close the log
        logger.close_game_log()
    # output the result of the game: 0 if player 0 wins, 1 if player 1 wins and -1 if it is a draw
    # first check if there was timeout, crash, invalid action or quit
    if timedout != -1:
        return (1 - timedout, names[timedout] + ' timed out', total_time - time_left[0], total_time - time_left[1], state.get_scores())
    elif crashed != -1:
        return (1 - crashed, names[crashed] + ' crashed: ' + exception, total_time - time_left[0], total_time - time_left[1], state.get_scores())
    elif invalidaction != -1:
        return (1 - invalidaction, names[invalidaction] + ' gave an invalid action: ' + str(action), total_time - time_left[0], total_time - time_left[1], state.get_scores())
    elif quit != -1:
        return (1 - quit, names[quit] + ' rage quit', total_time - time_left[0], total_time - time_left[1], state.get_scores())    
    else:
        # all is ok, output the winner
        return (state.get_winner(), 'scores: ' + str(state.get_scores()), total_time - time_left[0], total_time - time_left[1], state.get_scores())

"""
Define behavior in case of timeout.
"""
def handle_timeout(signum, frame):
    raise TimeoutError()

"""
Get an action from player with a timeout.
"""
def get_action_timed(player, state, last_action, time_left):
    signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(time_left)
    try:
        action = player.get_action(state.copy(), last_action, time_left)
    finally:
        signal.alarm(0)
    return action

"""
Run a game between the groups and log the result with logger.
"""
def run_tournament_match(initial_state, groups, logger, total_time):
    names = [g.get_display_name() for g in groups]
    agents = [g.agent for g in groups]
    return play_game(initial_state, names, agents, total_time, False, logger)

def make_match(initial_state, agents, time, logger):
    names = [a.get_name() for a in agents]
    if agents[0].id == 0:
      return play_game(initial_state, names, agents, time, False, logger)
    else:
      agents.reverse()
      return play_game(initial_state, names, agents, time, False, logger)

def make_n_matches(initial_state, agents, logger):
    names = [a.get_name() for a in agents]
    results = [ ]
    for i in range(n):
        res = play_game(initial_state.copy(), names, agents, 600, False, logger)
        results.append(res)
    for x in results:
      print(x)


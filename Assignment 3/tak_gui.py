import math
import sys
import os
import random
import argparse
import time
import signal
from threading import Thread
from tak import *
from gui import *
from interface import *
import color
from agent import *
from layout_manager import *

GRID_SIZE = 105

GRID_DELTA = { }
GRID_DELTA[3] = (38, 40)
GRID_DELTA[4] = (42, 39)
GRID_DELTA[5] = (38, 40)
GRID_DELTA[6] = (40, 40)
GRID_DELTA[8] = (40, 40)

DEBUG = 0


FONT_NAME = 'monospace'

SPACINGS = {
  'board_to_info': 20,
  'top_to_info': 15,
  'piece_spacing': 5,
  'piece_cell_dy': 0,
  'buttons_to_board': 10,
  'small_board': 2,
}

class PieceTypeArray():

  def __init__(self, state, r, c):
    self.piece_type = [ ]
    if state.stones[state.cur_player] > 0:
      self.piece_type.append(FLAT_STONE)
      if state.turn >= 3:
        self.piece_type.append(STANDING_STONE)
    if state.capstones[state.cur_player] > 0 and state.turn >= 3:
      self.piece_type.append(CAP_STONE)
    self.index = 0
  
  def get_type(self):
    return self.piece_type[self.index]
  
  def next(self):
    self.index = (self.index + 1) % len(self.piece_type)
    return self.get_type()

class PieceSelector():

  def __init__(self, state, r, c, max):
    self.max = max
    self.nb_selected = 1
    self.row = r
    self.col = c
  
  def next(self):
    self.nb_selected = self.nb_selected + 1
    if self.nb_selected > self.max:
      self.nb_selected = 1

class GUIState():

  def __init__(self, gui):
    self.gui = gui
    self.over_cell = None
    self.selected_cell = None
    self.state = gui.state.copy()
    self.function = self.init_human_action
    self.action = None
    self.piece_selector = None
  
  def can_finish(self):
    return self.action != None

  """
  Execute the current state
  """
  def execute(self):
    self.function()

  """
  State: initialize the action of a human
  """
  def init_human_action(self):
    self.gui.buttons['finish'].set_active(False)
    self.state = gui.state.copy()
    self.function = self.select_cell

  """
  State: the player is selecting an a cell (left click for add piece and right for movements)
  """
  def select_cell(self):
    events = pygame.event.get()
    # handle human player
    # loop over events and update game
    for event in events:
      # check for quit event
      if event.type == pygame.QUIT:
        # quit the game
        pygame.quit()
        sys.exit()
      elif event.type == pygame.MOUSEMOTION: # handle mouse movement
        mouse_x, mouse_y = event.pos
        if gui.grid.in_bounds(mouse_x, mouse_y):
          r, c = gui.grid.get_row_col(mouse_x, mouse_y)
          self.over_cell = (r, c)
        else:
          self.over_cell = None
      elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # handle mouse left click
        mouse_x, mouse_y = event.pos
        if gui.grid.in_bounds(mouse_x, mouse_y):
          r, c = gui.grid.get_row_col(mouse_x, mouse_y)
          # check whether cell at row r and column c is empty 
          # and the current player still has pieces to play
          if len(self.state.board[r][c]) == 0:
            if self.state.is_empty(r, c) and self.state.cur_player_has_pieces():
              self.piece_type_array = PieceTypeArray(self.state, r, c)
              cur_type = self.piece_type_array.get_type()
              self.action = ('place', cur_type, r, c)
              # cell is empty, we are placing a new piece
              self.gui.buttons['finish'].set_active(True)
              self.selected_cell = (r, c)
              self.over_cell = None
              if self.state.turn <= 2:
                self.state.set_top_piece(r, c, cur_type, 1 - self.state.cur_player)
              else:
                self.state.set_top_piece(r, c, cur_type, self.state.cur_player)
              self.function = self.change_piece
            else:
              # the position is not empty
              piece_type, owner = self.state.get_top_piece(r, c)
              if piece_type == STANDING_STONE and self.state.capstones[self.state.cur_player] > 0:
                # place a piece on top of a standing stone (can only be a capstone)
                self.over_cell = None
                self.selected_cell = (r, c)
                self.action = ('place', CAP_STONE, r, c)
                self.state.apply_action(self.action)
                self.gui.buttons['finish'].set_active(True)
                self.function = self.wait_finish
              elif piece_type != STANDING_STONE:
                # place a piece on top of a flatstone or capstone
                self.gui.buttons['finish'].set_active(True)
                self.selected_cell = (r, c)
                self.over_cell = None
                self.piece_type_array = PieceTypeArray(self.state, r, c)
                cur_type = self.piece_type_array.get_type()
                self.state.add_piece_cur_player(r, c, cur_type)            
                self.action = ('place', cur_type, r, c)
                self.function = self.change_piece
      elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # handle mouse right click
        mouse_x, mouse_y = event.pos
        if gui.grid.in_bounds(mouse_x, mouse_y):
          r, c = gui.grid.get_row_col(mouse_x, mouse_y)
          # check whether cell at row r and column c is empty 
          # and the current player still has pieces to play
          if not self.state.is_empty(r, c) and self.state.get_top_piece(r, c)[1] == self.state.cur_player and self.state.turn >= 3:
            self.piece_selector = PieceSelector(self.state, r, c, min(len(self.state.board[r][c]), self.state.size))
            self.selected_cell = (r, c)
            self.function = self.select_pieces
  
      
    # check for button clicks
    self.gui.check_button_click(events)

  """
  State: the player is selecting how many pieces to move
  """
  def select_pieces(self):
    events = pygame.event.get()
    # handle human player
    # loop over events and update game
    for event in events:
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # handle mouse right click
        self.piece_selector.next()
      elif event.type == pygame.MOUSEMOTION: # handle mouse motion
        mouse_x, mouse_y = event.pos
        if gui.grid.in_bounds(mouse_x, mouse_y):
          r, c = gui.grid.get_row_col(mouse_x, mouse_y)
          if self.piece_selector != None:
            k = self.piece_selector.nb_selected
            can_move = self.state.can_move_top_k(self.piece_selector.row, self.piece_selector.col, r, c, k)
            if gui.grid.are_adjacent(r, c, self.piece_selector.row, self.piece_selector.col) and can_move:
              self.over_cell = (r, c)
            else:
              self.over_cell = None
          else:
            self.over_cell = None
      elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # handle mouse left click
          # move the selected pieces
          mouse_x, mouse_y = event.pos
          if gui.grid.in_bounds(mouse_x, mouse_y):
            r, c = gui.grid.get_row_col(mouse_x, mouse_y)
            k = self.piece_selector.nb_selected
            can_move = self.state.can_move_top_k(self.piece_selector.row, self.piece_selector.col, r, c, k)
            if gui.grid.are_adjacent(r, c, self.piece_selector.row, self.piece_selector.col) and can_move:
              self.over_cell = None
              self.delta = (r - self.piece_selector.row, c - self.piece_selector.col)
              self.selected_cell = (r, c)
              self.state.move_top_k(self.piece_selector.row, self.piece_selector.col, r, c, self.piece_selector.nb_selected)
              self.action = ('move', self.piece_selector.row, self.piece_selector.col, self.delta, [self.piece_selector.nb_selected])
              self.piece_selector = PieceSelector(self.state, r, c, self.piece_selector.nb_selected - 1)
              self.gui.buttons['finish'].set_active(True)
              #if self.gui.grid.is_border(r, c) or self.piece_selector.max == 0 or not self.state.can_move_top_k(r, c, r + self.delta[0], c + self.delta[1], 1):
              if self.piece_selector.max == 0 or not self.state.can_move_top_k(r, c, r + self.delta[0], c + self.delta[1], 1):
                self.piece_selector = None
                self.function = self.wait_finish
              else:
                self.function = self.moving_pieces
    # check for button clicks
    self.gui.check_button_click(events)

  """
  State: the player is moving pieces
  """
  def moving_pieces(self):
    events = pygame.event.get()
    # handle human player
    # loop over events and update game
    for event in events:
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # handle mouse right click
        self.piece_selector.next()
      elif event.type == pygame.MOUSEMOTION:
        mouse_x, mouse_y = event.pos
        if gui.grid.in_bounds(mouse_x, mouse_y):
          r, c = gui.grid.get_row_col(mouse_x, mouse_y)
          delta = (r - self.piece_selector.row, c - self.piece_selector.col)
          k = self.piece_selector.nb_selected
          can_move = self.state.can_move_top_k(self.piece_selector.row, self.piece_selector.col, r, c, k)  
          if delta == self.delta and can_move:  
            self.over_cell = (r, c)
          else:
            self.over_cell = None
        else:
          self.over_cell = None
      elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # handle mouse left click
          # move the selected pieces
          mouse_x, mouse_y = event.pos
          if gui.grid.in_bounds(mouse_x, mouse_y):
            r, c = gui.grid.get_row_col(mouse_x, mouse_y)
            delta = (r - self.piece_selector.row, c - self.piece_selector.col)
            k = self.piece_selector.nb_selected
            can_move = self.state.can_move_top_k(self.piece_selector.row, self.piece_selector.col, r, c, k)
            if delta == self.delta and can_move:
              self.over_cell = None
              self.selected_cell = (r, c)
              self.state.move_top_k(self.piece_selector.row, self.piece_selector.col, r, c, self.piece_selector.nb_selected)
              self.action[4].append(self.piece_selector.nb_selected)
              self.piece_selector = PieceSelector(self.state, r, c, self.piece_selector.nb_selected - 1)
              self.gui.buttons['finish'].set_active(True)
              if self.piece_selector.max == 0 or not self.state.can_move_top_k(r, c, r + self.delta[0], c + self.delta[1], 1):
                self.piece_selector = None
                self.function = self.wait_finish
              else:
                self.function = self.moving_pieces
    # check for button clicks
    self.gui.check_button_click(events)

  """
  State: waiting for the player to click the finish button
  """
  def wait_finish(self):
    events = pygame.event.get()
    self.gui.check_button_click(events)

  """
  State: the playing is selecting the kind of piece he wants to place
  """
  def change_piece(self):
    events = pygame.event.get()
    # handle human player
    # loop over events and update game
    for event in events:
      # check for quit event
      if event.type == pygame.QUIT:
        # quit the game
        pygame.quit()
        sys.exit()
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_x, mouse_y = event.pos
        if gui.grid.in_bounds(mouse_x, mouse_y):
          r, c = gui.grid.get_row_col(mouse_x, mouse_y)
          # check whether the clicked cell is the current cell
          if (r, c) == self.selected_cell and self.state.turn >= 3:
            # click ok, change to the next piece type
            cur_type = self.piece_type_array.next()
            self.action = ('place', cur_type, r, c)
            self.state.set_top_piece_cur_player(r, c, cur_type)
    # check for button clicks
    self.gui.check_button_click(events)
  

class TakGUI(GUI):

  def __init__(self, state, player_type, agents, timeout, wait):
    super(TakGUI, self).__init__(state, player_type, agents, timeout, wait)
    # load images
    self.images = { }
    self.load_and_register_image('board', 'resources/board_{0}.png'.format(state.size))
    self.load_and_register_image('red', 'resources/red.png')
    self.load_and_register_image('blue', 'resources/blue.png')
    self.load_and_register_image('red_selected', 'resources/red_g.png')
    self.load_and_register_image('blue_selected', 'resources/blue_g.png')
    self.load_and_register_image_scale('red_icon', 'resources/red.png', 2)
    self.load_and_register_image_scale('blue_icon', 'resources/blue.png', 2)
    self.load_and_register_image_scale('red_icon_cur', 'resources/red_y.png', 2)
    self.load_and_register_image_scale('blue_icon_cur', 'resources/blue_y.png', 2)
    self.load_and_register_image('red_cap', 'resources/red_cap.png')
    self.load_and_register_image('blue_cap', 'resources/blue_cap.png')
    self.load_and_register_image('red_cap_selected', 'resources/red_cap_g.png')
    self.load_and_register_image('blue_cap_selected', 'resources/blue_cap_g.png')
    self.load_and_register_image_scale('red_cap_icon', 'resources/red_cap.png', 2)
    self.load_and_register_image_scale('blue_cap_icon', 'resources/blue_cap.png', 2)
    self.load_and_register_image_scale('red_cap_icon_cur', 'resources/red_cap_y.png', 2)
    self.load_and_register_image_scale('blue_cap_icon_cur', 'resources/blue_cap_y.png', 2)
    self.load_and_register_image_rotate('red_rot', 'resources/red.png', 90)
    self.load_and_register_image_rotate('blue_rot', 'resources/blue.png', 90)
    self.load_and_register_image_rotate('red_rot_selected', 'resources/red_g.png', 90)
    self.load_and_register_image_rotate('blue_rot_selected', 'resources/blue_g.png', 90)
    self.load_and_register_image('cursor_over', 'resources/cursor.png')
    self.load_and_register_image('cursor_selected', 'resources/selected.png')
    self.load_and_register_image('button_finish_active', 'resources/button_finish_g.png')
    self.load_and_register_image('button_finish_inactive', 'resources/button_finish_r.png')
    self.load_and_register_image('button_undo_active', 'resources/button_undo_g.png')
    self.load_and_register_image('button_undo_inactive', 'resources/button_undo_r.png')
    self.load_and_register_image('red_sq', 'resources/red_sq.png')
    self.load_and_register_image('red_sq_g', 'resources/red_sq_g.png')
    self.load_and_register_image('red_sq_x', 'resources/red_sq_x.png')
    self.load_and_register_image('red_sq_cap', 'resources/red_sq_cap.png')
    self.load_and_register_image('red_sq_cap_g', 'resources/red_sq_cap_g.png')
    self.load_and_register_image('blue_sq', 'resources/blue_sq.png')
    self.load_and_register_image('blue_sq_g', 'resources/blue_sq_g.png')
    self.load_and_register_image('blue_sq_x', 'resources/blue_sq_x.png')
    self.load_and_register_image('blue_sq_cap', 'resources/blue_sq_cap.png')
    self.load_and_register_image('blue_sq_cap_g', 'resources/blue_sq_cap_g.png')
    self.load_and_register_image('gray_sq', 'resources/gray_sq.png')

    self.buttons = { }
    self.buttons['finish'] = Button(self, 'button_finish_active', 'button_finish_inactive', self.finish_human_action, False)
    self.buttons['finish'].set_hotkey(pygame.K_f)
    self.buttons['undo'] = Button(self, 'button_undo_active', 'button_undo_inactive', self.undo_human_action, True)
    self.buttons['undo'].set_hotkey(pygame.K_u)
    self.piece_height = self.get_image_height(self.images['red']) 
    dx, dy = GRID_DELTA[self.state.size]
    self.text_height = self.get_image_size_from_id('red_icon')[1]
    self.grid = Grid(self.state.size, self.state.size, GRID_SIZE, GRID_SIZE, dx, dy)
    self.register_scalable(self.grid)
    self.gui_state = GUIState(self)
  
  def change_scale(self, scale):
    for k in self.images:
      self.images[k] = self.scale_image(self.images[k], scale)
    self.grid.change_scale(scale)
    self.piece_height = self.get_image_height(self.images['red'])
    for k in SPACINGS:
      SPACINGS[k] = round(SPACINGS[k] * scale)
    for k in self.buttons:
      self.buttons[k].set_scale(scale)
  
  def get_window_size(self):
    board_width, board_height = self.get_image_size(self.images['board'])
    width = board_width + self.state.size * (SPACINGS['small_board'] + self.get_image_width(self.images['gray_sq'])) + 2 * SPACINGS['board_to_info']
    height = board_height + 100
    return width, height

  def draw_screen(self):
    self.text_height = self.get_image_size_from_id('red_icon')[1]
    # draw the board
    self.draw_image_abs('board', 0, 0, 'board')
    # draw the cell below the mouse, if one exists
    over_cell = self.gui_state.over_cell
    if over_cell != None:
      rect = self.grid.get_rect(over_cell[0], over_cell[1])
      self.draw_image_abs('cursor_over', rect.x1, rect.y1, None)
    # draw the selected cell, if one exists
    selected_cell = self.gui_state.selected_cell
    if selected_cell != None:
      rect = self.grid.get_rect(selected_cell[0], selected_cell[1])
      self.draw_image_abs('cursor_selected', rect.x1, rect.y1, None)
    # draw the amouts of pieces of each kind
    s1 = ''
    s2 = ''
    if self.state.cur_player == 0:
      s1 = '_cur'
    else:
      s2 = '_cur'
    self.draw_image_rightof('red_icon' + s1, 'board', 0, 18, True, 'red_icon')
    self.draw_text_rightof('x{0}'.format(self.state.stones[0]), 'monospace', self.text_height, color.WHITE, 'red_icon', 0, 0, False, None)
    self.draw_image_below('red_cap_icon' + s1, 'red_icon', 0, 5, True, 'red_cap_icon')
    self.draw_text_rightof('x{0}'.format(self.state.capstones[0]), 'monospace', self.text_height, color.WHITE, 'red_cap_icon',  0, 0, False, None)
    self.draw_image_below('blue_icon' + s2, 'red_cap_icon', 0, 5, True, 'blue_icon')
    self.draw_text_rightof('x{0}'.format(self.state.stones[1]), 'monospace', self.text_height, color.WHITE, 'blue_icon',  0, 0, False, None)
    self.draw_image_below('blue_cap_icon' + s2, 'blue_icon', 0, 5, True, 'blue_cap_icon')
    self.draw_text_rightof('x{0}'.format(self.state.capstones[1]), 'monospace', self.text_height, color.WHITE, 'blue_cap_icon',  0, 0, False, None)
    # draw buttons
    self.draw_button_below(self.buttons['finish'], 'blue_cap_icon', 0, 10, True, 'finish')
    self.draw_button_rightof(self.buttons['undo'], 'finish', 5, 0, True, 'undo')
    # draw mini board
    path_pos = [ ]
    if self.state.game_over():
      path_pos = self.state.get_winning_path()
    board = self.gui_state.state.board
    image_ids = [ ]
    for r in range(self.state.size):
      for c in range(self.state.size):
        # compute the image name
        image_id = ''
        if len(board[r][c]) == 0:
          image_id = 'gray_sq'
        else:
          piece_type, owner = board[r][c].top()
          if owner == 0:
            image_id = 'red_sq'
          else:
            image_id = 'blue_sq'
          if piece_type == STANDING_STONE:
            image_id += '_x'
          elif piece_type == CAP_STONE:
            image_id += '_cap'
        if (r, c) in path_pos:
          image_id += '_g'
        image_ids.append(image_id)
    self.draw_images_in_grid_below(self.state.size, image_ids, 'finish', 0, 10, True, 'mini_board', 2)
    # draw pieces on the board
    for r in range(self.state.size):
      for c in range(self.state.size):
        self.draw_cell(r, c)
    # draw territory info
    self.draw_text_below('territory:', 'monospace', self.text_height, color.WHITE, 'mini_board', 0, 0, True, 'territory')
    red, blue = self.gui_state.state.control_count()
    red = str(red)
    if len(red) == 1: red = ' ' + red
    blue = str(blue)
    if len(blue) == 1: blue = ' ' + blue
    self.draw_text_below(red, 'monospace', self.text_height, color.RED, 'territory', 0, 0, True, 'red')
    self.draw_text_rightof(' vs ', 'monospace', self.text_height, color.WHITE, 'red', 0, 0, True, 'vs1')
    self.draw_text_rightof(blue, 'monospace', self.text_height, color.BLUE, 'vs1', 0, 0, True, 'blue')
    # draw time
    self.draw_text_below('time left:', 'monospace', self.text_height, color.WHITE, 'red', 0, 0, True, 'time')
    self.draw_text_below(self.get_time_left_str(0), 'monospace', self.text_height, color.RED, 'time', 0, 0, True, 'tred')
    self.draw_text_rightof(' vs ', 'monospace', self.text_height, color.WHITE, 'tred', 0, 0, True, 'vs2')
    self.draw_text_rightof(self.get_time_left_str(1), 'monospace', self.text_height, color.BLUE, 'vs2', 0, 0, True, 'tblue')
    # draw winner
    if self.state.game_over():
      self.draw_text_below('game over!', 'monospace', self.text_height, color.YELLOW, 'tred', 0, 0, True, 'gameover')
      self.draw_text_below('winner: ', 'monospace', self.text_height, color.YELLOW, 'gameover', 0, 0, True, 'winner')
      if self.state.winner == 0:
        self.draw_text_rightof('red', 'monospace', self.text_height, color.RED, 'winner', 0, 0, True, 'win')
      else:
        self.draw_text_rightof('blue', 'monospace', self.text_height, color.BLUE, 'winner', 0, 0, True, 'win')
    else:
      self.create_placeholder_below('tred', 0, 3 * self.text_height, 0, 0, True, 'pc1')
    # draw info
    self.draw_text_below('current player: ', 'monospace', self.text_height, color.WHITE, 'board', 20, 0, True, 'curplayer')
    if self.state.cur_player == 0:
      self.draw_text_rightof('red', 'monospace', self.text_height, color.RED, 'curplayer', 0, 0, True, 'player')
    else:
      self.draw_text_rightof('blue', 'monospace', self.text_height, color.BLUE, 'curplayer', 0, 0, True, 'player')
    if self.player_type[self.state.cur_player] == 'human':
      self.draw_text_below('human player', 'monospace', self.text_height, color.WHITE, 'curplayer', 0, 0, True, 'type')
    else: 
      self.draw_text_below('ai agent (' + self.agents[self.state.cur_player].get_name()[0:36] + ')', 'monospace', self.text_height, color.WHITE, 'curplayer', 0, 0, True, 'type')
    if self.state.invalid_player != None:
      self.draw_text_below('invalid action', 'monospace', self.text_height, color.WHITE, 'type', 0, 0, True, 'invalid')
    else:
      self.create_placeholder_below('type', 0, self.text_height, 0, 0, True, 'pc2')
    lowest = self.get_lowest_element_id()
    self.create_placeholder_below(lowest, 0, round(18 * self.scale), 0, 0, True, 'bottom_margin')
    rightmost = self.get_rightmost_element_id()
    self.create_placeholder_rightof(rightmost, round(18 * self.scale), 0, 0, 0, True, 'right_margin')    

  def draw_cell(self, r, c):
    rect = self.grid.get_rect(r, c)
    pieces = self.gui_state.state.board[r][c]
    i = 0
    left = len(pieces)
    if self.gui_state.piece_selector != None and r == self.gui_state.piece_selector.row and c == self.gui_state.piece_selector.col:
      # draw selection
      for piece_type, owner in pieces:
        s = ''
        if left <= self.gui_state.piece_selector.nb_selected:
          s = '_selected'
        if piece_type == FLAT_STONE:
          image_id = 'red' + s if owner == 0 else 'blue' + s
        elif piece_type == STANDING_STONE:
          image_id = 'red_rot' + s if owner == 0 else 'blue_rot' + s
        elif piece_type == CAP_STONE:
          image_id = 'red_cap' + s if owner == 0 else 'blue_cap' + s
        if i == 0:
          w, h = self.get_image_size_from_id(image_id)
          _, y = rect.get_center()
          y = y - h + self.get_image_size_from_id('red')[1]
          x = rect.x1 + (rect.get_width() - w) // 2
          self.draw_image_abs(image_id, x, y, 'cell_{0}_{1}_{2}'.format(r, c, i))
        else:
          dx = 0
          if piece_type == STANDING_STONE:
            w1, _ = self.get_image_size_from_id('red')
            w2, _ = self.get_image_size_from_id('red_rot')
            dx = (w1 - w2) // 2
          self.draw_image_above(image_id, 'cell_{0}_{1}_{2}'.format(r, c, i - 1), dx, 0, False, 'cell_{0}_{1}_{2}'.format(r, c, i))
        i += 1
        left -= 1
    else:
      # draw normal
      for piece_type, owner in pieces:  
        if piece_type == FLAT_STONE:
          image_id = 'red' if owner == 0 else 'blue'
        elif piece_type == STANDING_STONE:
          image_id = 'red_rot' if owner == 0 else 'blue_rot'
        elif piece_type == CAP_STONE:
          image_id = 'red_cap' if owner == 0 else 'blue_cap'
        if i == 0:
          w, h = self.get_image_size_from_id(image_id)
          _, y = rect.get_center()
          y = y - h + self.get_image_size_from_id('red')[1]
          x = rect.x1 + (rect.get_width() - w) // 2
          self.draw_image_abs(image_id, x, y, 'cell_{0}_{1}_{2}'.format(r, c, i))
        else:
          dx = 0
          if piece_type == STANDING_STONE:
            w1, _ = self.get_image_size_from_id('red')
            w2, _ = self.get_image_size_from_id('red_rot')
            dx = (w1 - w2) // 2
          self.draw_image_above(image_id, 'cell_{0}_{1}_{2}'.format(r, c, i - 1), dx, 0, False, 'cell_{0}_{1}_{2}'.format(r, c, i))
        i += 1
  
  def handle_human(self):
    self.gui_state.execute()

  def finish_human_action(self):
    action = self.gui_state.action
    self.state.apply_action(action)
    self.gui_state = GUIState(self)
    self.buttons['finish'].set_active(False)

  def handle_ai_action(self, action):
    if self.state.is_action_valid(action):
      self.state.apply_action(action)
      self.gui_state = GUIState(self)
      

  def undo_human_action(self):
    self.gui_state = GUIState(self)
 
  def check_button_click(self, events):
    for event in events:
      if event.type == pygame.MOUSEBUTTONDOWN:
        for k in self.buttons:
          if self.buttons[k].is_active():
            mouse_x, mouse_y = event.pos
            self.buttons[k].check_and_action(mouse_x, mouse_y)
    pressed = pygame.key.get_pressed()
    for k in self.buttons:
      if self.buttons[k].hotkey != None and pressed[self.buttons[k].hotkey] != 0 and self.buttons[k].is_active():
        self.buttons[k].action() 

if __name__ == "__main__":
  # process the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('-t', help='total number of seconds credited to each player')
  parser.add_argument('-size', help='board size (3,4,5,6 or 8)')
  parser.add_argument('-ai0', help='path to the ai that will play as player 0')
  parser.add_argument('-ai1', help='path to the ai that will play as player 1')
  #parser.add_argument('-w', help='time to wait after ai action')
  parser.add_argument('-init', help='initial state file')
  parser.add_argument('-max_h', help='max height')
  args = parser.parse_args()
  # set the time to play
  timeout = int(args.t) if args.t != None else 600
  # set board size
  size = int(args.size) if args.size != None else 5
  if not size in [3, 4, 5, 6, 8]:
      raise Exception('the size should be either 3,4,5,6 or 8')
  #wait = float(args.w) if args.w != None else 0
  max_height = int(args.max_h) if args.max_h != None else 6
  player_type = [ 'human', 'human' ]
  player_type[0] = args.ai0 if args.ai0 != None else 'human'
  player_type[1] = args.ai1 if args.ai1 != None else 'human'
  for i in range(2):
    if player_type[i].endswith('.py'):
      player_type[i] = player_type[i][:-3]
  agents = [ None for _ in range(2) ]
  # load the agents
  for i in range(2):
    if player_type[i] != 'human':
      j = player_type[i].rfind('/')
      # extract the dir from the agent
      dir = player_type[i][:j]
      # add the dir to the system path
      sys.path.append(dir)
      # extract the agent filename
      file = player_type[i][j+1:]
      # create the agent instance
      agents[i] = getattr(__import__(file), 'MyAgent')()
      agents[i].set_id(i)
  # initialize and run the game
  init_state = TakState(size, max_height)
  if args.init != None:
    fill_instance_file(init_state, args.init)
  gui = TakGUI(init_state, player_type, agents, timeout, 0)
  gui.run()

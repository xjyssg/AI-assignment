import random
import pygame
import os
from interface import *
import time
from threading import Thread
import threading
from math import ceil
import color

def get_action_threaded(state, last_action, agent, timeleft):
  result = [ ]
  thread = Thread(target=get_action, args=(state, last_action, agent, timeleft, result))
  thread.start()
  return result

def get_action(state, last_action, agent, timeleft, result):
  action = agent.get_action(state, last_action, timeleft)
  result.append(action)

def scale_image(image, scale):
  w = image.get_rect().size[0]
  h = image.get_rect().size[1]
  return pygame.transform.scale(image, (round(w * scale), round(h * scale)))

def load_image(path):
  return pygame.image.load(path)

def scale_image(image, scale):
  w = image.get_rect().size[0]
  h = image.get_rect().size[1]
  return pygame.transform.scale(image, (round(w * scale), round(h * scale)))
  
def rotate_image(image, angle):
  return pygame.transform.rotate(image, angle)

"""
Class to represent a button.
"""
class Button():

  """
  Button constructor.

  gui:            the gui containing the button
  active_image:   the image used to represent the button when the button is active
  inactive_image: the image used to represent the button when the button is not active
  action:         a function to be executed when the button is clicked
  active:         the initial state of the button (true by default)

  It is assumed that the active and inactive images have the same size. 
  The clicked area of the button corresponds to the rectangle of the image.
  This means that a circular button will be clickable on the corders also.
  """
  def __init__(self, gui, active_image_id, inactive_image_id, action, active = True):
    self.gui = gui
    self.x = 0
    self.y = 0
    self.active_image_id = active_image_id
    self.inactive_image_id = inactive_image_id
    self.action = action
    self.active = active
    self.hotkey = None
  
  """
  Set a hot key for the button. The key has to be a pygame.key instance. 
  """
  def set_hotkey(self, hotkey):
    self.hotkey = hotkey

  """
  Get the current image of the button. This depends on the button state.
  """
  def get_image_id(self):
    if self.active: return self.active_image_id
    else: return self.inactive_image_id

  """
  Set the button state.
  """
  def set_active(self, active):
    self.active = active

  """
  Check whether the button is active.
  """
  def is_active(self):
    return self.active

  """
  Set the button position.
  """
  def set_pos(self, x, y):
    self.x = x
    self.y = y

  """
  Given a mouse position checks whether the position is on top of the button. 
  If it is and the button is active then it will perfom the button action.
  """
  def check_and_action(self, mouse_x, mouse_y):
    w, h = self.gui.get_image_size_from_id(self.get_image_id())
    rect = Rect(self.x, self.y, self.x + w, self.y + h)
    if rect.contains(mouse_x, mouse_y) and self.is_active():
      self.action()

"""
Class that represents an image to draw on the screen.

It contains the image and the position on the screen.
"""
class LayoutRect():

  """
  Sprite constructor.

  image: an instance of pygame.image
  x:     the x position on the screen
  y:     the y position on the screen
  """
  def __init__(self, x, y, w, h):
    self.x = x
    self.y = y
    self.w = w
    self.h = h

  """
  Get the position of this sprite.
  """
  def get_pos(self):
    return self.x, self.y
  
  """
  Get the size of this sprite.
  """
  def get_size(self):
    return self.w, self.h
  
  """
  Get the position where we need to draw an image
  to make it appear on the right of this image and
  aligned on the y.
  """
  def get_right(self):
    return self.x + self.w, self.y  
  
  """
  Get the position where we need to draw an image
  to make it appear on the bottom of this image
  and aligned on the x.
  """
  def get_bottom(self):
    return self.x, self.y + self.h


class GUI():

  def __init__(self, state, player_type, agents, timeout, wait):
    # initialize pygame
    pygame.init()
    self.state = state.copy()
    self.player_type = player_type
    self.agents = agents
    self.time_left = [timeout, timeout]
    self.timeout = timeout
    self.wait = wait
    self.elements = { }
    self.images = { }
    self.scalable = [ ]
    self.width = 0
    self.height = 0
    self.scale = 1
  
  def get_time_left_str(self, player):
    if self.time_left[player] > 99 * 3600 + 59 * 60 + 59:
      return 'INFINITY'
    if self.time_left[player] <= 0:
      return 'TIMEDOUT'
    tmp = ceil(self.time_left[player])
    hour = str(tmp // 3600)
    if len(hour) == 1:
      hour = '0' + hour
    tmp %= 3600
    minutes = str(tmp // 60)
    if len(minutes) == 1:
      minutes = '0' + minutes
    tmp %= 60
    seconds = str(tmp)
    if len(seconds) == 1:
      seconds = '0' + seconds
    return '{0}:{1}:{2}'.format(hour, minutes, seconds)
  
  def register_scalable(self, scalable_obj):
    self.scalable.append(scalable_obj)

  """
  Load and register an image to be used.

  identifier: a unique identifier string for your image
  image_path: the path of the image to load
  """
  def load_and_register_image(self, image_id, image_path):
    self.images[image_id] = load_image(image_path)
  
  def get_image_from_id(self, image_id):
    return self.images[image_id]
  
  def get_rightmost_element_id(self):
    m = 0
    rightmost = None
    for k in self.elements:
      elem = self.elements[k]
      if elem.get_right()[0] > m:
        m = elem.get_right()[0]
        rightmost = k
    return rightmost
  
  def get_lowest_element_id(self):
    m = 0
    lowest = None
    for k in self.elements:
      elem = self.elements[k]
      if elem.get_right()[0] > m:
        m = elem.get_bottom()[0]
        lowest = k
    return lowest    


  """
  Get the size of an image from an id.

  image_id: the identifier of the image
  """
  def get_image_size_from_id(self, image_id):
    return self.images[image_id].get_rect().size

  """
  Load and register a scaled image to be used.

  identifier: a unique identifier string for your image
  image_path: the path of the image to load
  scale:      the image scale
  """
  def load_and_register_image_scale(self, image_id, image_path, scale):
    self.images[image_id] = scale_image(load_image(image_path), scale)
  
  """
  Load and register a rotated image to be used.

  identifier: a unique identifier string for your image
  image_path: the path of the image to load
  angle:      the image angle (degrees)
  """
  def load_and_register_image_rotate(self, image_id, image_path, angle):
    self.images[image_id] = rotate_image(load_image(image_path), angle)

  """
  Draw an image on the screen at an absolute position.

  image_id: the id of the image to draw
  x:        the x position to draw (top left)
  y:        the y position to draw (top left)
  id:       a unique id for this element
  """
  def draw_image_abs(self, image_id, x, y, id):
    w, h = self.images[image_id].get_rect().size
    self.screen.blit(self.images[image_id], (x, y))
    if id == None:
      self.elements[image_id] = LayoutRect(x, y, w, h)
    else:
      self.elements[id] = LayoutRect(x, y, w, h) 

  """
  Draw an image on the screen to the right of a given element.

  image_id:  the id of the image to draw
  target_id: the id of the element to which you want to be on the right of
  dx:        an optional x offset (0 be default)
  dy:        an optional y offset (0 by default)
  id:        a unique id for this element
  """
  def draw_image_rightof(self, image_id, target_id, dx, dy, scale_delta, id):
    if scale_delta:
      dx = round(dx * self.scale)
      dy = round(dy * self.scale)
    x, y = self.elements[target_id].get_right()
    self.draw_image_abs(image_id, x + dx, y + dy, id)

  """
  Draw an image on the screen on the bottom of a given element.

  image_id:  the id of the image to draw
  target_id: the id of the element to which you want to be on the bottom of
  dx:        an optional x offset (0 be default)
  dy:        an optional y offset (0 by default)
  id:        a unique id for this element
  """
  def draw_image_below(self, image_id, target_id, dx, dy, scale_delta, id):
    if scale_delta:
      dx = round(dx * self.scale)
      dy = round(dy * self.scale)
    x, y = self.elements[target_id].get_bottom()
    self.draw_image_abs(image_id, x + dx, y + dy, id)
  
  """
  Draw an image on the screen on the bottom of a given element.

  image_id:  the id of the image to draw
  target_id: the id of the element to which you want to be on the top of
  dx:        an optional x offset (0 be default)
  dy:        an optional y offset (0 by default)
  id:        a unique id for this element
  """
  def draw_image_above(self, image_id, target_id, dx, dy, scale_delta, id):
    if scale_delta:
      dx = round(dx * self.scale)
      dy = round(dy * self.scale)
    x, y = self.elements[target_id].get_pos()
    _, h = self.images[image_id].get_rect().size
    self.draw_image_abs(image_id, x + dx, y - h + dy, id)
    
  def create_placeholder_abs(self, x, y, w, h, id):
    self.elements[id] = LayoutRect(x, y, w, h)
  
  def create_placeholder_below(self, target_id, w, h, dx, dy, scale_delta, id):
    if scale_delta:
      dx = round(dx * self.scale)
      dy = round(dy * self.scale)
    x, y = self.elements[target_id].get_bottom()
    self.elements[id] = LayoutRect(x + dx, y + dy, w, h)

  def create_placeholder_rightof(self, target_id, w, h, dx, dy, scale_delta, id):
    if scale_delta:
      dx = round(dx * self.scale)
      dy = round(dy * self.scale)
    x, y = self.elements[target_id].get_right()
    self.elements[id] = LayoutRect(x + dx, y + dy, w, h)

  """
  Draw an image on the screen to the right of a given element.

  image_id:  the id of the image to draw
  target_id: the id of the element to which you want to be on the left of
  dx:        an optional x offset (0 be default)
  dy:        an optional y offset (0 by default)
  id:        a unique id for this element
  """
  def draw_image_leftof(self, image_id, target_id, dx, dy, scale_delta, id):
    if scale_delta:
      dx = round(dx * self.scale)
      dy = round(dy * self.scale)
    x, y = self.elements[target_id].get_pos()
    w, _ = self.images[image_id].get_rect().size
    self.draw_image_abs(image_id, x - w + dx, y + dy, id)
  
  def draw_images_in_grid(self, nb_cols, image_ids, x, y, grid_id, spacing):
    i = 0
    self.draw_image_abs(image_ids[i], x, y, grid_id + str(i))
    wi, hi = self.get_image_size_from_id(image_ids[i])
    w_row = wi + spacing
    i += 1
    w = 0
    h = hi + spacing
    while i < len(image_ids):
      if i % nb_cols != 0:
        wi, hi = self.get_image_size_from_id(image_ids[i])
        w_row += wi + spacing
        self.draw_image_rightof(image_ids[i], grid_id + str(i - 1), spacing, 0, True, grid_id + str(i))
      else:
        w = max(w_row, w)
        self.draw_image_below(image_ids[i],grid_id + str(i - nb_cols), 0, spacing, True, grid_id + str(i))
        wi, hi = self.get_image_size_from_id(image_ids[i])
        h += hi + spacing
        w_row = wi + spacing
      i += 1
    self.elements[grid_id] = LayoutRect(x, y, w, h)

  def draw_images_in_grid_below(self, nb_cols, image_ids, target_id, dx, dy, scale_delta, grid_id, spacing):
    if scale_delta:
      dx = round(dx * self.scale)
      dy = round(dy * self.scale)
    x, y = self.elements[target_id].get_bottom()
    self.draw_images_in_grid(nb_cols, image_ids, x + dx, y + dy, grid_id, spacing)

  """
  Draw text at an absolute position.

  text_height: the height we want the text to have
  hegiht:  the size of the text
  color: the color of the text
  x:     the x position (top left corner)
  y:     the y position (top left corner)
  """
  def draw_text_abs(self, text, fontname, text_height, color, x, y, id):
    size = self.find_font_size(fontname, text, text_height)
    font = pygame.font.SysFont(fontname, size)
    label = font.render(text, 1, color)
    w, h = font.size(text)
    self.screen.blit(label, (x, y))
    if id == None:
      self.elements[text] = LayoutRect(x, y, w, h)
    else:
      self.elements[id] = LayoutRect(x, y, w, h)
  
  """
  Draw text on the screen to the right of a given element.

  text:        the text to draw
  text_height: the height we want the text to have
  color: the   color of the text
  target_id:   the id of the element to which you want to be on the right of
  dx:          an optional x offset (0 be default)
  dy:          an optional y offset (0 by default)
  id:          a unique id for this element
  """
  def draw_text_rightof(self, text, fontname, text_height, color, target_id, dx, dy, scale_delta, id):
    if scale_delta:
      dx = round(dx * self.scale)
      dy = round(dy * self.scale)
    x, y = self.elements[target_id].get_right()
    self.draw_text_abs(text, fontname, text_height, color, x + dx, y + dy, id)


  """
  Draw text on the screen on the bottom of a given element.

  text:        the text to draw
  text_height: the height we want the text to have
  color: the   color of the text
  target_id:   the id of the element to which you want to be on the bottom of
  dx:          an optional x offset (0 be default)
  dy:          an optional y offset (0 by default)
  id:          a unique id for this element
  """
  def draw_text_below(self, text, fontname, text_height, color, target_id, dx, dy, scale_delta, id):
    if scale_delta:
      dx = round(dx * self.scale)
      dy = round(dy * self.scale)
    x, y = self.elements[target_id].get_bottom()
    self.draw_text_abs(text, fontname, text_height, color, x + dx, y + dy, id)

  """
  Draw a button on the screen to the right of a given element.

  image_id:  the id of the image to draw
  target_id: the id of the element to which you want to be on the right of
  dx:        an optional x offset (0 be default)
  dy:        an optional y offset (0 by default)
  id:        a unique id for this element
  """
  def draw_button_rightof(self, button, target_id, dx, dy, scale_delta, id):
    if scale_delta:
      dx = round(dx * self.scale)
      dy = round(dy * self.scale)
    x, y = self.elements[target_id].get_right()
    self.draw_image_abs(button.get_image_id(), x + dx, y + dy, id)
    button.set_pos(x, y)
  
  """
  Draw a button on the screen on the bottom of a given element.

  image_id:  the id of the image to draw
  target_id: the id of the element to which you want to be on the bottom of
  dx:        an optional x offset (0 be default)
  dy:        an optional y offset (0 by default)
  id:        a unique id for this element
  """
  def draw_button_below(self, button, target_id, dx, dy, scale_delta, id):
    if scale_delta:
      dx = round(dx * self.scale)
      dy = round(dy * self.scale)
    x, y = self.elements[target_id].get_bottom()
    self.draw_image_abs(button.get_image_id(), x + dx, y + dy, id)
    button.set_pos(x, y)


  """
  Draws the screen contents.
  """
  def draw(self):
    self.elements = { }
    self.screen.fill(color.BLACK)
    self.draw_screen()
    pygame.display.flip()

  """
  Draw the screen content. You need to implement this method.
  """
  def draw_screen(self):
    pass

  """
  Handle human player. You need to implements this method.
  """
  def handle_human(self):
    pass

  """
  Handle ai player.
  """
  def handle_ai(self):
    if not self.ai_thinking:
      # the ai is not yet thinking
      # start a thread to get an action
      self.action = get_action_threaded(self.state.copy(), self.last_action, self.agents[self.state.cur_player], self.time_left[self.state.cur_player])
      self.start = time.time()
      self.ai_thinking = True
      return
    elif len(self.action) != 0:
      # reset data
      self.ai_thinking = False
      self.start = 0
      self.end = 0
      # get the action
      action = self.action[0]
      self.action = [ ]
      if not self.state.is_action_valid(action):
        self.state.set_invalid_action(self.state.cur_player)
      self.handle_ai_action(action)
      self.draw()
      time.sleep(self.wait)
  
  def handle_ai_action(self, action):
    pass


  def run_timer(self):
    if not self.state.game_over():
      threading.Timer(0.1, self.run_timer).start()
      self.time_left[self.state.cur_player] -= 0.1
      if self.time_left[self.state.cur_player] <= 0:
        self.state.set_timed_out(self.state.cur_player)

  """
  Run the game in a window of dimensions width x height.
  """
  def run(self):
    # make the window open in the center
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    self.screen_w, self.screen_h = self.get_screen_resolution()
    # initialize the pygame screen
    self.screen = pygame.display.set_mode((0, 0))
    self.adjust_window_size()
    self.ai_thinking = False
    self.last_action = None
    self.run_timer()
    # game loop
    while not self.state.game_over():
      w, h = self.width, self.height
      self.draw()
      if w != self.width or h != self.height:
        self.adjust_window_size()
      if self.player_type[self.state.get_cur_player()] == 'human':
        self.handle_human()
      else:
        self.handle_ai()      
    # game is over, draw screen and show results
    self.adjust_window_size()  
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          break
      time.sleep(4)

  def adjust_window_size(self):
    print('adjusting window size for resolution {0}x{1}'.format(self.screen_w, self.screen_h))
    s = 1
    self.set_scale(s)
    while self.width > self.screen_w or self.height > self.screen_h:
      s -= 0.1
      self.set_scale(s)
    print('window running at scale {0}% ({1}x{2})'.format(round(100 * s), self.width, self.height))
    
  def get_screen_resolution(self):
    info = pygame.display.Info()
    return info.current_w, info.current_h
  
  def set_scale(self, scale):
    self.scale = scale
    self.width = 0
    self.height = 0
    for k in self.images:
      self.images[k] = scale_image(self.images[k], scale)
    for sc in self.scalable:
      sc.change_scale(scale)
    self.draw()
    for k in self.elements:
        self.width = max(self.width, self.elements[k].get_right()[0])
        self.height = max(self.height, self.elements[k].get_bottom()[1])
    self.screen = pygame.display.set_mode((self.width, self.height))    
    self.draw()
  
  def draw_layout_elements(self):
    for k in self.elements:
      elem = self.elements[k]
      self.draw_rect(elem.x, elem.y, elem.x + elem.w, elem.y + elem.h, color.LIME, 1)
  
  def draw_rect(self, x1, y1, x2, y2, color, line_width):
    pygame.draw.line(self.screen, color, (x1, y1), (x2, y1), line_width)
    pygame.draw.line(self.screen, color, (x1, y1), (x1, y2), line_width)
    pygame.draw.line(self.screen, color, (x2, y2), (x2, y1), line_width)
    pygame.draw.line(self.screen, color, (x2, y2), (x1, y2), line_width)

  def draw_amount_with_image(self, x, y, amount, image, fontname, color):
    image_width, image_height = self.get_image_size(image)
    self.draw_image(image, x, y)
    text = 'x' + str(amount)
    # get the size of the font to match the image height
    font_size = self.find_font_size(fontname, text, image_height)
    font = pygame.font.SysFont(fontname, font_size)
    label = font.render(text, 1, color)
    text_width, text_height = font.size(text)
    self.screen.blit(label, (x + image_width, y))
    
  def draw_grid(self, x, y, nb_rows, nb_cols, width, height, line_width, color):
    xx = x + width * nb_cols
    yy = y + height * nb_rows
    # draw the border
    pygame.draw.line(self.screen, color, (x, y), (xx, y), line_width)
    pygame.draw.line(self.screen, color, (x, y), (x, yy), line_width)
    pygame.draw.line(self.screen, color, (xx, yy), (xx, y), line_width)
    pygame.draw.line(self.screen, color, (xx, yy), (x, yy), line_width)
    # draw vertical lines
    for i in range(1, nb_cols):
      xcur = x + i * width
      pygame.draw.line(self.screen, color, (xcur, y), (xcur, yy), line_width)
    # draw horizontal lines
    for i in range(1, nb_rows):
      ycur = y + i * height
      pygame.draw.line(self.screen, color, (x, ycur), (xx, ycur), line_width)

  def draw_grid2(self, grid, color):
    self.draw_grid(grid.x, grid.y, grid.nb_rows, grid.nb_cols, grid.width, grid.height, 1, color)

  def draw_triangle(self, x1, y1, x2, y2, x3, y3, color):
    pygame.draw.polygon(self.screen, color, ((x1, y1), (x2, y2), (x3, y3)))

  def draw_bordered_triangle(self, x1, y1, x2, y2, x3, y3, color, line_width, border_color):
    pygame.draw.polygon(self.screen, color, ((x1, y1), (x2, y2), (x3, y3)))
    pygame.draw.line(self.screen, border_color, (x1, y1), (x2, y2), line_width)
    pygame.draw.line(self.screen, border_color, (x2, y2), (x3, y3), line_width)
    pygame.draw.line(self.screen, border_color, (x3, y3), (x1, y1), line_width)

  def draw_line(self, x1, y1, x2, y2, color, line_width = 1):
    pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), line_width)
    
  def draw_image(self, image, x, y):
    self.screen.blit(image, (x, y))

  def get_image_width(self, image):
    return image.get_rect().size[0]

  def get_image_height(self, image):
    return image.get_rect().size[1]

  def get_image_size(self, image):
    return image.get_rect().size

  def find_font_size(self, fontname, text, height):
    lb = 1
    ub = 100
    while ub - lb > 1:
      mid = (lb + ub) // 2
      font = pygame.font.SysFont(fontname, mid)
      label = font.render(text, 1, (255, 255, 255))
      text_width, text_height = font.size(text)
      if text_height > height:
        ub = mid - 1
      else:
        lb = mid
    return lb

  def draw_text(self, x, y, fontname, height, text, color):
    font_size = self.find_font_size(fontname, text, height)
    font = pygame.font.SysFont(fontname, font_size)
    label = font.render(text, 1, color)
    self.screen.blit(label, (x, y))
  
  def draw_button(self, button, x, y):
    button.set_pos(x, y)
    self.draw_image(button.get_image(), x, y)

from interface import *

class LayoutManager():

  def __init__(self, gui):
    self.gui = gui
    self.elements = { }
  
  def set_scale(self, scale):
    self.margin *= scale
  
  def register(self, identifier, rectangle):
    self.elements[identifier] = rectangle

  def register_image(self, identifier, image, x, y):
    w, h = image.get_rect().size
    self.elements[identifier] = Rect(x, y, x + w, y + h)
    self.gui.draw_image(image, x, y)

  def register_image_right(self, identifier, image, target, margin = 0, dx = 0, dy = 0):
    x, y = self.right_pos(target, margin)
    self.register_image(identifier, image, x + dx, y + dy)
  
  def register_image_bottom(self, identifier, image, target, margin = 0, dx = 0, dy = 0):
    x, y = self.bottom_pos(target, margin)
    self.register_image(identifier, image, x + dx, y + dy)
  
  def get_elements(self):
    return self.elements

  def x_start(self, identifier):
    return self.elements[identifier].x1
  
  def x_end(self, identifier):
    return self.elements[identifier].x2
  
  def y_start(self, identifier):
    return self.elements[identifier].y1

  def y_end(self, identifier):
    return self.elements[identifier].y2
  
  def right_x(self, identifier, margin = 0):
    return self.x_end(identifier) + margin

  def right_pos(self, identifier, margin = 0):
    return self.x_end(identifier) + margin, self.y_start(identifier)
    
  def bottom_y(self, identifier, margin = 0):
    return self.y_end(identifier) + margin

  def bottom_pos(self, identifier, margin = 0):
    return self.x_start(identifier), self.y_end(identifier) + margin
import math

class Scalable():

  def change_scale(self, scale):
    pass

class Grid(Scalable):

  def __init__(self, nb_rows, nb_cols, width, height, x, y):
    self.nb_rows = nb_rows
    self.nb_cols = nb_cols
    self.width = width
    self.height = height
    self.x = x
    self.y = y

  def get_rect(self, r, c):
    x1 = self.x + c * self.width
    y1 = self.y + r * self.height
    x2 = x1 + self.width
    y2 = y1 + self.height
    return Rect(x1, y1, x2, y2)

  def change_scale(self, scale):
    self.width = round(self.width * scale)
    self.height = round(self.height * scale)
    self.x = round(self.x * scale)
    self.y = round(self.y * scale)

  def get_center_xdraw(self, r, c, image):
    return self.get_rect(r, c).get_center_xdraw(image)

  def get_center_ydraw(self, r, c, image):
    return self.get_rect(r, c).get_center_ydraw(image)  

  def get_bottom_ydraw(self, r, c, image):
    return self.get_rect(r, c).y2 - image.get_rect().size[1]

  def in_bounds(self, x, y):
    return self.x <= x and x <= self.x + self.nb_cols * self.width and self.y <= y and y <= self.y + self.nb_rows * self.height

  def get_row_col(self, x, y):
    assert self.in_bounds(x, y)
    return (y - self.y) // self.height, (x - self.x) // self.width

  def get_rect_from_coord(self, x, y):
    r, c = self.get_row_col(x, y)
    return self.get_rect(r, c)
  
  def are_adjacent(self, r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2) == 1

  def is_border(self, r, c):
    return r == 0 or r == self.nb_rows - 1 or c == 0 or c == self.nb_cols - 1

class Rect(Scalable):

  def __init__(self, x1, y1, x2, y2):
    self.x1 = x1
    self.y1 = y1
    self.x2 = x2
    self.y2 = y2
  
  def change_scale(self, scale):
    self.x1 = round(self.x1 * scale)
    self.y1 = round(self.y1 * scale)
    self.x2 = round(self.x2 * scale)
    self.y2 = round(self.y2 * scale)

  def get_center(self):
    return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

  def get_center_xdraw(self, image):
    return self.x1 + (self.get_width() - image.get_rect().size[0]) // 2
  
  def get_center_ydraw(self, image):
    return self.y1 + (self.get_height() - image.get_rect().size[1]) // 2

  def get_bottom_ydraw(self, image):
    return self.y2 - image.get_rect().size[1]

  def get_width(self):
    return self.x2 - self.x1

  def get_height(self):
    return self.y2 - self.y1

  def contains(self, x, y):
    return self.x1 <= x and x <= self.x2 and self.y1 <= y and y <= self.y2

  def __str__(self):
    return '({0},{1}) ({2},{3})'.format(self.x1, self.y1, self.x2, self.y2)
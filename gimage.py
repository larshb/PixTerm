#!/usr/bin/env python3.8

import logging
from copy import deepcopy
from curses import init_pair, color_pair

log = logging.getLogger()

def rgb2ansi(rgb):
  r, g, b = rgb
  return r | g << 1 | b << 2


class Glyph():

  background = 0b000

  def __init__(self):
    self.top = self.background
    self.bottom = self.background

  def __str__(self):
    return f"\033[3{self.bottom};4{self.top}m▄"

  def __getitem__(self, key):
    return self.bottom if key else self.top

  def __setitem__(self, key, value):
    if key:
      self.bottom = value
    else:
      self.top = value
    if value == None:
      raise ValueError("Do you really want to remove attribute?")
    return value

  def raw(self):
    return self.top, self.bottom


class gImage():

  def __init__(self, width, height, background=None):

    self.width, self.height = width, height
  
    self.y0, self.x0 = 0, 0
    self.rows = height // 2
    self.columns = width
    self.data = [[Glyph() for _ in range(self.columns)]
                  for _ in range(self.rows)]
    if background:
      for r in range(self.rows):
        for c in range(self.columns):
          self.data[r][c].top = background
          self.data[r][c].bottom = background

  def __getitem__(self, key):
    return self.data[key]

  def __setitem__(self, key, value):
    self.data[key] = value
    return value

  def __str__(self):
    return '\033[0m\n'.join(
        [''.join(
            [str(self[r][c]) for c in range(self.columns)]
        ) for r in range(self.rows)]
    ) + "\033[0m"


  def __add__(self, o):
    o = deepcopy(o)
    self.columns += o.columns
    for r, row in enumerate(o.data):
      for glyph in row:
        self.data[r].append(deepcopy(glyph))
    return self


  def get(self, y, x):
    return self.data[y // 2][x][y % 2]

  
  def set(self, y, x, color):
    self.data[y // 2][x][y % 2] = color


  def resize(self, width, height):

    #log.debug(f"Resizing: {(self.width, self.height)} -> {(width, height)}")
    
    rows = height // 2 + int(height // 2 != height / 2)
    columns = width

    # Fix columns
    if columns < self.columns:
      for r in range(len(self.data)):
        self.data[r] = self.data[r][:columns]
    elif columns > self.columns:
      for r in range(len(self.data)):
        for _ in range(columns - self.columns):
          self.data[r].append(Glyph())

    # Fix rows
    if rows < self.rows:
      self.data = self.data[:rows]
    elif rows > self.rows:
      for _ in range(rows - self.rows):
        self.data.append([Glyph() for _ in range(columns)])

    self.rows, self.columns = rows, columns
    self.height, self.width = height, width

  def pasteImage(self, y0, x0, image, flush=False):

    w, h = image.size
    px = image.load()

    rows, columns = h // 2, w
    x1, y1 = x0 + columns, (y0 // 2) + rows + int(h // 2 != h / 2)

    if self.rows < y1 or self.columns < x1:
      #log.warning(f"gImage too small")
      nw = max(x1, self.columns)
      nh = max(y1, self.rows)
      self.resize(nw, nh*2)

    for x in range(w):
      for y in range(h):
        R, G, B = px[x, y]
        self.paint_pixel(y0 + y, x0 + x,
                         rgb2ansi((p // 128 for p in [R, G, B])), flush=flush)
        # self.data[(y+y0)//2][(x+x0)][(y+y0) % 2] = \
        #     rgb2ansi((p // 128 for p in [R, G, B]))

    return self

  def paint(self, y, x):
    y -= y % 2
    for r, row in enumerate(self.data):
      print(f"\x1b[{self.y0 // 2 + y // 2 + r + 1};{self.x0 + x + 1}H"
        + ''.join(str(g) for g in row), end="", flush=True)

  def paint_pixel(self, y, x, ansi_color, flush=True):
    # Assuming painted at 1x1
    try:
      self.data[y // 2][x][y % 2] = ansi_color
    except IndexError:
      log.error(f"Failed to set x={x}, y={y}")
    if flush:
      print(f"\033[{self.y0 // 2 + y // 2 + 1};{self.x0 + x + 1}H"
        + str(self.data[y // 2][x]), end="", flush=True)

  def place(self, y, x, flush=True):
    y -= y % 2
    self.y0, self.x0 = y, x
    if flush:
      self.paint(0, 0)

  def draw(self, string, y=0, x=0, flush=True,
           colormap={"_": 0b000, "X": 0b111}):
    string = string.replace(' ', '').strip()
    lines = string.splitlines()
    h, w = len(lines), len(lines[0])  # Naively assume square
    self.resize(max(w, self.width), max(h, self.height))
    for r, row in enumerate(lines):
      for c, ch in enumerate(row):
        self.paint_pixel(y+r, x+c, colormap.get(ch), flush=flush)


# --- 3x6 numbers ---
__NUMBSTR = '''
... ... ... ... ... ... ... ... ... ... 
xxx .x. xxx xxx x.x xxx xxx xxx xxx xxx 
x.x xx. ..x ..x x.x x.. x.. ..x x.x x.x 
x.x .x. xxx xxx xxx xxx xxx .x. xxx xxx 
x.x .x. x.. ..x ..x ..x x.x .x. x.x ..x 
xxx xxx xxx xxx ..x xxx xxx .x. xxx xxx .
'''.strip().split('\n')

background = 0b000
ansi_dict = {
    " ": background,
    "x": 0b010,
    ".": background
}

__GNUMBERS = [gImage(4, 6, background=background) for _ in range(10)]
for n, x0 in enumerate(range(0, len(__NUMBSTR[0]), 4)):
  for dr in range(3):
    for dc in range(4):
      for sr in range(2):
        __GNUMBERS[n][dr][dc][sr] = ansi_dict[__NUMBSTR[dr*2+sr][dc+n*4]]


def gnumber(i):
  return deepcopy(__GNUMBERS[i])


def int2gim(integer):
  return __import__("functools").reduce(
      gImage.__add__,
      [gnumber(int(digit)) for digit in str(integer)])
# --- * ---

if __name__ == "__main__":

  gim = gImage(32, 32)
  gim.draw('''
    _X___XXX_X__
    _X___X_X_X__
    _XXX_XXX_XXX
  ''')

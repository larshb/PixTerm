from PIL import Image
from gimage import gImage, int2gim
from random import randint
from time import time
from os.path import abspath, dirname
from pathlib import Path

HERE = Path(abspath(dirname(__file__)))

def snake():  # Snake

  class Pixel:
    BLANK = 0b000
    BORDER = 0b001
    FOOD = 0b010
    SNAKE = 0b011

  w, h = 32, 32
  playArea = gImage(w, h-8)

  # Border
  for x in [0, playArea.width-1]:
    for y in range(playArea.height):
      playArea.paint_pixel(y, x, Pixel.BORDER)
  for y in [0, playArea.height-1]:
    for x in range(playArea.width):
      playArea.paint_pixel(y, x, Pixel.BORDER)

  class Dir:
    N = U = A = (-1,  0)
    S = D = B = (1,  0)
    E = R = C = (0,  1)
    W = L = D = (0, -1)
    lookup = {
        "A": (-1,  0),
        "B": (1,  0),
        "C": (0,  1),
        "D": (0, -1)
    }

  class Snake:

    class Node:

      def __init__(self, y, x, back=None):
        self.y, self.x, self.back = y, x, back
        playArea.paint_pixel(y, x, Pixel.SNAKE)
        #debug(f"Node @ {x, y}")

      def die(self):
        playArea.paint_pixel(self.y, self.x, 0)
        node = self.forward
        del node.back
        node.back = None
        return node

      def grow(self, y, x):
        p = playArea.get(y, x)
        if p in [Pixel.BORDER, Pixel.SNAKE]:
          return None
        self.forward = Snake.Node(y, x, back=self)
        return self.forward

    def __init__(self, start_length=5, tick_rate=1/10):
      self.score = 0
      self.crashed = False
      self.dir = Dir.E
      dy, dx = self.dir
      self.tick_rate = tick_rate
      y, x = playArea.height // 2, 1
      self.head = self.rear = self.Node(y, x)
      for _ in range(start_length-1):
        y, x = y + dy, x + dx
        self.head = self.head.grow(y, x)

    def turn(self, dy, dx):
      n = self.head
      y, x = n.y + dy, n.x + dx
      if n.back and (y != n.back.y or x != n.back.x):
        self.dir = dy, dx

    def move(self):

      dy, dx = self.dir
      y, x = self.head.y + dy, self.head.x + dx

      # Eat?
      ate = playArea.get(y, x) == Pixel.FOOD

      # Grow?
      self.head = self.head.grow(y, x)
      if not self.head:  # Crashed
        return False

      # Shrink?
      if ate:
        self.score += 1
        int2gim(self.score).paint(h - 8, 2)
      else:
        self.rear = self.rear.die()

      return True

    def spawn_food(self):  # FIXME
      valid = False
      while not valid:
        y, x = randint(1, playArea.height -
                        2), randint(1, playArea.width - 2)
        valid = playArea.get(y, x) == Pixel.BLANK
      playArea.paint_pixel(y, x, Pixel.FOOD)

    def play(self):

      CHEAT = True

      try:
        import keylogger
        kbd = keylogger.KeyLogger()
        kbd.start()
        run = True
        self.__last_tick = time()
        dy, dx = self.dir

        def ticking():
          now = time()
          if now - self.__last_tick < self.tick_rate:
            return True
          else:
            self.__last_tick = now
            return False

        while run:
          while ticking():
            key = kbd.get()
            if key:
              if key == 'q':
                  run = False
                  kbd.stop()
              elif key in "ABCD":  # UDRL
                dy, dx = Dir.lookup[key]
              elif CHEAT:
                if key == ' ':
                  self.spawn_food()

          self.turn(dy, dx)
          run = run and self.move()

      finally:
        gameover_sprite = Image.open(HERE / "gameover.bmp")
        gow, goh = gameover_sprite.size
        y0, x0 = playArea.rows - goh//2 - 1, playArea.columns // 2 - gow // 2 - 1
        #debug(f"Placing gameover relatively {x0, y0}")
        #debug(f"{playArea.rows, playArea.columns, goh, gow}") # 16 32 17 19
        playArea.pasteImage(y0, x0, gameover_sprite, flush=True)
        #debug("Stopping keyboard")
        kbd.stop()
        #debug("Keyboard stopped")

  snk = Snake()
  snk.play()

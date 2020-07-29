#!/usr/bin/env python3.8

# Native modules
import logging
import threading
from curses import wrapper
from time import sleep, time
from signal import signal, SIGINT
from pathlib import Path
from os.path import abspath, dirname

# PyPi modules
from PIL import Image, ImageOps
from rich.logging import RichHandler

# Local modules
from gimage import gImage, int2gim
from ansi import screen_wrapper

logging.basicConfig(
  level="NOTSET",
  format="%(message)s",
  datefmt="[%X]",
  handlers=[RichHandler()])
log = logging.getLogger("rich")

def signal_handler(sig, frame):
  print("You pressed CTRL+C")
  #exit(0)
signal(SIGINT, signal_handler)

HERE = Path(abspath(dirname(__file__)))

from fcntl import ioctl
from struct import unpack
from termios import TIOCGWINSZ
def terminal_size():  # (h, w)
  return unpack('HH', ioctl(0, TIOCGWINSZ, "0000"))

log.info(f"Terminal size: {terminal_size()}")

def main():

  h, w = terminal_size()
  h *= 2  # Using gImage Glyphs

  background = gImage(w, h, background=0b000)
  for y in range(h):
    for x in [0, w-1]:
      background.paint_pixel(y, x, 0b101)
  for x in range(w):
    for y in [0, h-1]:
      background.paint_pixel(y, x, 0b101)

  gim = gImage(0, 0).pasteImage(0, 0, Image.open(HERE / "mario.bmp"))
  gim.paint(h-gim.height-1, 1)

  #gImage(0, 0).pasteImage(0, 0, Image.open(HERE / "lars.bmp")).paint(2, 2)
  gImage(0, 0).pasteImage(0, 0, Image.open(HERE / "penrose.bmp")).paint(2, 2)
  #input("")
  from snake import snake
  snake()

screen_wrapper(main)

ESC = "\x1b"
ESCA = ESC + "["
ALT_BUF = "?1049"
HIGH = "h"
TERM_CLEAR = "2J"
CURS = "?25"
LOW = "l"

ANSI_CODES = {
  "with": ";",
  "plain": "0",
  "no": "2",
  "bright": "1",
  "dim": "2",
  "italic": "3",
  "underline": "4",
  "reverse": "7",
  "fg": "3",
  "bg": "4",
  "br_fg": "9",
  "br_bg": "10",
  "black": "0",
  "red": "1",
  "green": "2",
  "yellow": "3",
  "blue": "4",
  "magenta": "5",
  "cyan": "6",
  "white": "7",
  "altbuf": "?1049",
  "cursor": "?25",
  "clear": "2",
  "terminal": "J",
  "line": "K",
  "high": "h",
  "low": "l",
  "on": "h",
  "off": "l",
  "jump": "H"
}

def ansi(string):
  return ESCA + "".join(ANSI_CODES.get(x, x) for x in string.split(' '))

def say(*strings):
  for string in strings:
    print(ansi(string), end="", flush=True)

def write(y, x, string):
  print(ansi(f"{y} with {x} jump") + string, end="", flush=True)

def screen(on):
  if on:
    say("altbuf on", "clear terminal", "cursor off")
  else:
    say("altbuf on", "clear terminal", "cursor on", "altbuf off")

def screen_wrapper(func):
  screen(True)
  try:
    func()
  finally:
    screen(False)

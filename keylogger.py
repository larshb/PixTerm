#!/usr/bin/env python3.8

from queue import Queue
from threading import Thread
from tty import setcbreak
from sys import stdin
from termios import tcgetattr, tcsetattr, TCSADRAIN
from logging import getLogger


log = getLogger()


class KeyLogger:

    def __init__(self, maxsize=0):
        self.queue = Queue(maxsize=maxsize)
        self.kill = False

    def __stdin_highjack(self):
        self.__stdin_opts = tcgetattr(stdin)
        setcbreak(stdin)

    def __stdin_restore(self):
        log.debug("Restoring stdin attributes")
        tcsetattr(stdin, TCSADRAIN, self.__stdin_opts)

    def __capture_thread(self):
        try:
            self.__stdin_highjack()
            key = 0
            while not self.kill:
                key = stdin.read(1)[0]
                self.queue.put_nowait(key)
                #self.queue.task_done()
        finally:
            self.__stdin_restore()

    def start(self):
        self.capture_thread = Thread(target=self.__capture_thread, daemon=True)
        self.capture_thread.start()

    def stop(self):
        self.kill = True
        #log.debug("Waiting for keylogger thread")
        self.capture_thread.join()
        #log.debug("Thread ended")

    def get(self):
        return None if self.queue.empty() else self.queue.get()

    def flush(self):
        key = None
        while not self.queue.empty():
            key = self.queue.get()
        return key

if __name__ == "__main__":

    kbd = KeyLogger()
    kbd.start()
    run = True
    last_key = None
    print("Press Q to quit!")

    while run:
        key = kbd.flush()
        if key:
            if key == 'q':
                run = False
                kbd.stop()
            elif key == chr(27):
                print("Escape detected!")
            elif key == '\n':
                print("You pressed Return!")
            else:
                print("-> " + key)

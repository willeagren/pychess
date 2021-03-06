"""
PychessGUI

Author: Wilhelm Ågren, wagren@kth.se
Last edited: 12-10-2021
"""
from .mode      import PychessMode
from .game      import PychessGame
from .utils     import *


class PychessGUI(PychessMode):
    def __init__(self, players, names, verbose=False, **kwargs):
        super().__init__(players, names, verbose=verbose, mode='PychessGUI')


    def start(self):
        print("[*]  starting pychess instance with mode {}".format(self.mode))

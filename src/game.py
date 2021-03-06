"""
PychessGame class and unittest implementation for main module Pychess.
Initialized from either PychessTUI (terminal User Interace)
or from the PychessGUI (Graphical User Interface). 
Run this program as main to perform unittest of local functions.

Author: Wilhelm Ågren, wagren@kth.se
Last edited: 12-10-2021
"""
import time
import math
import chess
import unittest

try:
    from .utils import *
except ImportError:
    print("[!]  PychessGame  ImportError caught, ignoring relative import")
    from  utils import *



class PychessGame:
    """!!! definition for class  PychessGame
    used as a main game object in both 'pychess_gui' and 'pychess_cli'
    the object is used as a wrapper of the chess board state and also
    implements necessary helper functions for running the game.
    game information is stored in self._info dictionary and is 
    initialized with **kwargs or DEFAULT values. the time for
    both players are also managed there. this information dictionary 
    may see more key-value pair being added to it as deemed necessary.

    public  funcs:
        $  PychessGame.start_clock              =>  none
        $  PychessGame.get_info                 =>  arbitrary
        $  PychessGame.get_state                =>  chess.Board
        $  PychessGame.get_prev_move            =>  chess.Move
        $  PychsesGame.make_move                =>  bool
        $  PychessGame.is_terminal              =>  bool

    private funcs:
        $  PychessGame._wprint                  =>  none
        $  PychessGame._eprint                  =>  none
        $  PychessGame._init_info               =>  dict
        $  PychessGame._update_info             =>  none
        $  PychessGame._set_info                =>  bool
        $  PychessGame._create_time_format      =>  str
        $  PychessGame._legal_moves             =>  list
        $  PychessGame._push_move               =>  bool

    dunder  funcs:
        $  PychessGame.__init__                 =>  PychessGame
        $  PychessGame.__str__                  =>  str

    """
    def __init__(self, players, board=None, verbose=False, stdout=None, **kwargs):
        self._state     = chess.Board() if board is None else board
        self._verbose   = verbose
        self._players   = players
        self._ai        = None if players == 2 else None
        self._stdout    = stdout
        self._info      = self._init_info(kwargs)


    def __str__(self):
        return "PychessGame"  

    
    def _wprint(self, msg):
        WPRINT(msg, str(self), self._verbose) if self._stdout is None else self._stdout.WPUT(msg, str(self), self._verbose)


    def _eprint(self, msg):
        EPRINT(msg, str(self), self._verbose) if self._stdout is None else self._stdout.EPUT(msg, str(self))


    def _init_info(self, kwargs):
        """ private func
        @spec  _init_info(PychessGame, dict)  =>  dict
        func initializes a local dictionary of important
        game information. this dictionary contains just about
        everything related to the initialized game state.
        this function is called whenever a new PychessGame object
        is being created in __init__, and the dictionary is 
        returned to become a local object attribute.
        """
        self._wprint("initializing information dictionary ...")
        infodict = dict()
        infodict['ai']              = self._ai
        infodict['FEN']             = self._state.fen()
        infodict['turn']            = self._state.turn
        infodict['white']           = kwargs.get('white', DEFAULT_WHITE)
        infodict['black']           = kwargs.get('black', DEFAULT_BLACK)
        infodict['players']         = self._players
        infodict['time-prev-move']  = time.time()
        infodict['time-start']      = kwargs.get('time', DEFAULT_TIME)
        infodict['time-increment']  = kwargs.get('increment', DEFAULT_INCREMENT)
        infodict['time-white']      = infodict['time-start']
        infodict['time-black']      = infodict['time-start']
        infodict['time-format']     = self._create_time_format(infodict['time-start'], infodict['time-increment'])
        infodict['state-history']   = [self._state]
        infodict['move-history']    = list()
        self._wprint("intialization done")
        return infodict


    def _update_info(self, move):
        """ private func
        @spec  _update_info(PychessGame, chess.Move)  =>  none
        func takes the just pushed move and updates all information
        of the new current state. only called from private func
        _push_move after a legal move has been made by a user.
        updates the FEN string, turn, white-time, black-time,
        state-history, move-history of the local attribute
        information dictionary.
        """
        self._wprint("updating information dictionary ...")
        self._info['FEN']           = self._state.fen()
        self._info['turn']          = self._state.turn
        self._info['time-white']    = math.ceil(self._info['time-start'] - (time.time() - self._info['time-prev-move']) + self._info['time-increment'] if not self._info['turn'] else self._info['time-white'])
        self._info['time-black']    = math.ceil(self._info['time-start'] - (time.time() - self._info['time-prev-move']) + self._info['time-increment'] if self._info['turn'] else self._info['time-black'])
        self._info['state-history'].append(self._state)
        self._info['move-history'].append(move)
        self._wprint("updating done")


    def _set_info(self, key, val):
        """ private func
        @spec  _set_info(PychessGame, str, arbitrary)  =>  bool
        func sets the value to the given key in the local attribute
        information dictionary. checks whether or not the key is actually
        a valid key for the dictionary. the function returns true if the 
        setting operation was legal/successfull, false if not.
        """
        self._wprint("setting information ...")
        if key not in self._info.keys():
            self._eprint("could not set information, invalid key")
            return False

        self._info[key] = val
        self._wprint("setting information done")
        return True


    def _create_time_format(self, t_total, t_incr):
        """ private func
        @spec  _create_time_format(PychessGame)  =>  str
        func takes the current time format in seconds and creates
        an easy to read string of time format. called when 
        initializing information dictionary on  __init__
        """
        self._wprint("creating time format for info initialization")
        t_min, t_sec = divmod(t_total, 60)
        t_format = "{}:{} +{}".format(t_min, t_sec, t_incr)
        return t_format


    def _legal_moves(self):
        """ private func
        @spec  _legal_moves(PychessGame)  =>  list
        func simply generates a list of legal chess.Move objects
        for the current board state. no pseudo-legal moves allowed!
        """
        self._wprint("generating legal moves")
        return list(self._state.legal_moves)


    def _push_move(self, move):
        """ private func
        @spec  _push_move(PychessGame, chess.Move)  =>  bool
        func takes a chess.Move object from user input, checks if the 
        move is legal, and if it is, it pushes it to the current state
        move stack and call _update_info to make sure new times are
        calculated and new player turn is set etc.
        """
        if move in self._legal_moves():
            self._wprint("pushing move {}".format(move.uci()))
            self._state.push(move)
            self._update_info(move)
            self._wprint("pushing and updating done")
            return True

        self._eprint("got illegal move from user")
        return False


    def start_clock(self):
        """ public func
        @spec  start_clock(PychessGame)  =>  none
        func overwrites the initial 'time-prev-move' time in the 
        info dictionary to the current time. this is done to 
        start the time counting from after the first move is made.
        """
        self._wprint("starting clock")
        self._info['time-prev-move'] = time.time()


    def get_info(self, key):
        """ public func
        @spec  get_info(PychessGame, str)  =>  arbitrary
        func looks up the given key argument and returns whatever
        is found, assumes the user knows what it does, which is 
        extremely foolish. TODO: implement input checking  and/or
        default value for returning.
        """
        self._wprint("getting information")
        return self._info[key]


    def get_state(self):
        """ public func
        @spec  get_state(PychessGame)  =>  chess.Board
        func simply gets the current state of the chess board from
        the PychessGame object. _state is wrapping the chess.Board
        object. the reason for implementing this function and not
        just allowing outside modules to access the local attribute
        of the game class is to make sure the correct state is
        being passed around.
        """
        self._wprint("getting state")
        return self._state


    def get_prev_move(self):
        """ public func
        @spec  get_prev_move(PychessGame)  =>  chess.Move
        func looks in the move history list of the information
        dictionary local to the game object and returns the last
        added move. if there is no move it returns an empty string.
        the returned values of this function have to be handled 
        as it might return if there is not move made yet ...
        """
        self._wprint("getting previous move")
        if len(self._info['move-history']) < 1:
            self._wprint("no previous move found")
            return ""
        move = self._info['move-history'][-1]
        self._wprint("returning previous move {}".format(move.uci()))
        return move


    def make_move(self, move):
        """ public func
        @spec  make_move(PychessGame, str)  =>  bool
        func takes a move as a formatted string and tries to
        push it to the move stack, contained in self._state which is 
        a chess.Board type object. this is basically a wrapper function
        for _push_move and thus returns the save bool value. true if 
        pushing the move was legal/successfull or false if not.
        """
        if type(move) == chess.Move:
            self._wprint("making move {}".format(move.uci()))
            return self._push_move(move)

        if len(move) != 4:
            self._eprint("got faulty move input from user")
            return False
        
        for char in move:
            if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖijklmnopqrstuvwxyzåäö90/,;.:-_'*¨^~`´\\?+=})]([/{&%€¤$#£\"@!§½":
                self._eprint("got faulty move input from user")
                return False
        
        move = chess.Move.from_uci(move)
        self._wprint("making move {}".format(move.uci()))
        return self._push_move(move)


    def is_terminal(self):
        """ public func
        @spec  is_terminal(PychessGame)  =>  bool
        func looks at the current state of the board and determines 
        whether or not the game is terminated, i.e. there is an outcome.
        _state.outcome() yields None if the game is still going, otherwise
        it returns a chess.Outcome object.
        """
        if self.get_info('time-white') <= 0:
            self._wprint("game is terminal, black won on time")
            self._info['winner'] = 'black wins!'
            return True
        if self.get_info('time-black') <= 0:
            self._wprint("game is terminal, white won on time")
            self._info['winner'] = 'white wins!'
            return True

        outcome = self._state.outcome()
        if outcome is None:
            return False
        resdict = {'1-0': 'white wins!', '0-1': 'black wins!', '1/2-1/2': 'draw!'}
        self._info['winner'] = resdict[outcome.result()]
        self._wprint("game is terminal, either checkmate or draw/stalemate")
        return True



class TestPychessGame(unittest.TestCase):
    """!!! definition for unittest class TestPychessGame
    used as module for testing funcs in above class.
    implemented using std lib unittest and running by
    invoking this module through unittest.main()
    this module is invoked whenever running this .py file
    as main. relative imports are handled above using 
    try except clauses.
    """
    def __init__(self, *args, **kwargs):
        super(TestPychessGame, self). __init__(*args, **kwargs)
        self._verbose = True
        self._pg = PychessGame(2, white='uysses', black='beq', verbose=False)


    def __str__(self):
        return "TestPychessGame"


    def test_set_info(self):
        self.assertFalse(self._pg._set_info('bingbong', 2))
        self.assertTrue(self._pg._set_info('ai', False))


    def test_legal_moves(self):
        self.assertEqual(type(self._pg._legal_moves()), list)
        self.assertTrue(len(self._pg._legal_moves()), 20)


    def test_push_move(self):
        self.assertFalse(self._pg._push_move(chess.Move.from_uci('a3b6')))
        self.assertTrue(self._pg._push_move(chess.Move.from_uci('e2e4')))


if __name__ == "__main__":
    unittest.main()


'''
Author : Ethan Reinhart
Date Due : 5 / 9 / 2022
Project : Sodoku Solver
'''
from sdk_config import CHOICES, UNKNOWN, ROOT
from sdk_config import NROWS, NCOLS
import logging
from typing import Sequence, List, Set
import enum
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#log.setLevel(logging.INFO)

class Event(object):
    """Abstract base class of all events, both for MVC
    and for other purposes.
    """
    pass

class EventKind(enum.Enum):
    TileChanged = 1
    TileGuessed = 2

class Listener(object):
    """Abstract base class for listeners.
    Subclass this to make the notification do
    something useful.
    """

    def __init__(self):
        """Default constructor for simple listeners without state"""
        pass

    def notify(self, event: Event):
        """The 'notify' method of the base class must be
        overridden in concrete classes.
        """
        raise NotImplementedError("You must override Listener.notify")

class TileEvent(Event):
    """Abstract base class for things that happen
    to tiles. We always indicate the tile.  Concrete
    subclasses indicate the nature of the event.
    """

    def __init__(self, tile: 'Tile', kind: EventKind):
        self.tile = tile
        self.kind = kind
        # Note 'Tile' type is a forward reference;
        # Tile class is defined below

    def __str__(self):
        """Printed representation includes name of concrete subclass"""
        return f"{repr(self.tile)}"

class TileListener(Listener):
    def notify(self, event: TileEvent):
        raise NotImplementedError(
            "TileListener subclass needs to override notify(TileEvent)")

class Listenable:
    """Objects to which listeners (like a view component) can be attached"""

    def __init__(self):
        self.listeners = [ ]

    def add_listener(self, listener: Listener):
        self.listeners.append(listener)

    def notify_all(self, event: Event):
        for listener in self.listeners:
            listener.notify(event)

class Tile(Listenable):
    """One tile on the Sudoku grid.
    Public attributes (read-only): value, which will be either
    UNKNOWN or an element of CHOICES; candidates, which will
    be a set drawn from CHOICES.  If value is an element of
    CHOICES,then candidates will be the singleton containing
    value.  If candidates is empty, then no tile value can
    be consistent with other tile values in the grid.
    value is a public read-only attribute; change it
    only through the access method set_value or indirectly
    through method remove_candidates.
    """
    def __init__(self, row: int, col: int, value=UNKNOWN):
        super().__init__()
        assert value == UNKNOWN or value in CHOICES
        self.row = row
        self.col = col
        self.set_value(value)

    def __hash__(self) -> int:
        """Hash on position only (not value)"""
        return hash((self.row, self.col))

    def set_value(self, value: str):
        '''Accepts a value and sets that value of the tile to that value'''
        if value in CHOICES:
            self.value = value
            self.candidates = {value}
        else:
            self.value = UNKNOWN
            self.candidates = set(CHOICES)
        self.notify_all(TileEvent(self, EventKind.TileChanged))

    def __str__(self):
        '''Returns the value of the tile for the string method'''
        return self.value

    def __repr__(self):
        '''Returns a representation of how to declare a tile'''
        return f"Tile({self.row}, {self.col}, '{str(self.value)}')"

    def could_be(self, value: str) -> bool:
        """True iff value is a candidate value for this tile"""
        return value in self.candidates

    def remove_candidates(self, used_values: Set[str]) -> bool:
        """The used values cannot be a value of this unknown tile.
        We remove those possibilities from the list of candidates.
        If there is exactly one candidate left, we set the
        value of the tile.
        Returns:  True means we eliminated at least one candidate,
        False means nothing changed (none of the 'used_values' was
        in our candidates set).
        """
        new_candidates = self.candidates.difference(used_values)
        if new_candidates == self.candidates:
            # Didn't remove any candidates
            return False
        self.candidates = new_candidates
        if len(self.candidates) == 1:
            self.set_value(new_candidates.pop())
        self.notify_all(TileEvent(self, EventKind.TileChanged))
        return True

class Board(object):
    """A board has a matrix of tiles"""

    def __init__(self):
        """The empty board
        Initializes cells and groups and can create different sized boards based on the value of ROOT"""
        # Row/Column structure: Each row contains columns
        self.tiles: List[List[Tile]] = [ ]
        self.groups = []
        for row in range(NROWS):
            cols = [ ]
            for col in range(NCOLS):
                cols.append(Tile(row, col))
            self.tiles.append(cols)
        for row in self.tiles:
            self.groups.append(row)
        for index in range(len(self.tiles)):
            column = []
            for row in self.tiles:
                column.append(row[index])
            self.groups.append(column)
        for block_row in range(ROOT):
            for block_col in range(ROOT):
                group = [ ]
                for row in range(ROOT):
                    for col in range(ROOT):
                        row_addr = (ROOT * block_row) + row
                        col_addr = (ROOT * block_col) + col
                        group.append(self.tiles[row_addr][col_addr])
                self.groups.append(group)

    def __str__(self) -> str:
        """In Sadman Sudoku format"""
        return "\n".join(self.as_list())


    def as_list(self) -> List[str]:
        """Tile values in a format compatible with
        set_tiles.
        """
        row_syms = [ ]
        for row in self.tiles:
            values = [tile.value for tile in row]
            row_syms.append("".join(values))
        return row_syms

    def set_tiles(self, tile_values: Sequence[Sequence[str]] ):
        """Set the tile values a list of lists or a list of strings"""
        for row_num in range(NROWS):
            for col_num in range(NCOLS):
                tile = self.tiles[row_num][col_num]
                tile.set_value(tile_values[row_num][col_num])

    def is_consistent(self) -> bool:
        '''Determines if the board is consistent with sudoku standards (values only occur once in each group)'''
        for group in self.groups:
            used = []
            for tile in group:
                if tile.value in CHOICES:
                    if tile.value in used:
                        return False
                    else:
                        used.append(tile.value)
        return True

    def naked_single(self) -> bool:
        """Eliminate candidates and check for sole remaining possibilities.
        Return value True means we crossed off at least one candidate.
        Return value False means we made no progress.
        """
        truth = False
        for group in self.groups:
            numset = set([])
            for tile in group:
                if tile.value in CHOICES:
                    numset.add(tile.value)
            for tile in group:
                if tile.value == UNKNOWN:
                    if tile.remove_candidates(numset):
                        truth = True
        return truth

    def hidden_single(self) -> bool:
        """Eliminate candidates and check for sole remaining possibilities.
        Return value True means we crossed off at least one candidate.
        Return value False means we made no progress.
        """
        truth = False
        for group in self.groups:
            leftovers = set(CHOICES)
            for tile in group:
                if tile.value in CHOICES:
                    leftovers.discard(tile.value)
            for val in leftovers:
                tiles = []
                for tile in group:
                    if val in tile.candidates:
                        tiles.append(tile)
                if len(tiles) == 1:
                    truth = True
                    tiles[0].set_value(val)
        return truth

    def propagate(self):
        """Repeat solution tactics until we
        don't make any progress, whether or not
        the board is solved.
        """
        progress = True
        while progress:
            progress = self.naked_single()
            self.hidden_single()
        return

    def solve(self):
        """General solver; guess-and-check
        combined with constraint propagation.
        """
        self.propagate()
        if self.is_complete() and self.is_consistent():
            return True
        if self.is_consistent() is False:
            return False
        else:
            new_tiles = self.as_list()
            tile = self.min_choice_tile()
            for val in tile.candidates:
                tile.set_value(val)
                if self.solve():
                    return True
                else:
                    self.set_tiles(new_tiles)
            return False


    def min_choice_tile(self) -> Tile:
        """Returns a tile with value UNKNOWN and
        minimum number of candidates.
        Precondition: There is at least one tile
        with value UNKNOWN.
        """
        ftruth = False
        for row in self.tiles:
            val_list = []
            for tile in row:
                val_list.append(tile.value)
            truth = UNKNOWN in val_list
            if truth:
                ftruth = True
        if ftruth:
            length = float('inf')
            min_tile = None
            for row in self.tiles:
                for tile in row:
                    if tile.value == UNKNOWN:
                        if len(tile.candidates) < length:
                            length = len(tile.candidates)
                            min_tile = tile
            return min_tile

    def is_complete(self) -> bool:
        """None of the tiles are UNKNOWN.
        Note: Does not check consistency; do that
        separately with is_consistent.
        """
        for row in self.tiles:
            for tile in row:
                if tile.value == UNKNOWN:
                    return False
        return True

import logging
log = logging.getLogger(__name__)

from atom.api import Atom, Bool, Enum, Int, List, Typed
import numpy as np
import pandas as pd

from . import electrode_coords as coords


class ElectrodeSelector(Atom):

    #: Coordinates to plot electrodes at.
    coords = Typed(pd.DataFrame)

    #: List of extra electrodes not shown in coords.
    extra = List()

    reference = List()
    selected = List()
    select_mode = Enum('multi', 'single')

    def toggle_reference(self, ch):
        reference = self.reference.copy()
        if ch in reference:
            reference.remove(ch)
        else:
            reference.append(ch)
        self.reference = reference

    def toggle_selected(self, ch):
        if self.select_mode == 'single':
            self.selected = [ch]
        else:
            # multi mode
            selected = self.selected[:]
            if ch in selected:
                selected.remove(ch)
            else:
                selected.append(ch)
            self.selected = selected


class BiosemiElectrodeSelector(ElectrodeSelector):

    n_channels = Int(32)
    include_exg = Bool(True)

    def _observe_n_channels(self, event):
        self.coords = self._default_coords()

    def _observe_include_exg(self, event):
        self.coords = self._default_coords()

    def _default_coords(self):
        return coords.load_normalized_coords(self.n_channels, self.include_exg)

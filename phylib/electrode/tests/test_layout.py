# -*- coding: utf-8 -*-

"""Test MEA."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import numpy as np

from phylib.utils.geometry import staggered_positions
from ..layout import probe_layout


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------

def test_probe_layout():
    positions = staggered_positions(32)
    channel_ids = {0: np.arange(1, 11, 2),
                   1: np.arange(7, 15, 2)}

    layout = probe_layout(positions, channel_ids)
    assert '<circle' in layout

#!/usr/bin/env python

'''
test_mrsdimcontrol.py - Tests methods of MRSDimControl class in controls.py

Authors: Vasilis Karlaftis    <vasilis.karlaftis@ndcn.ox.ac.uk>

Elements taken from fsleyes/fsleyes/tests/controls/test_controls.py by Paul McCarthy <pauldmccarthy@gmail.com>
         
Copyright (C) 2025 University of Oxford
'''

import os.path as op
from pathlib import Path
import fsl.data.image as fslimage
from tests import run_with_viewpanel, realYield

from fsleyes_plugin_mrs.controls    import MRSDimControl
from fsleyes_plugin_mrs.views       import MRSView

datadir = Path(__file__).parent / 'testdata' / 'svs'

# Test #1: check if the title matches the expected value
def test_title():
    assert isinstance(MRSDimControl.title(), str)
    assert MRSDimControl.title() == "MRS Dimension control"

# Test #2: check if supportedViews include the MRSView
def test_supportedViews():
    assert isinstance(MRSDimControl.supportedViews(), list)
    assert MRSView in MRSDimControl.supportedViews()

# Test #3: check MRSDimControl basic functionality on a single metabolite file
def test_toggle():
    run_with_viewpanel(_test_toggle, MRSView)

def _test_toggle(view, overlayList, displayCtx):

    img = fslimage.Image(op.join(datadir, 'metab'))
    overlayList.append(img)
    realYield(25)

    # toggle the panel off and on
    view.togglePanel(MRSDimControl)
    realYield(25)

    view.togglePanel(MRSDimControl)
    realYield(25)

from __future__ import print_function
from pyNastran.utils.log import get_logger

def add_dummy_gui_functions(test, debug=True):
    def removeOldGeometry(self):
        pass
    def cycleResults(self):
        pass
    def TurnTextOn():
        pass
    def TurnTextOff():
        pass
    def update_axes_length(value):
        pass
    def passer():
        pass
    def passer2(a, b):
        pass
    def log_info(msg):
        if debug:
            print('INFO:  ', msg)

    def log_error(msg):
        if debug:
            print('ERROR:  ', msg)

    class Grid(object):
        def Reset(self):
            pass
        def Allocate(self, nelements, delta):
            pass
        def InsertNextCell(self, *cell):
            pass
        def SetPoints(self, *cell):
            pass
        def Modified(self):
            pass
        def Update(self):
            pass

    class ScalarBar(object):
        def VisibilityOff(self):
            pass
        def VisibilityOn(self):
            pass
        def Modified(self):
            pass

    test._finish_results_io2 = passer2

    test.grid = Grid()
    test.grid2 = Grid()
    test.scalarBar = ScalarBar()
    test.log = get_logger(log=None, level='debug')
    test.log_error = log_error
    #test.log_info = print
    test.log_info = log_info
    test.removeOldGeometry = removeOldGeometry
    test.cycleResults = cycleResults
    test.TurnTextOn = TurnTextOn
    test.TurnTextOff = TurnTextOff
    test.update_axes_length = update_axes_length
    test.cycleResults_explicit = passer


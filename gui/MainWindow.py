import PySide2.QtGui
import gui.LivePlotter
import gui.GlobalVariables
from logic.TradeGlobals import GloVar


class Main(PySide2.QtGui.QWidget):

    def __init__(self, parent=None):

        PySide2.QtGui.QWidget.__init__(self, parent)

        self.layout = PySide2.QtGui.QHBoxLayout(self)

        self.layout.addWidget(gui.GlobalVariables.GlobalVariables(self), 1)

        _w = gui.LivePlotter.TraidingWidget(self)
        self.layout.addWidget(_w, 4)

        self.setLayout(self.layout)

        GloVar.emit_all()
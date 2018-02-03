import PySide.QtGui
import gui.LivePlotter
import gui.GlobalVariables
from logic.TradeGlobals import GloVar


class Main(PySide.QtGui.QWidget):

    def __init__(self,
                 parent=None,
                 simulation=True,
                 update_rate_trade_data=10,
                 update_rate_plotting=10,
                 update_rate_save_data=100):

        PySide.QtGui.QWidget.__init__(self, parent)

        self.layout = PySide.QtGui.QHBoxLayout(self)

        self.layout.addWidget(gui.GlobalVariables.GlobalVariables(self), 1)

        _w = gui.LivePlotter.TraidingWidget(self, simulation, update_rate_trade_data, update_rate_plotting, update_rate_save_data)
        self.layout.addWidget(_w, 4)

        self.setLayout(self.layout)

        GloVar.emit_all()